<?php
$mdFile=__DIR__.'/proyectos.md'; $dbFile=__DIR__.'/proyectos.sqlite';
function parseMarkdownTree(string $file):array{$lines=file($file,FILE_IGNORE_NEW_LINES);$root=['title'=>'ROOT','children'=>[]];$stack=[];$stack[]=&$root;foreach($lines as $line){if(!preg_match('/^(\s*)-\s*(.+?)\s*$/u',$line,$m))continue;$spaces=strlen(str_replace("\t",'    ',$m[1]));$level=intdiv($spaces,4);$title=trim($m[2]);if($title==='')continue;$node=['title'=>$title,'children'=>[]];while(count($stack)>$level+1)array_pop($stack);$parent=&$stack[count($stack)-1];$parent['children'][]=$node;$idx=count($parent['children'])-1;$stack[]=&$parent['children'][$idx];unset($parent);}return $root['children'];}
function nodeKey(array $path):string{return hash('sha256',implode(' > ',$path));}
function h($s):string{return htmlspecialchars((string)$s,ENT_QUOTES,'UTF-8');}
function colorData(float $start,float $size,int $i,int $count):array{$slice=$size/max(1,$count);$s=$start+$i*$slice;$h=fmod($s+$slice/2+360,360);return [$s,$slice,$h];}
$db=new PDO('sqlite:'.$dbFile);$db->setAttribute(PDO::ATTR_ERRMODE,PDO::ERRMODE_EXCEPTION);$db->exec("CREATE TABLE IF NOT EXISTS proyectos(node_key TEXT PRIMARY KEY,titulo TEXT NOT NULL DEFAULT '',descripcion TEXT NOT NULL DEFAULT '',estado TEXT NOT NULL DEFAULT 'pendiente',actualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)");
if($_SERVER['REQUEST_METHOD']==='POST'){
  $st=$db->prepare("INSERT INTO proyectos(node_key,titulo,descripcion,estado,actualizado) VALUES(?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(node_key) DO UPDATE SET titulo=excluded.titulo,descripcion=excluded.descripcion,estado=excluded.estado,actualizado=CURRENT_TIMESTAMP");
  $st->execute([$_POST['node_key']??'',trim($_POST['titulo']??''),trim($_POST['descripcion']??''),$_POST['estado']??'pendiente']);
  if(($_POST['ajax']??'')==='1'){header('Content-Type: application/json; charset=utf-8');echo json_encode(['ok'=>true]);exit;}
  header('Location: '.$_SERVER['PHP_SELF']);exit;
}
$tree=parseMarkdownTree($mdFile);$projects=[];foreach($db->query('SELECT * FROM proyectos') as $row)$projects[$row['node_key']]=$row;
function renderRows(array $nodes,array $path,array $projects,float $start=0,float $size=360,int $depth=0):void{$count=count($nodes);foreach($nodes as $i=>$n){[$s,$slice,$hue]=colorData($start,$size,$i,$count);$p=[...$path,$n['title']];$key=nodeKey($p);$pr=$projects[$key]??null;$has=count($n['children'])>0;$sat=max(42,64-$depth*3);$light=min(92,78+$depth*3);?>
<section class="pair-node depth-<?=$depth?>" data-key="<?=$key?>" data-level="<?=$depth?>" data-search="<?=h(mb_strtolower(implode(' ',$p).' '.($pr['titulo']??'').' '.($pr['descripcion']??'')))?>" style="--hue:<?=$hue?>;--sat:<?=$sat?>%;--light:<?=$light?>%;--depth:<?=$depth?>">
  <div class="pair-row">
    <div class="curriculum-cell">
      <button class="toggle <?=$has?'':'empty'?>" type="button"><?=$has?'▾':'•'?></button>
      <div class="cell-copy"><span class="level-label">NIVEL <?=$depth+1?></span><strong><?=h($n['title'])?></strong></div>
    </div>
    <div class="project-cell">
      <input class="inline-project-title" type="text" data-key="<?=$key?>" value="<?=h($pr['titulo']??'')?>" placeholder="Escribe el proyecto…" aria-label="Proyecto para <?=h($n['title'])?>">
      <span class="save-state" aria-live="polite"></span>
    </div>
  </div>
  <?php if($has):?><div class="pair-children"><?php renderRows($n['children'],$p,$projects,$s,$slice,$depth+1)?></div><?php endif?>
</section><?php }}
?>
<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mapa curricular y proyectos</title><link rel="stylesheet" href="style.css"></head><body>
<header class="topbar"><div><span class="kicker">JOCARSA · MAPA CURRICULAR</span><h1>Currículo ↔ Proyectos</h1></div><div class="toolbar"><input id="search" type="search" placeholder="Buscar unidad o proyecto…"><button id="expand">Expandir</button><button id="collapse">Contraer</button></div></header>
<div class="column-heads"><div>UNIDADES · SUBUNIDADES · CONTENIDOS</div><div>PROYECTOS ASOCIADOS</div></div>
<main id="map"><?php renderRows($tree,[],$projects)?></main>
<script src="app.js"></script></body></html>
