<?php

  require_once "Formularios.php";

  $json = file_get_contents("formulario.json");

  $formulario = new Formularios($json);

  echo $formulario->generar();

?>
