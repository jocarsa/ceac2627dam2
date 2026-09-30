<?php

const COLA = __DIR__ . "/cola.json";
const CSV_DATOS = __DIR__ . "/euromillones.csv";

function responder($datos){
    header("Content-Type: application/json; charset=utf-8");
    echo json_encode(
        $datos,
        JSON_UNESCAPED_UNICODE |
        JSON_PRETTY_PRINT
    );
    exit;
}

function leer_json_bloqueado($archivo){
    rewind($archivo);
    $contenido = stream_get_contents($archivo);

    if(trim($contenido) === ""){
        return [];
    }

    $datos = json_decode($contenido,true);
    return is_array($datos) ? $datos : [];
}

function escribir_json_bloqueado($archivo,$datos){
    rewind($archivo);
    ftruncate($archivo,0);
    fwrite(
        $archivo,
        json_encode(
            $datos,
            JSON_UNESCAPED_UNICODE |
            JSON_PRETTY_PRINT
        )
    );
    fflush($archivo);
}

function abrir_cola(){
    $f = fopen(COLA,"c+");

    if(!$f){
        responder([
            "ok"=>false,
            "error"=>"No se puede abrir cola.json"
        ]);
    }

    return $f;
}

?>