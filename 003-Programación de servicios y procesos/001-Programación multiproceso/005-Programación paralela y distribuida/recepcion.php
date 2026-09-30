<?php

// 1. Obtengo la IP
$ip = $_SERVER['REMOTE_ADDR'];

// 2. Obtengo el User Agent
$user_agent = $_SERVER['HTTP_USER_AGENT'] ?? 'Desconocido';

// 3. Obtengo el valor enviado por fetch
$valor = json_decode(file_get_contents("php://input"));

// 4. Abro el CSV en modo append
$archivo = fopen("datos.csv", "a");

// 5. Añado una nueva fila: IP, User Agent, Valor
fputcsv($archivo, [$ip, $user_agent, $valor]);

// 6. Cierro el archivo
fclose($archivo);

echo "OK";

?>