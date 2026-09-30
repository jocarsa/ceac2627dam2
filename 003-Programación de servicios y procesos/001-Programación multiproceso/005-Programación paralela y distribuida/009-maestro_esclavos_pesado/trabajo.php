<?php

require_once "comun.php";

$entrada = json_decode(
    file_get_contents("php://input"),
    true
);

$esclavo = trim(
    $entrada["esclavo"] ?? ""
);

if($esclavo === ""){
    responder([
        "trabajo"=>false,
        "mensaje"=>"Falta identificador de esclavo"
    ]);
}

if(!file_exists(COLA)){
    responder([
        "trabajo"=>false,
        "mensaje"=>"El maestro todavía no ha preparado trabajo."
    ]);
}

$ip = $_SERVER["REMOTE_ADDR"] ?? "desconocida";
$userAgent = $_SERVER["HTTP_USER_AGENT"] ?? "desconocido";

$f = abrir_cola();

/*
    Esta es la parte crítica.

    Mientras un PHP está buscando y reservando un paquete,
    ningún otro proceso puede modificar cola.json.
*/
flock($f,LOCK_EX);

$paquetes = leer_json_bloqueado($f);
$seleccionado = null;

foreach($paquetes as &$paquete){

    if(($paquete["estado"] ?? "") === "pendiente"){

        $paquete["estado"] = "asignado";
        $paquete["esclavo"] = $esclavo;
        $paquete["ip"] = $ip;
        $paquete["user_agent"] = $userAgent;
        $paquete["asignado_en"] = date("c");

        $seleccionado = [
            "trabajo"=>true,
            "id"=>$paquete["id"],
            "iteraciones"=>$paquete["iteraciones"],
            "datos"=>$paquete["datos"]
        ];

        break;
    }
}

unset($paquete);

if($seleccionado !== null){
    escribir_json_bloqueado($f,$paquetes);
}

flock($f,LOCK_UN);
fclose($f);

if($seleccionado === null){

    $hayAsignados = false;

    foreach($paquetes as $paquete){
        if(($paquete["estado"] ?? "") === "asignado"){
            $hayAsignados = true;
            break;
        }
    }

    responder([
        "trabajo"=>false,
        "mensaje"=>$hayAsignados
            ? "No quedan paquetes libres; otros esclavos están trabajando."
            : "Todos los paquetes han terminado."
    ]);
}

responder($seleccionado);

?>