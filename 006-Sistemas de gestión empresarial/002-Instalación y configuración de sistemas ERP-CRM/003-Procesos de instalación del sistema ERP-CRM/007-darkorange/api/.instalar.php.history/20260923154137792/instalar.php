<?php
	echo "Hola que tal soy tu instalador";
  echo "<br>";
  echo $_POST['modelo'];
  echo "<br>";
  echo "Vamos a destripar";
  echo "<br>";
  $partido = explode("\n",$_POST['modelo']);
  foreach($partido as $clave){
  	echo $clave;
    if($clave[0] == "-"){
    	echo " esto es una columna";
    }else{
    	echo " esto no es una columna";
    }
    echo "<br>";
  }	
?>