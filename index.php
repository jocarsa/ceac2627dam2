<?php
declare(strict_types=1);

/*
 * JOCARSA | CURRÍCULO ↔ PROYECTOS
 *
 * - Real directory tree
 * - Maximum 3 directory levels
 * - SQLite project persistence
 * - Legacy Markdown migration
 * - Permanent directory/project mapping
 * - AJAX inline editing
 */

$folderRoot = __DIR__;
$mdFile = __DIR__ . '/proyectos.md';
$dbFile = __DIR__ . '/proyectos.sqlite';

// Maximum number of directory levels to index.
$maxDepth = 3;

/* =========================================================
   UTILITIES
   ========================================================= */

function h($value): string {
    return htmlspecialchars(
        (string)$value,
        ENT_QUOTES | ENT_SUBSTITUTE,
        'UTF-8'
    );
}

function normalizedFolderName(string $name): string {
    $name = preg_replace(
        '/^\s*\d+\s*[-._) ]+\s*/u',
        '',
        $name
    );

    $name = mb_strtolower(trim($name), 'UTF-8');

    $ascii = iconv(
        'UTF-8',
        'ASCII//TRANSLIT//IGNORE',
        $name
    );

    if ($ascii !== false) {
        $name = strtolower($ascii);
    }

    return trim(
        preg_replace('/[^a-z0-9]+/i', ' ', $name)
    );
}

function nodeKey(array $path): string {
    return hash('sha256', implode(' > ', $path));
}

function normalizedPath(array $path): string {
    return implode(
        '/',
        array_map('normalizedFolderName', $path)
    );
}

function colorData(
    float $start,
    float $size,
    int $i,
    int $count
): array {
    $slice = $size / max(1, $count);
    $s = $start + $i * $slice;
    $h = fmod($s + $slice / 2 + 360, 360);

    return [$s, $slice, $h];
}

/* =========================================================
   DATABASE
   ========================================================= */

$db = new PDO('sqlite:' . $dbFile);

$db->setAttribute(
    PDO::ATTR_ERRMODE,
    PDO::ERRMODE_EXCEPTION
);

$db->exec("
    CREATE TABLE IF NOT EXISTS proyectos (
        node_key TEXT PRIMARY KEY,
        titulo TEXT NOT NULL DEFAULT '',
        descripcion TEXT NOT NULL DEFAULT '',
        estado TEXT NOT NULL DEFAULT 'pendiente',
        actualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
");

$db->exec("
    CREATE TABLE IF NOT EXISTS carpetas_proyectos (
        ruta TEXT PRIMARY KEY,
        node_key TEXT NOT NULL,
        actualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
");

$db->exec("
    CREATE INDEX IF NOT EXISTS idx_carpetas_node_key
    ON carpetas_proyectos(node_key)
");

/* =========================================================
   LEGACY MARKDOWN MIGRATION
   ========================================================= */

function parseMarkdownTree(string $file): array {
    if (!is_file($file) || !is_readable($file)) {
        return [];
    }

    $lines = file($file, FILE_IGNORE_NEW_LINES);

    $root = [
        'title' => 'ROOT',
        'children' => []
    ];

    $stack = [];
    $stack[] = &$root;

    foreach ($lines as $line) {
        if (!preg_match(
            '/^(\s*)-\s*(.+?)\s*$/u',
            $line,
            $m
        )) {
            continue;
        }

        $spaces = strlen(
            str_replace("\t", '    ', $m[1])
        );

        $level = intdiv($spaces, 4);
        $title = trim($m[2]);

        if ($title === '') {
            continue;
        }

        $node = [
            'title' => $title,
            'children' => []
        ];

        while (count($stack) > $level + 1) {
            array_pop($stack);
        }

        $parent = &$stack[count($stack) - 1];
        $parent['children'][] = $node;

        $idx = count($parent['children']) - 1;
        $stack[] = &$parent['children'][$idx];

        unset($parent);
    }

    return $root['children'];
}

function indexMarkdownTree(
    array $nodes,
    array $path = [],
    array &$index = []
): array {
    foreach ($nodes as $node) {
        $current = [...$path, $node['title']];
        $lookup = normalizedPath($current);

        if (!isset($index[$lookup])) {
            $index[$lookup] = nodeKey($current);
        }

        indexMarkdownTree(
            $node['children'],
            $current,
            $index
        );
    }

    return $index;
}

/* =========================================================
   REAL DIRECTORY TREE — MAXIMUM 3 LEVELS
   ========================================================= */

function readFolderTree(
    string $directory,
    int $depth = 0,
    int $maxDepth = 3
): array {

    /*
     * depth = 0 -> read level 1
     * depth = 1 -> read level 2
     * depth = 2 -> read level 3
     * depth = 3 -> STOP
     */

    if ($depth >= $maxDepth) {
        return [];
    }

    $excluded = [
        '.git',
        '.svn',
        '.idea',
        '.vscode',
        'node_modules',
        'vendor',
        '__pycache__',
        'venv',
        '.venv',
        'dist',
        'build'
    ];

    if (!is_dir($directory) || !is_readable($directory)) {
        return [];
    }

    $folders = [];

    foreach (new DirectoryIterator($directory) as $entry) {
        if (
            $entry->isDot() ||
            !$entry->isDir() ||
            $entry->isLink()
        ) {
            continue;
        }

        $name = $entry->getFilename();

        if (
            in_array($name, $excluded, true) ||
            str_starts_with($name, '.')
        ) {
            continue;
        }

        $folders[] = [
            'title' => $name,
            'children' => readFolderTree(
                $entry->getPathname(),
                $depth + 1,
                $maxDepth
            )
        ];
    }

    usort(
        $folders,
        fn($a, $b) => strnatcasecmp(
            $a['title'],
            $b['title']
        )
    );

    return $folders;
}

/* =========================================================
   PERMANENT DIRECTORY / PROJECT MAPPINGS
   ========================================================= */

function loadFolderMappings(PDO $db): array {
    $mappings = [];

    foreach (
        $db->query(
            "SELECT ruta, node_key FROM carpetas_proyectos"
        ) as $row
    ) {
        $mappings[$row['ruta']] = $row['node_key'];
    }

    return $mappings;
}

function assignFolderKeys(
    array $nodes,
    array $path,
    array $markdownIndex,
    array &$mappings,
    PDO $db
): array {
    $result = [];

    $insert = $db->prepare("
        INSERT INTO carpetas_proyectos
            (ruta, node_key, actualizado)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(ruta) DO NOTHING
    ");

    foreach ($nodes as $node) {
        $current = [...$path, $node['title']];

        $relativePath = implode('/', $current);
        $lookup = normalizedPath($current);

        /*
         * Priority:
         * 1. Existing SQLite mapping
         * 2. Matching Markdown entry
         * 3. New folder key
         */

        $key = $mappings[$relativePath]
            ?? $markdownIndex[$lookup]
            ?? nodeKey($current);

        if (!isset($mappings[$relativePath])) {
            $insert->execute([
                $relativePath,
                $key
            ]);

            $mappings[$relativePath] = $key;
        }

        $node['key'] = $key;

        $node['children'] = assignFolderKeys(
            $node['children'],
            $current,
            $markdownIndex,
            $mappings,
            $db
        );

        $result[] = $node;
    }

    return $result;
}

/* =========================================================
   FOLDER URL
   ========================================================= */

function folderInfo(array $path): ?array {
    global $folderRoot;

    $directory = $folderRoot;

    foreach ($path as $segment) {
        $directory .= DIRECTORY_SEPARATOR . $segment;

        if (!is_dir($directory)) {
            return null;
        }
    }

    return [
        'url' => './' . implode(
            '/',
            array_map('rawurlencode', $path)
        ) . '/',
        'name' => end($path)
    ];
}

/* =========================================================
   LOAD TREE AND MIGRATE
   ========================================================= */

$folderTree = readFolderTree(
    $folderRoot,
    0,
    $maxDepth
);

$markdownTree = parseMarkdownTree($mdFile);
$markdownIndex = indexMarkdownTree($markdownTree);

$mappings = loadFolderMappings($db);

$db->beginTransaction();

try {
    $tree = assignFolderKeys(
        $folderTree,
        [],
        $markdownIndex,
        $mappings,
        $db
    );

    $db->commit();

} catch (Throwable $e) {
    $db->rollBack();
    throw $e;
}

/* =========================================================
   AJAX PROJECT SAVING
   ========================================================= */

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $key = trim((string)($_POST['node_key'] ?? ''));
    $title = trim((string)($_POST['titulo'] ?? ''));
    $description = trim(
        (string)($_POST['descripcion'] ?? '')
    );
    $status = (string)($_POST['estado'] ?? 'pendiente');

    header('Content-Type: application/json; charset=utf-8');

    if (!preg_match('/^[a-f0-9]{64}$/', $key)) {
        http_response_code(400);

        echo json_encode([
            'ok' => false,
            'error' => 'Clave no válida'
        ]);

        exit;
    }

    /*
     * Verify that the key belongs to an indexed directory,
     * not merely an old mapping from a deeper level.
     */
    $activeKeys = [];

    $collectKeys = function (array $nodes) use (&$collectKeys, &$activeKeys): void {
        foreach ($nodes as $node) {
            $activeKeys[$node['key']] = true;
            $collectKeys($node['children']);
        }
    };

    $collectKeys($tree);

    if (!isset($activeKeys[$key])) {
        http_response_code(404);

        echo json_encode([
            'ok' => false,
            'error' => 'Proyecto no encontrado entre los niveles indexados'
        ]);

        exit;
    }

    $st = $db->prepare("
        INSERT INTO proyectos
            (
                node_key,
                titulo,
                descripcion,
                estado,
                actualizado
            )
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(node_key)
        DO UPDATE SET
            titulo = excluded.titulo,
            descripcion = excluded.descripcion,
            estado = excluded.estado,
            actualizado = CURRENT_TIMESTAMP
    ");

    $st->execute([
        $key,
        $title,
        $description,
        $status
    ]);

    if (($_POST['ajax'] ?? '') === '1') {
        echo json_encode(['ok' => true]);
        exit;
    }

    header('Location: ' . $_SERVER['PHP_SELF']);
    exit;
}

/* =========================================================
   LOAD PROJECTS
   ========================================================= */

$projects = [];

foreach (
    $db->query("SELECT * FROM proyectos") as $row
) {
    $projects[$row['node_key']] = $row;
}

/* =========================================================
   RENDER
   ========================================================= */

function renderRows(
    array $nodes,
    array $path,
    array $projects,
    float $start = 0,
    float $size = 360,
    int $depth = 0
): void {
    $count = count($nodes);

    foreach ($nodes as $i => $node) {
        [$s, $slice, $hue] = colorData(
            $start,
            $size,
            $i,
            $count
        );

        $currentPath = [...$path, $node['title']];
        $key = $node['key'];

        $folderLink = folderInfo($currentPath);
        $project = $projects[$key] ?? null;

        $hasChildren = count($node['children']) > 0;

        $sat = max(42, 64 - $depth * 3);
        $light = min(92, 78 + $depth * 3);

        $search = mb_strtolower(
            implode(' ', $currentPath) . ' ' .
            ($project['titulo'] ?? '') . ' ' .
            ($project['descripcion'] ?? ''),
            'UTF-8'
        );
        ?>

        <section
            class="pair-node depth-<?= $depth ?>"
            data-key="<?= h($key) ?>"
            data-level="<?= $depth ?>"
            data-search="<?= h($search) ?>"
            style="
                --hue:<?= $hue ?>;
                --sat:<?= $sat ?>%;
                --light:<?= $light ?>%;
                --depth:<?= $depth ?>
            "
        >

            <div class="pair-row">

                <div class="curriculum-cell">

                    <button
                        class="toggle <?= $hasChildren ? '' : 'empty' ?>"
                        type="button"
                    ><?= $hasChildren ? '▾' : '•' ?></button>

                    <div class="cell-copy">

                        <span class="level-label">
                            NIVEL <?= $depth + 1 ?>
                        </span>

                        <?php if ($folderLink): ?>

                            <a
                                class="folder-link"
                                href="<?= h($folderLink['url']) ?>"
                                title="Abrir carpeta: <?= h($folderLink['name']) ?>"
                            ><?= h($folderLink['name']) ?></a>

                        <?php else: ?>

                            <strong>
                                <?= h($node['title']) ?>
                            </strong>

                        <?php endif; ?>

                    </div>

                </div>

                <div class="project-cell">

                    <input
                        class="inline-project-title"
                        type="text"
                        data-key="<?= h($key) ?>"
                        value="<?= h($project['titulo'] ?? '') ?>"
                        placeholder="Escribe el proyecto…"
                        aria-label="Proyecto para <?= h($node['title']) ?>"
                    >

                    <span
                        class="save-state"
                        aria-live="polite"
                    ></span>

                </div>

            </div>

            <?php if ($hasChildren): ?>

                <div class="pair-children">

                    <?php
                    renderRows(
                        $node['children'],
                        $currentPath,
                        $projects,
                        $s,
                        $slice,
                        $depth + 1
                    );
                    ?>

                </div>

            <?php endif; ?>

        </section>

        <?php
    }
}
?>

<!doctype html>
<html lang="es">

<head>
    <meta charset="utf-8">

    <meta
        name="viewport"
        content="width=device-width,initial-scale=1"
    >

    <title>Mapa curricular y proyectos</title>

    <link rel="stylesheet" href="style.css">

    <style>
        .cell-copy .folder-link,
        .cell-copy .folder-link:link,
        .cell-copy .folder-link:visited,
        .cell-copy .folder-link:hover,
        .cell-copy .folder-link:active {
            color: inherit !important;
            font: inherit !important;
            font-weight: 700 !important;
            text-decoration: none !important;
            border: 0 !important;
            background: transparent !important;
        }

        .pair-row > .curriculum-cell {
            border-radius: 999px 0 0 999px !important;
        }

        .pair-row > .project-cell {
            border-radius: 0 999px 999px 0 !important;
        }

        .pair-node {
            border-radius: 32px;
        }

        .pair-node > .pair-row {
            border-radius: 999px;
        }
    </style>
</head>

<body>

<header class="topbar">

    <div>
        <span class="kicker">
            JOCARSA · MAPA CURRICULAR
        </span>

        <h1>Currículo ↔ Proyectos</h1>
    </div>

    <div class="toolbar">

        <input
            id="search"
            type="search"
            placeholder="Buscar carpeta o proyecto…"
        >

        <button id="expand" type="button">
            Expandir
        </button>

        <button id="collapse" type="button">
            Contraer
        </button>

    </div>

</header>

<div class="column-heads">
    <div>
        CARPETAS · SUBCARPETAS · CONTENIDOS
    </div>

    <div>
        PROYECTOS ASOCIADOS
    </div>
</div>

<main id="map">
    <?php renderRows($tree, [], $projects); ?>
</main>

<script src="app.js"></script>

</body>
</html>

