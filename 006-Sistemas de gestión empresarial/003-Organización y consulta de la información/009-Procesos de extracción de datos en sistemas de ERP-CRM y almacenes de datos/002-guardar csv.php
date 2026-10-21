<?php
  $archivo = fopen("datos.csv",'w');
  fwrite($archivo,"uno,dos,tres,cuatro\n");
  fclose($archivo);
?>