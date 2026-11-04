
<?php

$url = "https://www.aemet.es/xml/municipios/localidad_46250.xml";

// Descargar XML mediante cURL
$curl = curl_init($url);

curl_setopt_array($curl, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_TIMEOUT => 15,
    CURLOPT_USERAGENT => "Mozilla/5.0"
]);

$xmlTexto = curl_exec($curl);
$codigoHTTP = curl_getinfo($curl, CURLINFO_HTTP_CODE);

if ($xmlTexto === false || $codigoHTTP !== 200) {
    die("Error al descargar el XML");
}

curl_close($curl);

// Convertir XML en objeto PHP
libxml_use_internal_errors(true);

$xml = simplexml_load_string($xmlTexto);

if ($xml === false) {
    die("Error al interpretar el XML");
}

// Mostrar nombre del municipio
echo "<h1>" . htmlspecialchars((string)$xml->nombre) . "</h1>";

// Mostrar todo el contenido
echo "<pre>";
print_r($xml);
echo "</pre>";

?>
