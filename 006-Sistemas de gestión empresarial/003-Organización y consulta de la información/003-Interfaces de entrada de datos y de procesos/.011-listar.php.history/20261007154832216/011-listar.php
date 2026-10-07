<?php

header("Content-Type: application/json");

$db = new PDO("sqlite:empresa.db");

$db->setAttribute(
    PDO::ATTR_ERRMODE,
    PDO::ERRMODE_EXCEPTION
);

$consulta = $db->query("
    SELECT *
    FROM clientes
    ORDER BY id DESC
");

$filas = $consulta->fetchAll(
    PDO::FETCH_ASSOC
);

echo json_encode($filas);

?>