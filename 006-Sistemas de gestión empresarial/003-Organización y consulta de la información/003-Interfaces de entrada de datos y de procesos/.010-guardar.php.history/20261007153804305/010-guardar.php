<?php

header("Content-Type: application/json");

// Recibo el JSON
$json = file_get_contents("php://input");
$datos = json_decode($json, true);

// Conecto a SQLite
$db = new PDO("sqlite:empresa.db");
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Quito id por seguridad, si viniera
unset($datos["id"]);

// Obtengo dinámicamente los nombres de los campos
$campos = array_keys($datos);

// Creo los interrogantes ?, ?, ?, ...
$interrogantes = array_fill(0, count($campos), "?");

// Construyo la consulta
$sql = "
    INSERT INTO clientes
    (" . implode(",", $campos) . ")
    VALUES
    (" . implode(",", $interrogantes) . ")
";

// Preparo
$consulta = $db->prepare($sql);

// Ejecuto pasando los valores
$consulta->execute(array_values($datos));

// Devuelvo respuesta
echo json_encode([
    "ok" => true,
    "id" => $db->lastInsertId()
]);

?>