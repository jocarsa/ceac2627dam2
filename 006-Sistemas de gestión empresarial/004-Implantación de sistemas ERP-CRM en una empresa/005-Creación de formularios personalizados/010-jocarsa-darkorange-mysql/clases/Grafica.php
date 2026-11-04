<?php
declare(strict_types=1);
require_once __DIR__.'/Vistas.php';
class Grafica extends Vista {
 public function __construct(string $titulo,private array $datos,private string $tipo='barras'){parent::__construct($titulo);}
 public function renderizar():string {
  $html='<div class="vista"><h2>'.$this->escapar($this->titulo).'</h2>';
  if(!$this->datos)return $html.'<p>Sin datos</p></div>';
  $max=max(1,...array_values($this->datos));$i=0;
  $html.='<div class="grafica-barras">';
  foreach($this->datos as $etiqueta=>$valor){$pct=round(100*$valor/$max,2);$html.='<div class="grafica-fila"><span>'.$this->escapar((string)$etiqueta).'</span><div class="grafica-pista"><div class="grafica-barra" style="width:'.$pct.'%"></div></div><strong>'.(int)$valor.'</strong></div>';$i++;}
  return $html.'</div></div>';
 }
}
