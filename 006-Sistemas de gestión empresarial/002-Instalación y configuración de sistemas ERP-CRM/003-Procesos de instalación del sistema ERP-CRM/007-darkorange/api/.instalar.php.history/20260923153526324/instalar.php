<?php
	echo "Hola que tal soy tu instalador";
  echo "<br>";
  echo $_POST['modelo'];
  echo "<br>";
  echo "Vamos a destripar";
  echo "<br>";
  $partido = explode("\n"$_POST['modelo']);
?>