<?php
header('Content-Type: application/json; charset=utf-8');

$archivo = 'cola.json';
$ip = $_SERVER['REMOTE_ADDR'] ?? 'desconocida';
$ua = $_SERVER['HTTP_USER_AGENT'] ?? 'desconocido';
$esclavo = $ip . '|' . substr(sha1($ua), 0, 10);

if (!file_exists($archivo)) {
    http_response_code(409);
    echo json_encode(['estado'=>'sin_cola']);
    exit;
}

$f = fopen($archivo, 'c+');
flock($f, LOCK_EX);
rewind($f);
$contenido = stream_get_contents($f);
$cola = $contenido ? json_decode($contenido, true) : [];

$trabajo = null;
foreach ($cola as &$paquete) {
    if ($paquete['estado'] === 'pendiente') {
        $paquete['estado'] = 'asignado';
        $paquete['esclavo'] = $esclavo;
        $paquete['asignado_en'] = date('c');
        $trabajo = ['id'=>$paquete['id'], 'datos'=>$paquete['datos']];
        break;
    }
}
unset($paquete);

if ($trabajo !== null) {
    rewind($f);
    ftruncate($f, 0);
    fwrite($f, json_encode($cola, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    fflush($f);
}
flock($f, LOCK_UN);
fclose($f);

echo json_encode($trabajo ?? ['estado'=>'sin_trabajo']);
