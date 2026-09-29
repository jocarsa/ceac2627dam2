El ERP que estamos diseñando se puede adaptar a cualquier negocio de una forma muy sencilla: cuenta con un instalador en el cual, cualquier usuario sin conocimientos de programación puede introducir un modelo de datos: ese modelo se convierte automáticamente a la base de datos

Muchos sistemas de gestión tienen una base de datos con tablas prefijadas. En nuestro caso hemos realizado un instalador que muestra al usuario una primera pantalla donde puede introducir su modelo.

El modelo tiene una forma como esta:
clientes
-nombre
-apellidos
-email
-telefono

Una vez que el modelo se envía, el programa parsea el texto y lo convierte a una base de datos SQLite. Estamos usando SQLite como prototipo en un futuro lo convertiremos a MySQL.

Para ello el instalador tiene dos parte, una que procesa el texto:
foreach($partido as $clave){
Y otra que crea las tablas adecuadamente:
if($tabla != ""){
	$sql = "CREATE TABLE IF NOT EXISTS ".$tabla." (";
	$sql .= "id INTEGER PRIMARY KEY AUTOINCREMENT";

	if(count($columnas) > 0){
		$sql .= ", ";
		$sql .= implode(" TEXT, ",$columnas)." TEXT";
	}
	
En el video que se adjunta podemos ver el proceso completo de instalación de un ERP desde cero en el cual definimos un modelo de datos inicial y vemos cómo se convierte en una aplicación en funcionamiento.

Esto nos sirve para tener un sistema completamente personalizable que podamos instalar a cualquier cliente en minutos.

