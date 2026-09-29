<?php
 switch($_GET['ruta']){
 		case "entidades":
    	echo '
      	["clientes","productos","ventas","rrhh"]
      ';
      break;
    case "tabla":
    	echo '
      	["clientes","productos","ventas","rrhh"]
      ';
      break;
 }
?>