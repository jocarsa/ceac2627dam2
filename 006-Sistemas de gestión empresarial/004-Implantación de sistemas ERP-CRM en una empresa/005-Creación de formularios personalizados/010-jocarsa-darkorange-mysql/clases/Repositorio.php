<?php
declare(strict_types=1);
require_once __DIR__.'/Conexion.php';
final class Repositorio {
 private PDO $db;
 public function __construct(){ $this->db=Conexion::abrir(); }
 public function entidades(): array {return $this->db->query("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_TYPE='BASE TABLE' ORDER BY TABLE_NAME")->fetchAll(PDO::FETCH_COLUMN);}
 public function columnas(string $tabla):array {
  $q=$this->db->prepare('SELECT COLUMN_NAME AS name, COLUMN_TYPE AS type, DATA_TYPE AS data_type, IS_NULLABLE AS nullable, COLUMN_DEFAULT AS default_value, COLUMN_KEY AS column_key, EXTRA AS extra, CHARACTER_MAXIMUM_LENGTH AS max_length FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=? ORDER BY ORDINAL_POSITION');$q->execute([$tabla]);return $q->fetchAll();
 }
 public function tabla(string $tabla):array {
  $cols=$this->columnas($tabla);if(!$cols)throw new RuntimeException('Tabla desconocida');
  $sql='SELECT * FROM '.$this->ident($tabla).' LIMIT 200';$filas=$this->db->query($sql)->fetchAll();
  foreach($filas as &$fila)foreach($cols as $c){$n=$c['name'];if(in_array($c['data_type'],['blob','tinyblob','mediumblob','longblob','binary','varbinary','bit'],true)&&$fila[$n]!==null)$fila[$n]='[binario: '.strlen((string)$fila[$n]).' bytes]';}unset($fila);
  return ['tabla'=>$tabla,'columnas'=>$cols,'registros'=>$filas];
 }
 public function relaciones(string $tabla):array {
  $q=$this->db->prepare('SELECT COLUMN_NAME,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=? AND REFERENCED_TABLE_NAME IS NOT NULL');$q->execute([$tabla]);$salida=[];
  foreach($q->fetchAll() as $r){$t=$r['REFERENCED_TABLE_NAME'];$pk=$r['REFERENCED_COLUMN_NAME'];$cols=$this->columnas($t);$labels=array_column($cols,'name');$label=in_array('nombre',$labels,true)?'nombre':(in_array('titulo',$labels,true)?'titulo':$pk);
   $rows=$this->db->query('SELECT '.$this->ident($pk).' AS valor, '.$this->ident($label).' AS etiqueta FROM '.$this->ident($t).' LIMIT 500')->fetchAll();$salida[$r['COLUMN_NAME']]=array_map(fn($x)=>['value'=>(string)$x['valor'],'label'=>(string)$x['etiqueta'].' (#'.$x['valor'].')'],$rows);
  }return $salida;
 }
 public function insertar(string $tabla,array $datos,array $archivos=[]):int {
  $cols=$this->columnas($tabla);if(!$cols)throw new RuntimeException('Tabla desconocida');$campos=[];$valores=[];
  foreach($cols as $c){$n=$c['name'];if(str_contains($c['extra'],'auto_increment')||str_contains($c['extra'],'GENERATED'))continue;
   if(isset($archivos[$n])&&$archivos[$n]['error']===UPLOAD_ERR_OK){$v=file_get_contents($archivos[$n]['tmp_name']);if($v===false)throw new RuntimeException('Archivo no legible');$lim=$c['max_length']??match($c['data_type']){'tinyblob'=>255,'blob'=>65535,'mediumblob'=>16777215,'longblob'=>4294967295,default=>null};if($lim!==null&&strlen($v)>(int)$lim)throw new RuntimeException('Archivo demasiado grande: '.$n);}
   elseif(array_key_exists($n,$datos)){$v=$datos[$n];if(is_array($v))$v=implode(',',$v);if($v==='')$v=null;if($v!==null&&in_array($c['data_type'],['datetime','timestamp'],true))$v=str_replace('T',' ',$v);}
   else continue;
   $campos[]=$n;$valores[]=$v;
  }
  if(!$campos)throw new RuntimeException('No hay campos que guardar');
  $sql='INSERT INTO '.$this->ident($tabla).' ('.implode(',',array_map($this->ident(...),$campos)).') VALUES ('.implode(',',array_fill(0,count($campos),'?')).')';$q=$this->db->prepare($sql);$q->execute($valores);return (int)$this->db->lastInsertId();
 }
 public function totales():array {$salida=[];foreach($this->entidades() as $t){$salida[$t]=(int)$this->db->query('SELECT COUNT(*) FROM '.$this->ident($t))->fetchColumn();}return $salida;}
 private function ident(string $s):string {return '`'.str_replace('`','``',$s).'`';}
}
