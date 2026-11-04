<?php

$curl = curl_init("http://localhost/ceac2627dam2/003-Programaci%C3%B3n%20de%20servicios%20y%20procesos/003-Programaci%C3%B3n%20de%20comunicaciones%20en%20red/006-Enlazado%20y%20establecimiento%20de%20conexiones/004-servidor.php");

curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

$contenido = curl_exec($curl);

curl_close($curl);

echo $contenido;

?>