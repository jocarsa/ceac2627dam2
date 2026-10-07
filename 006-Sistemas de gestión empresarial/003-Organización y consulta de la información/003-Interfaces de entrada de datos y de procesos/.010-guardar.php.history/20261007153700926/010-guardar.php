<?php

header("Content-Type: application/json");

// 1. Recoger el JSON enviado por JavaScript
$json = file_get_contents("php://input");

// 2. Convertir JSON en array PHP
$datos = json_decode($json, true);

// 3. Conectar con SQLite
$db = new PDO("sqlite:datos.db");

// 4. Preparar INSERT
$sql = "
    INSERT INTO personas
    (nombre, apellidos, email)
    VALUES
    (:nombre, :apellidos, :email)
";

$consulta = $db->prepare($sql);

// 5. Ejecutar
$consulta->execute([
    ":nombre" => $datos["nombre"],
    ":apellidos" => $datos["apellidos"],
    ":email" => $datos["email"]
]);

// 6. Responder al JavaScript
echo json_encode([
    "ok" => true,
    "mensaje" => "Registro guardado correctamente",
    "id" => $db->lastInsertId()
]);

?>