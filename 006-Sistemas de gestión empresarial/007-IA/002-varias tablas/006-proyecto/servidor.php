
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

// Las peticiones de facturación se interpretan con Ollama, pero se ejecutan
// mediante operaciones parametrizadas; nunca mediante SQL libre generado por IA.
if (preg_match('/\b(factura|facturas|facturar|facturaci[oó]n)\b/iu', $pregunta)) {
    $instrucciones = <<<'PROMPT'
Clasifica la solicitud de facturación. Devuelve SOLO un objeto JSON con:
"accion": "listar" | "crear" | "consultar" | "aclarar",
"pedido_id": entero o null,
"cliente_id": entero o null,
"producto_id": entero o null,
"precio": número o null,
"cliente_nombre": texto o null,
"producto_nombre": texto o null,
"factura_id": entero o null,
"mensaje": texto breve si faltan datos.
Si pide facturar un pedido existente, usa crear y pedido_id.
Si pide factura nueva sin pedido, exige cliente, producto y precio BASE sin IVA.
Si pide ver una factura existente, usa consultar y factura_id.
Si pide listado de facturas, usa listar.
No inventes identificadores, nombres ni importes. Ante ambigüedad usa aclarar.
PROMPT;
    $ch = curl_init($ollamaURL);
    curl_setopt_array($ch, [CURLOPT_POST=>true,CURLOPT_POSTFIELDS=>json_encode([
        'model'=>$modelo,'prompt'=>$instrucciones."\nSOLICITUD: ".$pregunta,
        'stream'=>false,'format'=>'json','options'=>['temperature'=>0]
    ],JSON_UNESCAPED_UNICODE),CURLOPT_HTTPHEADER=>['Content-Type: application/json'],
    CURLOPT_RETURNTRANSFER=>true,CURLOPT_CONNECTTIMEOUT=>10,CURLOPT_TIMEOUT=>180]);
    $raw=curl_exec($ch);$status=curl_getinfo($ch,CURLINFO_HTTP_CODE);curl_close($ch);
    if($raw===false || $status!==200) responder(['error'=>'No se pudo interpretar la petición de facturación'],502);
    $payload=json_decode($raw,true);
    $intencion=json_decode($payload['response']??'',true);
    if(!is_array($intencion)) responder(['error'=>'La IA no devolvió una intención válida'],422);
    $accion=$intencion['accion']??'aclarar';
    if($accion==='aclarar') responder(['error'=>$intencion['mensaje']??'Indica los datos de la factura.'],422);
    if($accion==='consultar') {
        $id=filter_var($intencion['factura_id']??null,FILTER_VALIDATE_INT);
        if(!$id) responder(['error'=>'Indica el ID de la factura que quieres abrir.'],422);
        responder(['tipo'=>'FACTURA','mensaje'=>'Factura disponible','numero'=>'#'.$id,'url'=>'factura.php?id='.$id]);
    }
    if(!in_array($accion,['listar','crear'],true)) responder(['error'=>'Operación de facturación no reconocida'],422);
    $_POST=['accion'=>$accion];
    if($accion==='crear') {
        foreach(['pedido_id','cliente_id','producto_id','precio'] as $clave)
            if(isset($intencion[$clave])) $_POST[$clave]=(string)$intencion[$clave];
        if(empty($_POST['pedido_id']) && (empty($_POST['cliente_id']) || empty($_POST['producto_id']))) {
            // Se admiten nombres únicamente si identifican un registro inequívoco.
            try {
                $db=new SQLite3($archivoBD,SQLITE3_OPEN_READONLY);
                foreach(['cliente'=>'clientes','producto'=>'productos'] as $campo=>$tabla) {
                    if(!empty($_POST[$campo.'_id'])) continue;
                    $nombre=trim((string)($intencion[$campo.'_nombre']??''));
                    if($nombre==='') continue;
                    $columna=$campo==='cliente'?'nombre || " " || apellidos':'nombre || " " || modelo';
                    $st=$db->prepare("SELECT id FROM $tabla WHERE lower($columna)=lower(:nombre) OR lower(nombre)=lower(:nombre) LIMIT 2");
                    $st->bindValue(':nombre',$nombre,SQLITE3_TEXT);
                    $r=$st->execute();$ids=[];while($fila=$r->fetchArray(SQLITE3_ASSOC))$ids[]=$fila['id'];
                    if(count($ids)===1) $_POST[$campo.'_id']=(string)$ids[0];
                }
                $db->close();
            } catch(Throwable $e) {responder(['error'=>'No se pudieron comprobar cliente y producto'],500);}
        }
        if(empty($_POST['pedido_id']) && (empty($_POST['cliente_id']) || empty($_POST['producto_id']) || !isset($_POST['precio'])))
            responder(['error'=>'Para crear la factura necesito cliente, producto y precio base sin IVA, o bien el ID de un pedido existente.'],422);
    }
    require __DIR__.'/facturacion.php';
    exit;
}

// ==========================================
// 2. ESQUEMA DE SQLITE
// ==========================================

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
Eres un experto en SQLite.

Convierte la petición del usuario en una única
consulta SQL válida para SQLite.

PETICIÓN:
$pregunta

ESQUEMA:
$schema

REGLAS:

1. Devuelve exclusivamente SQL.
2. No incluyas explicaciones ni markdown.
3. Genera una única sentencia.
4. Puedes generar SELECT o INSERT.
5. No generes UPDATE, DELETE, DROP ni ALTER.
6. Utiliza únicamente las tablas y columnas
   existentes en el esquema.
7. Para consultas de lectura utiliza SELECT.
8. Para crear registros utiliza INSERT INTO.
9. Si preguntan por cantidades utiliza COUNT().
10. Para agrupaciones utiliza GROUP BY.
11. Para promedios utiliza AVG().
12. Para ordenaciones utiliza ORDER BY.
13. En SELECT utiliza JOIN cuando sea necesario
    para recuperar datos relacionados.
14. En los resultados de SELECT muestra los datos
    descriptivos asociados a las claves foráneas
    en lugar de mostrar únicamente sus identificadores.
15. Para insertar pedidos, recupera los IDs
    relacionados mediante subconsultas cuando
    el usuario proporcione nombres en lugar de IDs.
16. No inventes información obligatoria que
    no haya proporcionado el usuario.
17. No generes múltiples sentencias.
18. No utilices RETURNING.

Devuelve exclusivamente SQL.
PROMPT;

// ==========================================
// 4. CONSULTAR OLLAMA
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
// 5. RECUPERAR SQL
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
// 6. VALIDAR SQL
// ==========================================

// Solo permitir SELECT e INSERT
if (!preg_match('/^(SELECT|INSERT\s+INTO)\s/i', $sql)) {
    responder([
        "error" => "Solo se permiten SELECT e INSERT",
        "sql" => $sql
    ], 400);
}

// Rechazar comentarios
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

// Evitar múltiples sentencias
$sqlSinFinal = preg_replace('/;\s*$/', '', $sql);

if (str_contains($sqlSinFinal, ';')) {
    responder([
        "error" => "No se permiten múltiples consultas",
        "sql" => $sql
    ], 400);
}

$sql = trim($sqlSinFinal);

// Rechazar instrucciones no permitidas
if (preg_match(
    '/\b(UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA|REPLACE|VACUUM|REINDEX|RETURNING)\b/i',
    $sql
)) {
    responder([
        "error" => "Instrucción SQL no permitida",
        "sql" => $sql
    ], 400);
}

$tipo = preg_match('/^SELECT\b/i', $sql)
    ? "SELECT"
    : "INSERT";

// ==========================================
// 7. COMPROBAR BASE DE DATOS
// ==========================================

if (!is_file($archivoBD)) {
    responder([
        "error" => "No existe empresa.db"
    ], 500);
}

if (!is_readable($archivoBD)) {
    responder([
        "error" => "No se puede leer empresa.db"
    ], 500);
}

if ($tipo === "INSERT" && !is_writable($archivoBD)) {
    responder([
        "error" => "No se puede escribir en empresa.db"
    ], 500);
}

// ==========================================
// 8. CONECTAR A SQLITE
// ==========================================

$conexion = null;

try {

    $conexion = new SQLite3(
        $archivoBD,
        $tipo === "SELECT"
            ? SQLITE3_OPEN_READONLY
            : SQLITE3_OPEN_READWRITE
    );

    $conexion->enableExceptions(true);
    $conexion->busyTimeout(5000);

    // Activar integridad referencial
    $conexion->exec("PRAGMA foreign_keys = ON");

    if ($tipo === "SELECT") {
        $conexion->exec("PRAGMA query_only = ON");
    }

    if (method_exists($conexion, "enableLoadExtension")) {
        $conexion->enableLoadExtension(false);
    }

    // Preparar sentencia
    $sentencia = $conexion->prepare($sql);

    if ($sentencia === false) {
        throw new Exception(
            "No se pudo preparar la consulta"
        );
    }

    // Comprobar tipo de operación
    if ($tipo === "SELECT" && !$sentencia->readOnly()) {
        throw new Exception(
            "La consulta SELECT no es de solo lectura"
        );
    }

    if ($tipo === "INSERT" && $sentencia->readOnly()) {
        throw new Exception(
            "Se esperaba una operación de escritura"
        );
    }

    // ======================================
    // 9. EJECUTAR SELECT O INSERT
    // ======================================

    if ($tipo === "SELECT") {

        $resultado = $sentencia->execute();

        if ($resultado === false) {
            throw new Exception(
                "Error ejecutando SELECT"
            );
        }

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

        responder([
            "tipo" => "SELECT",
            "pregunta" => $pregunta,
            "sql" => $sql,
            "total" => count($registros),
            "resultados" => $registros
        ]);

    } else {

        // INSERT

        $conexion->exec("BEGIN IMMEDIATE");

        try {

            $resultado = $sentencia->execute();

            if ($resultado === false) {
                throw new Exception(
                    "Error ejecutando INSERT"
                );
            }

            $resultado->finalize();

            $filasAfectadas = $conexion->changes();
            $ultimoID = $conexion->lastInsertRowID();

            $conexion->exec("COMMIT");

        } catch (Throwable $e) {

            $conexion->exec("ROLLBACK");
            throw $e;
        }

        $sentencia->close();
        $conexion->close();
        $conexion = null;

        responder([
            "tipo" => "INSERT",
            "pregunta" => $pregunta,
            "sql" => $sql,
            "mensaje" => "Operación ejecutada correctamente",
            "filas_afectadas" => $filasAfectadas,
            "ultimo_id" => $ultimoID,
            "total" => 0,
            "resultados" => []
        ]);
    }

} catch (Throwable $e) {

    if ($conexion !== null) {
        $conexion->close();
    }

    responder([
        "error" => "Error ejecutando SQL",
        "detalle" => $e->getMessage(),
        "sql" => $sql
    ], 500);
}

?>
