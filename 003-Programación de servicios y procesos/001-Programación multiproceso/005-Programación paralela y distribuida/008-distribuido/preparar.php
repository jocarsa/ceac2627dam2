<?php
header('Content-Type: application/json; charset=utf-8');

$csv = 'euromillones.csv';
$cola = 'cola.json';
$tamano = isset($_GET['tamano']) ? max(1, intval($_GET['tamano'])) : 100;

$f = fopen($csv, 'r');
$cabeceras = fgetcsv($f);
$filas = [];
while (($fila = fgetcsv($f)) !== false) {
    $obj = array_combine($cabeceras, $fila);
    $filas[] = $obj;
}
fclose($f);

$paquetes = [];
foreach (array_chunk($filas, $tamano) as $i => $chunk) {
    $paquetes[] = [
        'id' => $i + 1,
        'estado' => 'pendiente',
        'esclavo' => null,
        'datos' => $chunk,
        'resultado' => null
    ];
}

file_put_contents($cola, json_encode($paquetes, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), LOCK_EX);
echo json_encode(['ok'=>true, 'filas'=>count($filas), 'paquetes'=>count($paquetes), 'tamano'=>$tamano]);
