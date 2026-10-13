<?php
	echo "Hola que tal soy tu instalador";
	echo "<br>";
	echo $_POST['modelo'];
	echo "<br>";
	echo "Vamos a destripar";
	echo "<br>";

	// Creamos/abrimos la base de datos
	$db = new SQLite3('../data/darkorange.db');

	$partido = explode("\n",$_POST['modelo']);

	$tabla = "";
	$columnas = [];

	foreach($partido as $clave){

		$clave = trim($clave);

		if($clave == ""){
			continue;
		}

		if($clave[0] == "-"){
			$columna = trim(substr($clave,1));
			$columnas[] = $columna;
		}else{

			// Si ya teníamos una tabla, la creamos
			if($tabla != ""){
				$sql = "CREATE TABLE IF NOT EXISTS ".$tabla." (";
				$sql .= "id INTEGER PRIMARY KEY AUTOINCREMENT";

				if(count($columnas) > 0){
					$sql .= ", ";
					$sql .= implode(" TEXT, ",$columnas)." TEXT";
				}

				$sql .= ");";

				echo "<pre>".$sql."</pre>";

				$db->exec($sql);
			}

			// Empezamos una nueva tabla
			$tabla = $clave;
			$columnas = [];
		}
	}

	// Creamos la última tabla
	if($tabla != ""){
		$sql = "CREATE TABLE IF NOT EXISTS ".$tabla." (";
		$sql .= "id INTEGER PRIMARY KEY AUTOINCREMENT";

		if(count($columnas) > 0){
			$sql .= ", ";
			$sql .= implode(" TEXT, ",$columnas)." TEXT";
		}

		$sql .= ");";

		echo "<pre>".$sql."</pre>";

		$db->exec($sql);
	}

	$db->close();

	echo "<br>";
	echo "Base de datos creada correctamente";
	echo "<br>";
	echo "../data/darkorange.db";
?>