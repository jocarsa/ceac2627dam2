<?php

require_once "comun.php";

$f = abrir_cola();
flock($f,LOCK_EX);

escribir_json_bloqueado($f,[]);

flock($f,LOCK_UN);
fclose($f);

responder([
    "ok"=>true,
    "mensaje"=>"Cola reiniciada"
]);

?>