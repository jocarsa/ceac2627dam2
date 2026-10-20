<form method="POST" action="?">
	<label>Introduce el termino de busqueda</label>
	<input type="text" name="clave">
  <input type="submit">
</form>
<?php

// Conectar a SQLite
$conexion = new SQLite3("clientes.db");

// Ejecutar consulta
$resultado = $conexion->query("
	SELECT * FROM clientes
  WHERE nombre LIKE '%".$_POST['clave']."%'
  ");

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
