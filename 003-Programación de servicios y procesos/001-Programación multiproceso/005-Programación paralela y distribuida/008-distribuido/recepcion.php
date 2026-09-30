<?php
header('Content-Type: application/json; charset=utf-8');

$archivo = 'cola.json';
$entrada = json_decode(file_get_contents('php://input'), true);
if (!isset($entrada['id'], $entrada['frecuencias'])) {
    http_response_code(400);
    echo json_encode(['ok'=>false, 'error'=>'Resultado invalido']);
    exit;
}

$ip = $_SERVER['REMOTE_ADDR'] ?? 'desconocida';
$ua = $_SERVER['HTTP_USER_AGENT'] ?? 'desconocido';
$esclavo = $ip . '|' . substr(sha1($ua), 0, 10);

$f = fopen($archivo, 'c+');
flock($f, LOCK_EX);
rewind($f);
$cola = json_decode(stream_get_contents($f), true) ?: [];
$guardado = false;

foreach ($cola as &$paquete) {
    if ($paquete['id'] == $entrada['id'] &&
        $paquete['estado'] === 'asignado' &&
        $paquete['esclavo'] === $esclavo) {
        $paquete['estado'] = 'terminado';
        $paquete['resultado'] = $entrada['frecuencias'];
        $paquete['terminado_en'] = date('c');
        $guardado = true;
        break;
    }
}
unset($paquete);

if ($guardado) {
    rewind($f);
    ftruncate($f, 0);
    fwrite($f, json_encode($cola, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    fflush($f);
}
flock($f, LOCK_UN);
fclose($f);

if (!$guardado) http_response_code(409);
echo json_encode(['ok'=>$guardado]);
