<?php

// 1. Obtengo la IP
$ip = $_SERVER['REMOTE_ADDR'];

// 2. Obtengo el valor enviado por fetch
$valor = json_decode(file_get_contents("php://input"));

// 3. Abro el CSV en modo append
$archivo = fopen("datos.csv", "a");

// 4. Añado una nueva fila
fputcsv($archivo, [$ip, $valor]);

// 5. Cierro el archivo
fclose($archivo);

echo "OK";

?>