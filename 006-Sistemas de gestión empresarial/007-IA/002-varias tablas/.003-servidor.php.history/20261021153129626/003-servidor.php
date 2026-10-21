
<?php

header("Content-Type: application/json; charset=utf-8");

// ==========================================
// CONFIGURACIÓN
// ==========================================

$archivoBD = __DIR__ . "/empresa.db";
$ollamaURL = "http://localhost:11434/api/generate";
$modelo = "granite4.1:8b";

// ==========================================
// FUNCIÓN PARA DEVOLVER JSON
// ==========================================

function responder($datos, $codigo = 200) {
    http_response_code($codigo);

    echo json_encode(
        $datos,
        JSON_UNESCAPED_UNICODE |
        JSON_INVALID_UTF8_SUBSTITUTE
    );

    exit;
}

// ==========================================
// 1. RECIBIR PREGUNTA
// ==========================================

$pregunta = trim($_POST["pregunta"] ?? "");

if ($pregunta === "") {
    responder([
        "error" => "La pregunta está vacía"
    ], 400);
}

// ==========================================
// 2. ESQUEMA DE LA BASE DE DATOS EXISTENTE
// ==========================================

// Este texto NO crea ninguna tabla.
// Solo informa a Ollama de su estructura.

$schema = <<<SQL
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    ciudad TEXT,
    fecha_registro TEXT
);

CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    modelo TEXT NOT NULL,
    categoria TEXT,
    precio REAL NOT NULL,
    potencia INTEGER,
    autonomia INTEGER,
    stock INTEGER DEFAULT 0
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    precio_venta REAL NOT NULL,
    estado TEXT DEFAULT 'Pendiente',
    FOREIGN KEY (cliente_id)
        REFERENCES clientes(id),
    FOREIGN KEY (producto_id)
        REFERENCES productos(id)
);
SQL;

// ==========================================
// 3. CONSTRUIR PROMPT
// ==========================================

$prompt = <<<PROMPT
Eres un experto en consultas SQL para SQLite.

Tu tarea es convertir preguntas en lenguaje natural
en consultas SQL válidas.

Pregunta del usuario:

$pregunta

Estructura de la base de datos:

$schema

REGLAS OBLIGATORIAS:

1. Devuelve exclusivamente código SQL.
2. No incluyas explicaciones.
3. No incluyas markdown.
4. No incluyas bloques de código.
5. Genera únicamente consultas SELECT.
6. Utiliza exclusivamente la tabla clientes.
7. Utiliza exclusivamente las columnas existentes.
8. La consulta debe ser compatible con SQLite.
9. No inventes columnas ni tablas.
10. No generes operaciones de modificación.
11. Si preguntan por cantidades, utiliza COUNT().
12. Si preguntan por agrupaciones, utiliza GROUP BY.
13. Si preguntan por promedios, utiliza AVG().
14. Si preguntan por ordenaciones, utiliza ORDER BY.
15.-Si las tablas involucradas tienen Foreign Keys, sigue las claves para no mostrar claves sino la información asociada
16.-Recupera el contenido de las Foreign Keys. No muestres id de clave. Muestra los datos asociados.

Devuelve únicamente la consulta SQL.
PROMPT;

// ==========================================
// 4. CONSULTAR A OLLAMA
// ==========================================

$datosOllama = [
    "model" => $modelo,
    "prompt" => $prompt,
    "stream" => false,
    "options" => [
        "temperature" => 0
    ]
];

$curl = curl_init($ollamaURL);

curl_setopt_array($curl, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => json_encode($datosOllama),
    CURLOPT_HTTPHEADER => [
        "Content-Type: application/json"
    ],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_CONNECTTIMEOUT => 10,
    CURLOPT_TIMEOUT => 180
]);

$respuesta = curl_exec($curl);

$errorCurl = curl_error($curl);
$codigoHTTP = curl_getinfo(
    $curl,
    CURLINFO_HTTP_CODE
);

curl_close($curl);

if ($respuesta === false || $codigoHTTP !== 200) {
    responder([
        "error" => "No se pudo conectar con Ollama",
        "detalle" => $errorCurl ?: "HTTP $codigoHTTP"
    ], 502);
}

// ==========================================
// 5. RECUPERAR RESPUESTA DE OLLAMA
// ==========================================

$datosRespuesta = json_decode($respuesta, true);

if (
    !is_array($datosRespuesta) ||
    !isset($datosRespuesta["response"])
) {
    responder([
        "error" => "Respuesta inválida de Ollama"
    ], 502);
}

$sql = trim($datosRespuesta["response"]);

// Eliminar posibles fences Markdown
$sql = preg_replace(
    '/^```(?:sql)?\s*/i',
    '',
    $sql
);

$sql = preg_replace(
    '/\s*```$/',
    '',
    $sql
);

$sql = trim($sql);

// ==========================================
// 6. VALIDAR CONSULTA SQL
// ==========================================

// Comprobación básica de formato.
// No sustituye a un analizador SQL completo.

if (!preg_match('/^SELECT\s/i', $sql)) {
    responder([
        "error" => "Ollama no generó una consulta SELECT",
        "sql" => $sql
    ], 400);
}

// Rechazar comentarios y múltiples sentencias
if (
    str_contains($sql, '--') ||
    str_contains($sql, '/*') ||
    str_contains($sql, '*/')
) {
    responder([
        "error" => "No se permiten comentarios SQL",
        "sql" => $sql
    ], 400);
}

$sqlSinFinal = preg_replace('/;\s*$/', '', $sql);

if (str_contains($sqlSinFinal, ';')) {
    responder([
        "error" => "No se permiten múltiples consultas",
        "sql" => $sql
    ], 400);
}

// Rechazar instrucciones peligrosas
if (preg_match(
    '/\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA|REPLACE|VACUUM|REINDEX)\b/i',
    $sql
)) {
    responder([
        "error" => "La consulta contiene instrucciones no permitidas",
        "sql" => $sql
    ], 400);
}

// ==========================================
// 7. COMPROBAR BASE DE DATOS EXISTENTE
// ==========================================

if (!is_file($archivoBD)) {
    responder([
        "error" => "No existe la base de datos clientes.db"
    ], 500);
}

if (!is_readable($archivoBD)) {
    responder([
        "error" => "No hay permisos para leer clientes.db"
    ], 500);
}

// ==========================================
// 8. CONECTAR Y CONSULTAR SQLITE
// ==========================================

$conexion = null;

try {

    // Abrir exclusivamente en modo lectura
    $conexion = new SQLite3(
        $archivoBD,
        SQLITE3_OPEN_READONLY
    );

    $conexion->enableExceptions(true);
    $conexion->busyTimeout(5000);

    // Impedir escrituras desde esta conexión
    $conexion->exec("PRAGMA query_only = ON");

    // Desactivar extensiones cargables
    if (method_exists($conexion, "enableLoadExtension")) {
        $conexion->enableLoadExtension(false);
    }

    // Autorizar exclusivamente SELECT
    // mediante una única sentencia preparada.
    $sentencia = $conexion->prepare($sql);

    if ($sentencia === false) {
        throw new Exception("No se pudo preparar la consulta");
    }

    if (!$sentencia->readOnly()) {
        throw new Exception(
            "La consulta no es de solo lectura"
        );
    }

    $resultado = $sentencia->execute();

    if ($resultado === false) {
        throw new Exception(
            "No se pudo ejecutar la consulta"
        );
    }

    // ======================================
    // 9. RECUPERAR RESULTADOS
    // ======================================

    $registros = [];
    $limite = 1000;

    while (
        count($registros) < $limite &&
        ($fila = $resultado->fetchArray(SQLITE3_ASSOC))
    ) {
        $registros[] = $fila;
    }

    $resultado->finalize();
    $sentencia->close();
    $conexion->close();
    $conexion = null;

    // ======================================
    // 10. DEVOLVER JSON AL NAVEGADOR
    // ======================================

    responder([
        "pregunta" => $pregunta,
        "sql" => $sql,
        "total" => count($registros),
        "resultados" => $registros
    ]);

} catch (Throwable $e) {

    if ($conexion !== null) {
        $conexion->close();
    }

    responder([
        "error" => "Error ejecutando la consulta SQLite",
        "detalle" => $e->getMessage(),
        "sql" => $sql
    ], 500);
}

?>
