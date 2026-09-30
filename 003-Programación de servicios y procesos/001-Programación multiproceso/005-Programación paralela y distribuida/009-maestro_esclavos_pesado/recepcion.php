<?php

require_once "comun.php";

$entrada = json_decode(
    file_get_contents("php://input"),
    true
);

$id = intval($entrada["id"] ?? 0);
$esclavo = trim($entrada["esclavo"] ?? "");
$resultado = $entrada["resultado"] ?? null;
$segundos = floatval($entrada["segundos"] ?? 0);

if($id <= 0 || $esclavo === "" || !is_array($resultado)){
    responder([
        "ok"=>false,
        "error"=>"Resultado inválido"
    ]);
}

$f = abrir_cola();
flock($f,LOCK_EX);

$paquetes = leer_json_bloqueado($f);

$encontrado = false;
$error = null;

foreach($paquetes as &$paquete){

    if(intval($paquete["id"]) !== $id){
        continue;
    }

    $encontrado = true;

    /*
       Solo aceptamos el resultado del esclavo al que
       se asignó originalmente este paquete.
    */

    if(($paquete["esclavo"] ?? "") !== $esclavo){
        $error = "Este paquete pertenece a otro esclavo";
        break;
    }

    if(($paquete["estado"] ?? "") === "terminado"){
        $error = "El paquete ya estaba terminado";
        break;
    }

    if(($paquete["estado"] ?? "") !== "asignado"){
        $error = "El paquete no está asignado";
        break;
    }

    $paquete["estado"] = "terminado";
    $paquete["resultado"] = $resultado;
    $paquete["segundos"] = $segundos;
    $paquete["terminado_en"] = date("c");

    /*
       Ya no necesitamos conservar los datos dentro de
       la cola una vez terminado el paquete.
    */
    $paquete["datos"] = [];

    break;
}

unset($paquete);

if($error === null && $encontrado){
    escribir_json_bloqueado($f,$paquetes);
}

flock($f,LOCK_UN);
fclose($f);

if(!$encontrado){
    responder([
        "ok"=>false,
        "error"=>"Paquete inexistente"
    ]);
}

if($error !== null){
    responder([
        "ok"=>false,
        "error"=>$error
    ]);
}

responder([
    "ok"=>true,
    "id"=>$id
]);

?>