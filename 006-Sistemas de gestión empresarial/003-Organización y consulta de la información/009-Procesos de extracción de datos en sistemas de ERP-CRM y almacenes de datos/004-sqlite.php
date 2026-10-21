<?php
$archivo = fopen("datos.csv",'w');
$db = new SQLite3("clientes.db");

$resultado = $db->query("SELECT * FROM clientes");
while ($fila = $resultado->fetchArray(SQLITE3_ASSOC)) {
    fwrite($archivo,$fila['nombre'].",".$fila['apellidos'].",".$fila['email']."\n");
}

fclose($archivo);
$db->close();
?>