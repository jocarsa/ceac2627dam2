<?php
	echo "Hola que tal soy tu instalador";
	echo "<br>";
	echo $_POST['modelo'];
	echo "<br>";
	echo "Vamos a destripar";
	echo "<br>";

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

			// Si ya teníamos una tabla, generamos su SQL
			if($tabla != ""){
				$sql = "CREATE TABLE ".$tabla." (";
				$sql .= "id INTEGER PRIMARY KEY AUTOINCREMENT, ";
				$sql .= implode(" TEXT, ",$columnas)." TEXT";
				$sql .= ");";

				echo "<pre>".$sql."</pre>";
			}

			// Nueva tabla
			$tabla = $clave;
			$columnas = [];
		}
	}

	// Crear la última tabla
	if($tabla != ""){
		$sql = "CREATE TABLE ".$tabla." (";
		$sql .= "id INTEGER PRIMARY KEY AUTOINCREMENT";

		if(count($columnas) > 0){
			$sql .= ", ";
			$sql .= implode(" TEXT, ",$columnas)." TEXT";
		}

		$sql .= ");";

		echo "<pre>".$sql."</pre>";
	}
?>