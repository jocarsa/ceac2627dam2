<?php
declare(strict_types=1);
require_once __DIR__.'/../clases/Presentacion.php';
header('Content-Type: application/json; charset=utf-8');
try {
 $repo=new Repositorio();$vistas=new Presentacion($repo);$ruta=$_GET['ruta']??'dashboard';$tabla=(string)($_GET['tabla']??'');
 switch($ruta){
 case 'entidades':$resultado=$repo->entidades();break;
 case 'tabla':$resultado=['html'=>$vistas->tabla($tabla)];break;
 case 'formulario':$resultado=['html'=>$vistas->formulario($tabla)];break;
 case 'dashboard':$resultado=['html'=>$vistas->dashboard()];break;
 case 'reporting':$resultado=['html'=>$vistas->informe()];break;
 case 'guardar':
  if($_SERVER['REQUEST_METHOD']!=='POST')throw new RuntimeException('Se requiere POST');
  $id=$repo->insertar($tabla,$_POST,$_FILES);$resultado=['ok'=>true,'id'=>$id];break;
 default:throw new RuntimeException('Ruta desconocida');
 }
 echo json_encode($resultado,JSON_UNESCAPED_UNICODE|JSON_INVALID_UTF8_SUBSTITUTE|JSON_THROW_ON_ERROR);
} catch(Throwable $e){http_response_code(400);echo json_encode(['ok'=>false,'error'=>$e->getMessage()],JSON_UNESCAPED_UNICODE|JSON_INVALID_UTF8_SUBSTITUTE);}
