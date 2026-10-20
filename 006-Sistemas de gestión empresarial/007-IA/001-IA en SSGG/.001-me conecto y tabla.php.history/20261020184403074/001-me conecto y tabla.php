<?php

// Conectar a SQLite
$conexion = new SQLite3("clientes.db");

// Ejecutar consulta
$resultado = $conexion->query("SELECT * FROM clientes");

// Recorrer los registros
while ($fila = $resultado->fetchArray(SQLITE3_ASSOC)) {
    echo "ID: " . $fila["id"] . "<br>";
    echo "Nombre: " . $fila["nombre"] . "<br>";
    echo "Email: " . $fila["email"] . "<br>";
    echo "<hr>";
}

// Cerrar conexión
$conexion->close();

?>
