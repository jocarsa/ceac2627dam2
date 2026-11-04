<?php
declare(strict_types=1);
require_once __DIR__.'/Repositorio.php';
require_once __DIR__.'/Vistas.php';
require_once __DIR__.'/Grafica.php';
require_once __DIR__.'/Formularios.php';
final class Presentacion {
 public function __construct(private Repositorio $repo){}
 public function tabla(string $nombre):string {
  $datos=$this->repo->tabla($nombre);$columnas=array_column($datos['columnas'],'name');
  return (new Tabla($nombre,$columnas,array_map(fn($f)=>array_values($f),$datos['registros'])))->renderizar();
 }
 public function formulario(string $nombre):string {
  $columnas=$this->repo->columnas($nombre);$relaciones=$this->repo->relaciones($nombre);$campos=[];
  foreach($columnas as $c){$tipo=strtoupper($c['type']);$n=$c['name'];if(str_contains($c['extra'],'auto_increment')||str_contains($c['extra'],'GENERATED'))continue;
   $campo=['nombre'=>$n,'titulo'=>str_replace('_',' ',ucfirst($n)),'tipo'=>$tipo,'required'=>$c['nullable']==='NO'&&$c['default_value']===null];
   if(isset($relaciones[$n])){$campo['tipo']='SELECT';$campo['opciones']=array_column($relaciones[$n],'value');$campo['required']=false;}
   elseif(str_contains($n,'email')&&str_starts_with($tipo,'VARCHAR')){$campo['tipo']='EMAIL';}
   elseif(str_contains($n,'telefono')&&str_starts_with($tipo,'VARCHAR')){$campo['tipo']='TEL';}
   elseif(in_array($c['data_type'],['text','mediumtext','longtext'],true)){$campo['tipo']='TEXTAREA';}
   elseif(in_array($c['data_type'],['json','geometry','point','linestring','polygon','multipoint','multilinestring','multipolygon','geometrycollection'],true)){$campo['tipo']='TEXTAREA';}
   $campos[]=$campo;
  }
  $form=new Formularios(['accion'=>'api/index.php?ruta=guardar&tabla='.rawurlencode($nombre),'metodo'=>'POST','campos'=>$campos,'boton'=>'Guardar registro']);
  return '<div class="vista"><h2>Nuevo registro</h2>'.$form->generar().'</div>';
 }
 public function dashboard():string {
  $totales=$this->repo->totales();$html='<div class="barra"><div><small>DATOS REALES · MYSQL</small><h2>Dashboard</h2></div></div><div class="dashboard-kpis"><div><small>Entidades</small><strong>'.count($totales).'</strong></div><div><small>Registros</small><strong>'.array_sum($totales).'</strong></div></div>';
  return $html.(new Grafica('Registros por entidad',$totales))->renderizar();
 }
 public function informe():string {
  $html='<div class="barra"><h2>Informe general</h2></div>'.$this->dashboard();foreach($this->repo->entidades() as $t)$html.=$this->tabla($t);return $html;
 }
}
