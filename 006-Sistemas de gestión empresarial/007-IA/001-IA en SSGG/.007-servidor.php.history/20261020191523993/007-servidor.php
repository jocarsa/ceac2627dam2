
<?php

header("Content-Type: application/json; charset=utf-8");

$pregunta = trim($_POST["pregunta"] ?? "");

if ($pregunta === "") {
    http_response_code(400);
    echo json_encode(["error" => "Pregunta vacía"]);
    exit;
}

$schema = <<<SQL
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    apellidos TEXT,
    email TEXT,
    telefono TEXT,
    direccion TEXT,
    ciudad TEXT,
    provincia TEXT,
    codigo_postal TEXT,
    fecha_nacimiento TEXT,
    fecha_registro TEXT,
    activo INTEGER DEFAULT 1
);
SQL;

$prompt = "
Eres un experto en SQLite.

Genera una consulta SQL para responder esta pregunta:

$pregunta

Solo quiero el código SQL.
No me des explicaciones, markdown ni fences.
Utiliza exclusivamente las tablas y columnas disponibles.

El schema de la base de datos es:

$schema
";

$datos = [
    "model" => "granite4.1:8b",
    "prompt" => $prompt,
    "stream" => false,
    "options" => [
        "temperature" => 0
    ]
];

$curl = curl_init("http://localhost:11434/api/generate");

curl_setopt_array($curl, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => json_encode($datos),
    CURLOPT_HTTPHEADER => [
        "Content-Type: application/json"
    ],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 180
]);

$respuesta = curl_exec($curl);
$error = curl_error($curl);
$estado = curl_getinfo($curl, CURLINFO_HTTP_CODE);

curl_close($curl);

if ($respuesta === false || $estado !== 200) {
    http_response_code(502);
    echo json_encode([
        "error" => "Error comunicando con Ollama",
        "detalle" => $error ?: "HTTP $estado"
    ]);
    exit;
}

$resultado = json_decode($respuesta, true);

if (!isset($resultado["response"])) {
    http_response_code(502);
    echo json_encode(["error" => "Respuesta inválida de Ollama"]);
    exit;
}

echo json_encode([
    "sql" => trim($resultado["response"])
], JSON_UNESCAPED_UNICODE);

?>
