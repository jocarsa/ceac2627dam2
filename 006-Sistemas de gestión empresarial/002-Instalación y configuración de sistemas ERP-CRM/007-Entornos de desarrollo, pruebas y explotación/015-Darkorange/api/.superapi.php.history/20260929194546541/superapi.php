<?php
 switch($_GET['ruta']){
 		case "modulos":
    	echo '
      	["ventas","rrhh","facturacion","compras"]
      ';
      break;
 		case "entidades":
    	// Me conecto a SQLite
    	$db = new SQLite3('../data/darkorange.db');
      // Pido el listado de tablas
			$result = $db->query("SELECT name 
                            FROM sqlite_master 
                            WHERE type='table';");
      // Creo un array de entidades
      $entidades = [];
      // Recorro el resultado
      while ($fila = $result->fetchArray(SQLITE3_ASSOC)) {
      	$entidades[] = $fila['name'];
      }
      // Y lo sacco por pantalla en formato json
      echo json_encode($entidades);
      $db->close();
      break;
    case "tabla":
    	$db = new SQLite3('../data/darkorange.db');
      $result = $db->query("SELECT * 
                            FROM clientes;");
      $registros = [];
      while ($fila = $result->fetchArray(SQLITE3_ASSOC)) {
      	$registros[] = $fila;
      }
      echo json_encode($registros);
      break;
 }
?>