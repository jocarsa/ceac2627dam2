<?php
// Conectar a SQLite
$db = new SQLite3("basededatos.db");

// Ejecutar SELECT
$resultado = $db->query("SELECT * FROM clientes");

// Recorrer resultados con while
while ($fila = $resultado->fetchArray(SQLITE3_ASSOC)) {
    echo $fila["id"] . " - ";
    echo $fila["nombre"] . " ";
    echo $fila["apellidos"] . " - ";
    echo $fila["email"] . "<br>";
}

// Cerrar conexión
$db->close();
?>