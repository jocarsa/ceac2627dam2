<?php
header('Content-Type: application/json; charset=utf-8');
$db = new SQLite3('../data/darkorange.db');
$db->enableExceptions(true);

function entrada() {
    $datos = json_decode(file_get_contents('php://input'), true);
    return is_array($datos) ? $datos : [];
}
function nombreSeguro($nombre) {
    return '"' . str_replace('"', '""', $nombre) . '"';
}
function validarTabla($db, $tabla) {
    $stmt = $db->prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=? AND name NOT LIKE 'sqlite_%'");
    $stmt->bindValue(1, $tabla, SQLITE3_TEXT);
    $r = $stmt->execute()->fetchArray(SQLITE3_ASSOC);
    if (!$r) throw new Exception('Tabla no válida');
    return nombreSeguro($tabla);
}
function estructura($db, $tabla) {
    $segura = validarTabla($db, $tabla);
    $res = $db->query("PRAGMA table_info($segura)");
    $columnas = [];
    $pk = null;
    while ($c = $res->fetchArray(SQLITE3_ASSOC)) {
        $columnas[] = $c;
        if (!empty($c['pk'])) $pk = $c['name'];
    }
    return [$columnas, $pk];
}

try {
    $ruta = $_GET['ruta'] ?? '';
    switch ($ruta) {
        case 'modulos':
            echo json_encode(['ventas','rrhh','facturacion','compras'], JSON_UNESCAPED_UNICODE);
            break;

        case 'entidades':
            $r = $db->query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name");
            $tablas = [];
            while ($f = $r->fetchArray(SQLITE3_ASSOC)) $tablas[] = $f['name'];
            echo json_encode($tablas, JSON_UNESCAPED_UNICODE);
            break;

        case 'tabla':
            $tabla = $_GET['tabla'] ?? '';
            $segura = validarTabla($db, $tabla);
            [$columnas, $pk] = estructura($db, $tabla);
            $orden = $pk ? ' ORDER BY '.nombreSeguro($pk).' DESC' : '';
            $r = $db->query("SELECT * FROM $segura$orden");
            $registros = [];
            while ($f = $r->fetchArray(SQLITE3_ASSOC)) $registros[] = $f;
            echo json_encode([
                'tabla'=>$tabla,
                'columnas'=>$columnas,
                'clavePrimaria'=>$pk,
                'registros'=>$registros
            ], JSON_UNESCAPED_UNICODE);
            break;

        case 'crear':
            $e = entrada();
            $tabla = $e['tabla'] ?? '';
            $datos = $e['datos'] ?? [];
            $segura = validarTabla($db, $tabla);
            [$columnas, $pk] = estructura($db, $tabla);

            $permitidas = array_column(
                array_filter($columnas, fn($c) => empty($c['pk']) && $c['name'] !== 'id'),
                'name'
            );
            $datos = array_intersect_key($datos, array_flip($permitidas));
            if (!$datos) throw new Exception('No hay campos para insertar');

            $campos = array_keys($datos);
            $nombres = implode(',', array_map('nombreSeguro', $campos));
            $marcas = implode(',', array_fill(0, count($campos), '?'));
            $stmt = $db->prepare("INSERT INTO $segura ($nombres) VALUES ($marcas)");
            $i = 1;
            foreach ($datos as $valor) $stmt->bindValue($i++, $valor, SQLITE3_TEXT);
            $stmt->execute();

            echo json_encode(['ok'=>true,'id'=>$db->lastInsertRowID()], JSON_UNESCAPED_UNICODE);
            break;

        default:
            throw new Exception('Ruta no válida');
    }
} catch (Throwable $e) {
    http_response_code(400);
    echo json_encode(['ok'=>false,'error'=>$e->getMessage()], JSON_UNESCAPED_UNICODE);
}
$db->close();
?>