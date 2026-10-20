
<?php

header("Content-Type: application/json; charset=utf-8");

function responder($datos, $codigo = 200) {
    http_response_code($codigo);
    echo json_encode(
        $datos,
        JSON_UNESCAPED_UNICODE | JSON_INVALID_UTF8_SUBSTITUTE
    );
    exit;
}

// 1. Recibir pregunta

$pregunta = trim($_POST["pregunta"] ?? "");

if ($pregunta === "") {
    responder(["error" => "Pregunta vacía"], 400);
}

// 2. Definir esquema

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

// 3. Construir prompt

$prompt = "
Eres un experto en SQLite.

Genera una consulta SQL para responder esta pregunta:

$pregunta

REGLAS:
- Devuelve exclusivamente una consulta SELECT.
- No incluyas explicaciones.
- No incluyas markdown ni fences.
- No generes INSERT, UPDATE, DELETE, DROP ni ALTER.
- Utiliza exclusivamente las tablas y columnas disponibles.
- La consulta debe ser compatible con SQLite.

El schema de la base de datos es:

$schema
";

// 4. Preparar petición a Ollama

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
    responder([
        "error" => "Error comunicando con Ollama",
        "detalle" => $error ?: "HTTP $estado"
    ], 502);
}

// 5. Recuperar SQL generado

$resultado = json_decode($respuesta, true);

if (!isset($resultado["response"])) {
    responder([
        "error" => "Respuesta inválida de Ollama"
    ], 502);
}

$sql = trim($resultado["response"]);

// Eliminar posibles fences de markdown
$sql = preg_replace('/^```(?:sql)?\s*/i', '', $sql);
$sql = preg_replace('/\s*```$/', '', $sql);
$sql = trim($sql);

// 6. Validación básica del SQL

if (!preg_match('/^SELECT\s/i', $sql)) {
    responder([
        "error" => "La IA no generó una consulta SELECT",
        "sql" => $sql
    ], 400);
}

// Bloquear múltiples sentencias
$sqlSinFinal = preg_replace('/;\s*$/', '', $sql);

if (str_contains($sqlSinFinal, ';')) {
    responder([
        "error" => "No se permiten múltiples consultas",
        "sql" => $sql
    ], 400);
}

// 7. Conectar a SQLite en modo solo lectura

try {

    $conexion = new SQLite3(
        __DIR__ . "/clientes.db",
        SQLITE3_OPEN_READONLY
    );

    $conexion->enableExceptions(true);
    $conexion->busyTimeout(5000);

    // 8. Ejecutar consulta
    $resultadoSQL = $conexion->query($sql);

    // 9. Recuperar registros
    $registros = [];

    while (
        $fila = $resultadoSQL->fetchArray(SQLITE3_ASSOC)
    ) {
        $registros[] = $fila;
    }

    $resultadoSQL->finalize();
    $conexion->close();

    // 10. Devolver respuesta JSON
    responder([
        "pregunta" => $pregunta,
        "sql" => $sql,
        "total" => count($registros),
        "resultados" => $registros
    ]);

} catch (Throwable $e) {

    responder([
        "error" => "Error ejecutando consulta SQLite",
        "detalle" => $e->getMessage(),
        "sql" => $sql
    ], 500);

}

?>
