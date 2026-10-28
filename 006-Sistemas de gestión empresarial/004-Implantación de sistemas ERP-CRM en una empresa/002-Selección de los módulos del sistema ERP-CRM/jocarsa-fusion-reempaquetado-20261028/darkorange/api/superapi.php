<?php
header('Content-Type: application/json; charset=utf-8');
$universeRoot = realpath(__DIR__ . '/../../universo/data');
if (!$universeRoot) { http_response_code(503); exit(json_encode(['ok'=>false,'error'=>'No se encuentra universo/data'])); }
$meta = new PDO('sqlite:' . $universeRoot . '/application.sqlite');
$meta->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$projectId = $_GET['proyecto'] ?? '';
if ($projectId === '') $projectId = (string)$meta->query("SELECT value FROM preferences WHERE key='activeId'")->fetchColumn();
$stmtProject = $meta->prepare('SELECT id,name FROM projects WHERE id=?');
$stmtProject->execute([$projectId]);
$project = $stmtProject->fetch(PDO::FETCH_ASSOC);
if (!$project) $project = $meta->query('SELECT id,name FROM projects ORDER BY created_at LIMIT 1')->fetch(PDO::FETCH_ASSOC);
if (!$project) { http_response_code(404); exit(json_encode(['ok'=>false,'error'=>'No hay proyectos en Universo'])); }
$projectId = $project['id'];
$dbFile = $universeRoot . '/' . $project['name'] . '.sqlite';
if (!is_file($dbFile)) { http_response_code(404); exit(json_encode(['ok'=>false,'error'=>'No existe la base de datos del proyecto'])); }
$db = new SQLite3($dbFile);
$db->exec('PRAGMA foreign_keys=ON');
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
        case 'proyectos':
            echo json_encode($meta->query('SELECT id,name FROM projects ORDER BY name')->fetchAll(PDO::FETCH_ASSOC), JSON_UNESCAPED_UNICODE);
            break;
        case 'modulos':
            $q=$meta->prepare('SELECT title,categories_json FROM entities WHERE project_id=?');
            $q->execute([$projectId]);
            $groups=[];
            foreach($q->fetchAll(PDO::FETCH_ASSOC) as $e){
                foreach((json_decode($e['categories_json'],true) ?: []) as $cat){
                    $cat=trim((string)$cat);
                    if($cat!=='') $groups[$cat][]=$e['title'];
                }
            }
            echo json_encode($groups,JSON_UNESCAPED_UNICODE);
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

        case 'relaciones':
            $tabla=$_GET['tabla']??'';
            $q=$meta->prepare('SELECT id,title,properties_json FROM entities WHERE project_id=?');
            $q->execute([$projectId]);$entities=$q->fetchAll(PDO::FETCH_ASSOC);$byId=[];
            foreach($entities as $e) $byId[$e['id']]=$e;
            $q=$meta->prepare('SELECT * FROM links WHERE project_id=?');$q->execute([$projectId]);$rels=[];
            foreach($q->fetchAll(PDO::FETCH_ASSOC) as $l){
                if(!isset($byId[$l['to_id']],$byId[$l['from_id']]) || $byId[$l['to_id']]['title']!==$tabla) continue;
                $from=$byId[$l['from_id']];$to=$byId[$l['to_id']];
                $src=null;$dst=null;
                foreach(json_decode($from['properties_json'],true)?:[] as $c)if($c['id']===$l['from_prop'])$src=trim(explode(':',$c['text'])[0]);
                foreach(json_decode($to['properties_json'],true)?:[] as $c)if($c['id']===$l['to_prop'])$dst=trim(explode(':',$c['text'])[0]);
                if(!$src||!$dst)continue;
                $sql='SELECT '.nombreSeguro($src).' AS id,* FROM '.validarTabla($db,$from['title']).' LIMIT 1000';
                $res=$db->query($sql);$options=[];
                while($r=$res->fetchArray(SQLITE3_ASSOC)){
                    $label=$r['nombre']??$r['title']??$r['descripcion']??$r['id'];
                    $options[]=['value'=>$r['id'],'label'=>(string)$label.' (#'.$r['id'].')'];
                }
                $rels[$dst]=$options;
            }
            echo json_encode($rels,JSON_UNESCAPED_UNICODE);break;
        case 'crear':
            $e = entrada();
            $tabla = $e['tabla'] ?? '';
            $datos = $e['datos'] ?? [];
            $segura = validarTabla($db, $tabla);
            [$columnas, $pk] = estructura($db, $tabla);

            $permitidas = array_column(
                array_filter($columnas, fn($c) => empty($c['pk'])),
                'name'
            );
            $datos = array_intersect_key($datos, array_flip($permitidas));
            if (!$datos) throw new Exception('No hay campos para insertar');

            $campos = array_keys($datos);
            $nombres = implode(',', array_map('nombreSeguro', $campos));
            $marcas = implode(',', array_fill(0, count($campos), '?'));
            $stmt = $db->prepare("INSERT INTO $segura ($nombres) VALUES ($marcas)");
            $i = 1;
            foreach ($datos as $valor) $stmt->bindValue($i++, $valor === '' ? null : $valor, $valor === '' ? SQLITE3_NULL : SQLITE3_TEXT);
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
