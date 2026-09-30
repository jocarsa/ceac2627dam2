<?php

require_once "comun.php";

if(!file_exists(COLA)){
    responder([
        "total"=>0,
        "pendientes"=>0,
        "asignados"=>0,
        "terminados"=>0,
        "esclavos"=>0,
        "numero_mas_frecuente"=>null,
        "frecuencia_maxima"=>0,
        "paquetes"=>[]
    ]);
}

$f = abrir_cola();
flock($f,LOCK_SH);

$paquetes = leer_json_bloqueado($f);

flock($f,LOCK_UN);
fclose($f);

$pendientes = 0;
$asignados = 0;
$terminados = 0;

$esclavos = [];
$frecuencias = [];
$resumen = [];

foreach($paquetes as $paquete){

    $estado = $paquete["estado"] ?? "desconocido";

    if($estado === "pendiente") $pendientes++;
    if($estado === "asignado") $asignados++;
    if($estado === "terminado") $terminados++;

    if(!empty($paquete["esclavo"])){
        $esclavos[$paquete["esclavo"]] = true;
    }

    if(
        $estado === "terminado" &&
        isset($paquete["resultado"]["frecuencias"])
    ){
        foreach(
            $paquete["resultado"]["frecuencias"]
            as $numero=>$cantidad
        ){
            if(!isset($frecuencias[$numero])){
                $frecuencias[$numero] = 0;
            }

            $frecuencias[$numero] += intval($cantidad);
        }
    }

    $resumen[] = [
        "id"=>$paquete["id"],
        "estado"=>$estado,
        "esclavo"=>$paquete["esclavo"],
        "ip"=>$paquete["ip"],
        "segundos"=>$paquete["segundos"]
    ];
}

$numeroMasFrecuente = null;
$frecuenciaMaxima = 0;

foreach($frecuencias as $numero=>$cantidad){

    if($cantidad > $frecuenciaMaxima){
        $frecuenciaMaxima = $cantidad;
        $numeroMasFrecuente = intval($numero);
    }
}

responder([
    "total"=>count($paquetes),
    "pendientes"=>$pendientes,
    "asignados"=>$asignados,
    "terminados"=>$terminados,
    "esclavos"=>count($esclavos),
    "numero_mas_frecuente"=>$numeroMasFrecuente,
    "frecuencia_maxima"=>$frecuenciaMaxima,
    "frecuencias"=>$frecuencias,
    "paquetes"=>$resumen
]);

?>