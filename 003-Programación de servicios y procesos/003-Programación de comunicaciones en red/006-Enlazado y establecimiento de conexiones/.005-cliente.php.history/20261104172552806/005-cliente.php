<?php

$curl = curl_init("https://jocarsa.com/datos.php");

curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

$contenido = curl_exec($curl);

curl_close($curl);

echo $contenido;

?>