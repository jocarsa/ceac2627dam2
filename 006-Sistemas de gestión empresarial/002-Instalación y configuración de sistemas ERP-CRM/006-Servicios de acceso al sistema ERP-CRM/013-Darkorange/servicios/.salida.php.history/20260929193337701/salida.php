<?php
	$db = new SQLite3('../data/darkorange.db');
  $result = $db->query("SELECT name 
                            FROM sqlite_master 
                            WHERE type='table';");
                            // Creo un array de entidades
                            $entidades = [];
                            // Recorro el resultado
                            while ($fila = $result->fetchArray(SQLITE3_ASSOC)) {
                            $entidades[] = $fila;
                            }
  echo json_encode($entidades);
      
?>