<?php
$archivo = fopen("datos.csv",'w');
$db = new SQLite3("clientes.db");

$resultado = $db->query("SELECT * FROM clientes");


while ($fila = $resultado->fetchArray(SQLITE3_ASSOC)) {
    echo $fila["id"] . " - ";
    echo $fila["nombre"] . " ";
    echo $fila["apellidos"] . " - ";
    echo $fila["email"] . "<br>";
}


$db->close();
?>