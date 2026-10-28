<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
try {
 $root=dirname(__DIR__).'/data'; if(!is_dir($root))mkdir($root,0770,true);
 $meta=new PDO('sqlite:'.$root.'/application.sqlite');$meta->setAttribute(PDO::ATTR_ERRMODE,PDO::ERRMODE_EXCEPTION);$meta->exec('PRAGMA busy_timeout=5000; CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,name TEXT NOT NULL,view_json TEXT NOT NULL DEFAULT "{}",created_at TEXT DEFAULT CURRENT_TIMESTAMP); CREATE TABLE IF NOT EXISTS entities(project_id TEXT NOT NULL,id TEXT NOT NULL,title TEXT NOT NULL,x REAL NOT NULL,y REAL NOT NULL,properties_json TEXT NOT NULL,categories_json TEXT NOT NULL,PRIMARY KEY(project_id,id)); CREATE TABLE IF NOT EXISTS links(project_id TEXT NOT NULL,id TEXT NOT NULL,from_id TEXT NOT NULL,from_prop TEXT NOT NULL,to_id TEXT NOT NULL,to_prop TEXT NOT NULL,PRIMARY KEY(project_id,id)); CREATE TABLE IF NOT EXISTS preferences(key TEXT PRIMARY KEY,value TEXT NOT NULL);');
 $action=$_GET['action']??'load';$input=json_decode(file_get_contents('php://input'),true)??[];
 function out($v){echo json_encode($v,JSON_UNESCAPED_UNICODE|JSON_INVALID_UTF8_SUBSTITUTE);exit;}
 function projectDb(string $root,string $id):PDO {if(!preg_match('/^[a-zA-Z0-9_-]{1,100}$/',$id))throw new Exception('Identificador de proyecto no válido');$db=new PDO('sqlite:'.$root.'/project_'.$id.'.sqlite');$db->setAttribute(PDO::ATTR_ERRMODE,PDO::ERRMODE_EXCEPTION);$db->exec('PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;');return $db;}
 function ident(string $s):string {if($s===''||str_contains($s,"\0"))throw new Exception('Identificador SQL vacío');return '"'.str_replace('"','""',$s).'"';}
 function cols(array $entity):array {$out=[];foreach($entity['properties']??[] as $p){$parts=explode(':',$p['text']??'',2);$name=trim($parts[0]);if($name==='')throw new Exception('Campo sin nombre');$type=strtoupper(trim($parts[1]??'TEXT'));$base=preg_replace('/\(.*/','',$type);$aff=preg_match('/INT|BOOL/',$base)?'INTEGER':(preg_match('/REAL|FLOAT|DOUBLE|DECIMAL|NUMERIC/',$base)?'REAL':(preg_match('/BLOB|BINARY/',$base)?'BLOB':'TEXT'));$out[$p['id']]=['name'=>$name,'type'=>$aff];}return $out;}
 if($action==='load'){$projects=$meta->query('SELECT * FROM projects ORDER BY created_at,id')->fetchAll(PDO::FETCH_ASSOC);$result=[];foreach($projects as $p){$q=$meta->prepare('SELECT * FROM entities WHERE project_id=?');$q->execute([$p['id']]);$entities=[];foreach($q->fetchAll(PDO::FETCH_ASSOC) as $e){$entity=['id'=>$e['id'],'title'=>$e['title'],'x'=>(float)$e['x'],'y'=>(float)$e['y'],'properties'=>json_decode($e['properties_json'],true),'categories'=>json_decode($e['categories_json'],true)];$db=projectDb($root,$p['id']);try{$rows=$db->query('SELECT * FROM '.ident($e['title']))->fetchAll(PDO::FETCH_ASSOC);$columns=cols($entity);$entity['rows']=array_map(function($r)use($columns){$row=[];foreach($columns as $pid=>$col)$row[$pid]=$r[$col['name']]??null;return $row;},$rows);}catch(Throwable $ignored){$entity['rows']=[];}$entities[]=$entity;}$q=$meta->prepare('SELECT * FROM links WHERE project_id=?');$q->execute([$p['id']]);$links=array_map(fn($l)=>['id'=>$l['id'],'from'=>$l['from_id'],'fromProp'=>$l['from_prop'],'to'=>$l['to_id'],'toProp'=>$l['to_prop']],$q->fetchAll(PDO::FETCH_ASSOC));$result[]=['id'=>$p['id'],'name'=>$p['name'],'view'=>json_decode($p['view_json'],true),'data'=>['entities'=>$entities,'links'=>$links]];}$active=$meta->query("SELECT value FROM preferences WHERE key='activeId'")->fetchColumn();out(['ok'=>true,'store'=>['activeId'=>$active?:($result[0]['id']??null),'projects'=>$result]]);}
 if($action==='save'){
 $store=$input['store']??null;if(!is_array($store)||!isset($store['projects'])||!is_array($store['projects']))throw new Exception('Datos incorrectos');
 $meta->beginTransaction();$ids=[];
 foreach($store['projects'] as $p){$id=$p['id'];$ids[]=$id;$db=projectDb($root,$id);$entities=$p['data']['entities']??[];$links=$p['data']['links']??[];
 $stmt=$meta->prepare('INSERT INTO projects(id,name,view_json) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,view_json=excluded.view_json');$stmt->execute([$id,$p['name'],json_encode($p['view']??[])]);
 $meta->prepare('DELETE FROM entities WHERE project_id=?')->execute([$id]);$meta->prepare('DELETE FROM links WHERE project_id=?')->execute([$id]);
 foreach($entities as $e)$meta->prepare('INSERT INTO entities VALUES(?,?,?,?,?,?,?)')->execute([$id,$e['id'],$e['title'],$e['x'],$e['y'],json_encode($e['properties']),json_encode($e['categories']??[])]);
 foreach($links as $l)$meta->prepare('INSERT INTO links VALUES(?,?,?,?,?,?)')->execute([$id,$l['id'],$l['from'],$l['fromProp'],$l['to'],$l['toProp']]);
 // Preserve existing tables when schema changes; rebuild only if necessary.
 $db->exec('PRAGMA foreign_keys=OFF');$db->beginTransaction();
 $desired=[];
 foreach($entities as $e){$table=$e['title'];$desired[]=$table;$columns=cols($e);if(!$columns)continue;$names=array_column($columns,'name');if(count($names)!==count(array_unique(array_map('strtolower',$names))))throw new Exception('Campos duplicados en '.$table);
 $defs=[];foreach($columns as $c)$defs[]=ident($c['name']).' '.$c['type'];
 $pk=null;foreach($columns as $pid=>$c)if(strtolower($c['name'])==='id'){$pk=$c['name'];break;}
 if($pk)$defs[]='PRIMARY KEY ('.ident($pk).')';
 foreach($links as $l){if($l['to']!==$e['id'])continue;$source=null;foreach($entities as $candidate)if($candidate['id']===$l['from'])$source=$candidate;if(!$source)continue;$sc=cols($source);if(!isset($sc[$l['fromProp']],$columns[$l['toProp']]))continue;if(strtolower($sc[$l['fromProp']]['name'])!=='id')continue;$defs[]='FOREIGN KEY ('.ident($columns[$l['toProp']]['name']).') REFERENCES '.ident($source['title']).' ('.ident($sc[$l['fromProp']]['name']).')';}
 $create='CREATE TABLE '.ident($table).' ('.implode(',',$defs).')';$old=$db->query("SELECT sql FROM sqlite_master WHERE type='table' AND name=".$db->quote($table))->fetchColumn();
 if(!$old){$db->exec($create);}else{$norm=fn($s)=>strtolower(preg_replace('/\s+/','',str_replace(['"','`'],'',$s)));if($norm($old)!==$norm($create)){$tmp='__migration_'.substr(hash('sha256',$e['id']),0,16);$db->exec('DROP TABLE IF EXISTS '.ident($tmp));$db->exec(str_replace('CREATE TABLE '.ident($table),'CREATE TABLE '.ident($tmp),$create));$oldcols=$db->query('PRAGMA table_info('.ident($table).')')->fetchAll(PDO::FETCH_ASSOC);$common=array_values(array_intersect($names,array_column($oldcols,'name')));if($common){$c=implode(',',array_map('ident',$common));$db->exec('INSERT OR IGNORE INTO '.ident($tmp).' ('.$c.') SELECT '.$c.' FROM '.ident($table));}$db->exec('DROP TABLE '.ident($table));$db->exec('ALTER TABLE '.ident($tmp).' RENAME TO '.ident($table));}} 
 // Rows are real SQLite data, not JSON blobs.
 $db->exec('DELETE FROM '.ident($table));foreach($e['rows']??[] as $r){$fields=[];$values=[];foreach($columns as $pid=>$c){if(array_key_exists($pid,$r)&&$r[$pid]!==''&&$r[$pid]!==null){$fields[]=$c['name'];$values[]=$r[$pid];}}if(!$fields)continue;$sql='INSERT INTO '.ident($table).' ('.implode(',',array_map('ident',$fields)).') VALUES ('.implode(',',array_fill(0,count($fields),'?')).')';$db->prepare($sql)->execute($values);}
 }
 // Drop tables removed from the model (exclude internal SQLite tables).
 $existing=$db->query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")->fetchAll(PDO::FETCH_COLUMN);foreach($existing as $name)if(!in_array($name,$desired,true))$db->exec('DROP TABLE '.ident($name));
 $db->commit();$db->exec('PRAGMA foreign_keys=ON');
 }
 $all=$meta->query('SELECT id FROM projects')->fetchAll(PDO::FETCH_COLUMN);foreach($all as $id)if(!in_array($id,$ids,true)){$meta->prepare('DELETE FROM projects WHERE id=?')->execute([$id]);$meta->prepare('DELETE FROM entities WHERE project_id=?')->execute([$id]);$meta->prepare('DELETE FROM links WHERE project_id=?')->execute([$id]);}
 $meta->prepare("INSERT INTO preferences(key,value) VALUES('activeId',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value")->execute([$store['activeId']??'']);$meta->commit();foreach($all as $id)if(!in_array($id,$ids,true))@unlink($root.'/project_'.$id.'.sqlite');out(['ok'=>true]);
 }
 throw new Exception('Acción desconocida');
}catch(Throwable $e){if(isset($meta)&&$meta->inTransaction())$meta->rollBack();http_response_code(400);out(['ok'=>false,'error'=>$e->getMessage()]);}
