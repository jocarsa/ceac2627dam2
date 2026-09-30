<?php

require_once "comun.php";

$entrada = json_decode(
    file_get_contents("php://input"),
    true
);

$tamano = max(
    1,
    intval($entrada["tamano"] ?? 10)
);

$iteraciones = max(
    1000,
    intval($entrada["iteraciones"] ?? 50000000)
);

if(!file_exists(CSV_DATOS)){
    responder([
        "ok"=>false,
        "error"=>"No existe euromillones.csv"
    ]);
}

$archivo = fopen(CSV_DATOS,"r");

$cabeceras = fgetcsv($archivo);

$filas = [];

while(($valores = fgetcsv($archivo)) !== false){

    if(count($valores) < count($cabeceras)){
        continue;
    }

    $fila = [];

    foreach($cabeceras as $i=>$cabecera){
        $fila[trim($cabecera)] =
            isset($valores[$i])
            ? trim($valores[$i])
            : "";
    }

    $filas[] = $fila;
}

fclose($archivo);

$trozos = array_chunk($filas,$tamano);

$paquetes = [];

foreach($trozos as $i=>$trozo){

    $paquetes[] = [
        "id"=>$i+1,
        "estado"=>"pendiente",
        "esclavo"=>null,
        "ip"=>null,
        "user_agent"=>null,
        "asignado_en"=>null,
        "terminado_en"=>null,
        "segundos"=>null,
        "iteraciones"=>$iteraciones,
        "datos"=>$trozo,
        "resultado"=>null
    ];
}

$f = abrir_cola();
flock($f,LOCK_EX);

escribir_json_bloqueado($f,$paquetes);

flock($f,LOCK_UN);
fclose($f);

responder([
    "ok"=>true,
    "filas"=>count($filas),
    "tamano_paquete"=>$tamano,
    "paquetes"=>count($paquetes),
    "iteraciones_por_paquete"=>$iteraciones
]);

?>