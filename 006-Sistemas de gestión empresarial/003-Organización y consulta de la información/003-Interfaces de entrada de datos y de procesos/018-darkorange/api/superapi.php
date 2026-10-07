<?php
header('Content-Type: application/json; charset=utf-8');
$db = new SQLite3('../data/darkorange.db');
$db->enableExceptions(true);

function tablasPermitidas($db){
  $resultado=$db->query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'");
  $tablas=[]; while($fila=$resultado->fetchArray(SQLITE3_ASSOC)) $tablas[]=$fila['name'];
  return $tablas;
}
function validarTabla($db,$tabla){ if(!in_array($tabla,tablasPermitidas($db),true)) throw new Exception('Tabla no válida'); return '"'.str_replace('"','""',$tabla).'"'; }
function estructura($db,$tabla){
  $segura=validarTabla($db,$tabla); $r=$db->query("PRAGMA table_info($segura)"); $columnas=[]; $pk=null;
  while($f=$r->fetchArray(SQLITE3_ASSOC)){ $columnas[]=$f; if($f['pk']) $pk=$f['name']; }
  if(!$pk) throw new Exception('La tabla no tiene clave primaria');
  return [$columnas,$pk];
}
function entrada(){ return json_decode(file_get_contents('php://input'),true) ?: []; }

try{
  $ruta=$_GET['ruta'] ?? '';
  switch($ruta){
    case 'modulos': echo json_encode(['ventas','rrhh','facturacion','compras']); break;
    case 'entidades': echo json_encode(tablasPermitidas($db),JSON_UNESCAPED_UNICODE); break;
    case 'estructura':
      [$columnas,$pk]=estructura($db,$_GET['tabla'] ?? '');
      echo json_encode(['columnas'=>$columnas,'clavePrimaria'=>$pk],JSON_UNESCAPED_UNICODE); break;
    case 'tabla':
      $tabla=$_GET['tabla'] ?? ''; $segura=validarTabla($db,$tabla); [$columnas,$pk]=estructura($db,$tabla);
      $r=$db->query("SELECT * FROM $segura ORDER BY \"".str_replace('"','""',$pk)."\" DESC"); $registros=[];
      while($f=$r->fetchArray(SQLITE3_ASSOC)) $registros[]=$f;
      echo json_encode(['columnas'=>$columnas,'clavePrimaria'=>$pk,'registros'=>$registros],JSON_UNESCAPED_UNICODE); break;
    case 'crear':
      $e=entrada(); $tabla=$e['tabla']??''; $datos=$e['datos']??[]; $segura=validarTabla($db,$tabla); [$columnas,$pk]=estructura($db,$tabla);
      $permitidas=array_column(array_filter($columnas,fn($c)=>!$c['pk']),'name'); $datos=array_intersect_key($datos,array_flip($permitidas));
      if(!$datos) throw new Exception('No hay datos para insertar');
      $campos=array_keys($datos); $sql="INSERT INTO $segura (".implode(',',array_map(fn($c)=>'"'.str_replace('"','""',$c).'"',$campos)).") VALUES (".implode(',',array_fill(0,count($campos),'?')).")";
      $stmt=$db->prepare($sql); $i=1; foreach($datos as $v) $stmt->bindValue($i++,$v,SQLITE3_TEXT); $stmt->execute(); echo json_encode(['ok'=>true]); break;
    case 'actualizar':
      $e=entrada(); $tabla=$e['tabla']??''; $id=$e['id']??null; $datos=$e['datos']??[]; $segura=validarTabla($db,$tabla); [$columnas,$pk]=estructura($db,$tabla);
      $permitidas=array_column(array_filter($columnas,fn($c)=>!$c['pk']),'name'); $datos=array_intersect_key($datos,array_flip($permitidas));
      $sets=implode(',',array_map(fn($c)=>'"'.str_replace('"','""',$c).'" = ?',array_keys($datos))); $stmt=$db->prepare("UPDATE $segura SET $sets WHERE \"".str_replace('"','""',$pk)."\" = ?");
      $i=1; foreach($datos as $v) $stmt->bindValue($i++,$v,SQLITE3_TEXT); $stmt->bindValue($i,$id); $stmt->execute(); echo json_encode(['ok'=>true]); break;
    case 'eliminar':
      $e=entrada(); $tabla=$e['tabla']??''; $id=$e['id']??null; $segura=validarTabla($db,$tabla); [, $pk]=estructura($db,$tabla);
      $stmt=$db->prepare("DELETE FROM $segura WHERE \"".str_replace('"','""',$pk)."\" = ?"); $stmt->bindValue(1,$id); $stmt->execute(); echo json_encode(['ok'=>true]); break;
    default: throw new Exception('Ruta no válida');
  }
}catch(Throwable $e){ http_response_code(400); echo json_encode(['ok'=>false,'error'=>$e->getMessage()],JSON_UNESCAPED_UNICODE); }
$db->close();
?>
