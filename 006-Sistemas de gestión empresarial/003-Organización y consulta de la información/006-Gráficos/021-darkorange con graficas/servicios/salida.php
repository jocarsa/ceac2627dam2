<?php

$db = new SQLite3('../data/darkorange.db');

// Obtener todas las tablas
$result = $db->query("
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    AND name NOT LIKE 'sqlite_%'
    ORDER BY name
");

// Contenedor de toda la base de datos
$basededatos = [];

// Recorrer tablas
while ($fila = $result->fetchArray(SQLITE3_ASSOC)) {

    $tabla = $fila['name'];

    // Obtener todos los registros
    $resultadoTabla = $db->query(
        'SELECT * FROM "' . str_replace('"', '""', $tabla) . '"'
    );

    $registros = [];

    while ($registro = $resultadoTabla->fetchArray(SQLITE3_ASSOC)) {
        $registros[] = $registro;
    }

    // Guardar tabla y registros
    $basededatos[$tabla] = $registros;
}

// Devolver JSON
header('Content-Type: application/json; charset=utf-8');

echo json_encode(
    $basededatos,
    JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE
);

$db->close();

?>