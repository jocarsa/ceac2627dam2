<?php
header('Content-Type: application/json; charset=utf-8');
function out($v,$code=200){http_response_code($code);echo json_encode($v,JSON_UNESCAPED_UNICODE|JSON_INVALID_UTF8_SUBSTITUTE);exit;}
try {
 $db=new SQLite3(__DIR__.'/empresa.db',SQLITE3_OPEN_READWRITE);
 $db->enableExceptions(true);$db->busyTimeout(5000);$db->exec('PRAGMA foreign_keys=ON');
 $db->exec('CREATE TABLE IF NOT EXISTS facturas (id INTEGER PRIMARY KEY AUTOINCREMENT,numero TEXT UNIQUE NOT NULL,fecha TEXT NOT NULL,pedido_id INTEGER UNIQUE REFERENCES pedidos(id),cliente_id INTEGER NOT NULL REFERENCES clientes(id),producto_id INTEGER NOT NULL REFERENCES productos(id),cliente_nombre TEXT NOT NULL,cliente_apellidos TEXT NOT NULL,cliente_email TEXT,cliente_telefono TEXT,cliente_ciudad TEXT,producto_nombre TEXT NOT NULL,producto_modelo TEXT NOT NULL,producto_categoria TEXT,producto_potencia INTEGER,producto_autonomia INTEGER,base REAL NOT NULL,iva REAL NOT NULL,total REAL NOT NULL)');
 $accion=$_POST['accion']??$_GET['accion']??'';
 if($accion==='listar'){
  $r=$db->query('SELECT id,numero,fecha,pedido_id,cliente_nombre || " " || cliente_apellidos AS cliente,producto_nombre || " " || producto_modelo AS producto,total FROM facturas ORDER BY id DESC LIMIT 500');$filas=[];while($x=$r->fetchArray(SQLITE3_ASSOC))$filas[]=$x;out(['tipo'=>'SELECT','resultados'=>$filas]);
 }
 if($accion!=='crear')out(['error'=>'Acción desconocida'],400);
 $pedido=filter_var($_POST['pedido_id']??null,FILTER_VALIDATE_INT);
 $cliente=filter_var($_POST['cliente_id']??null,FILTER_VALIDATE_INT);
 $producto=filter_var($_POST['producto_id']??null,FILTER_VALIDATE_INT);
 $precio=filter_var($_POST['precio']??null,FILTER_VALIDATE_FLOAT);
 if(!$pedido && (!$cliente || !$producto || $precio===false || $precio===null || $precio<0))out(['error'=>'Indica un pedido válido o cliente_id, producto_id y precio (base sin IVA)'],400);
 $db->exec('BEGIN IMMEDIATE');
 try{
  if($pedido){
   $s=$db->prepare('SELECT p.id pedido_id,p.cliente_id,p.producto_id,p.precio_venta base,c.nombre cliente_nombre,c.apellidos cliente_apellidos,c.email cliente_email,c.telefono cliente_telefono,c.ciudad cliente_ciudad,pr.nombre producto_nombre,pr.modelo producto_modelo,pr.categoria producto_categoria,pr.potencia producto_potencia,pr.autonomia producto_autonomia FROM pedidos p JOIN clientes c ON c.id=p.cliente_id JOIN productos pr ON pr.id=p.producto_id WHERE p.id=:id');$s->bindValue(':id',$pedido,SQLITE3_INTEGER);
  }else{
   $s=$db->prepare('SELECT NULL pedido_id,c.id cliente_id,pr.id producto_id,:base base,c.nombre cliente_nombre,c.apellidos cliente_apellidos,c.email cliente_email,c.telefono cliente_telefono,c.ciudad cliente_ciudad,pr.nombre producto_nombre,pr.modelo producto_modelo,pr.categoria producto_categoria,pr.potencia producto_potencia,pr.autonomia producto_autonomia FROM clientes c CROSS JOIN productos pr WHERE c.id=:cliente AND pr.id=:producto');$s->bindValue(':cliente',$cliente,SQLITE3_INTEGER);$s->bindValue(':producto',$producto,SQLITE3_INTEGER);$s->bindValue(':base',$precio,SQLITE3_FLOAT);
  }
  $fila=$s->execute()->fetchArray(SQLITE3_ASSOC);
  if(!$fila)throw new RuntimeException('Pedido, cliente o producto inexistente');
  if($pedido){$check=$db->prepare('SELECT id FROM facturas WHERE pedido_id=:p');$check->bindValue(':p',$pedido,SQLITE3_INTEGER);if($check->execute()->fetchArray(SQLITE3_ASSOC))throw new RuntimeException('Este pedido ya tiene una factura');}
  $base=round((float)$fila['base'],2);if($base<0)throw new RuntimeException('Importe inválido');
  $iva=round($base*.21,2);$total=round($base+$iva,2);
  $fecha=date('Y-m-d');$anio=date('Y');
  $seq=(int)$db->querySingle("SELECT COALESCE(MAX(id),0)+1 FROM facturas");
  $numero=sprintf('F-%s-%06d',$anio,$seq);
  $cols=['numero','fecha','pedido_id','cliente_id','producto_id','cliente_nombre','cliente_apellidos','cliente_email','cliente_telefono','cliente_ciudad','producto_nombre','producto_modelo','producto_categoria','producto_potencia','producto_autonomia','base','iva','total'];
  $values=array_merge(['numero'=>$numero,'fecha'=>$fecha],$fila,['base'=>$base,'iva'=>$iva,'total'=>$total]);
  $q=$db->prepare('INSERT INTO facturas ('.implode(',',$cols).') VALUES (:'.implode(',:',$cols).')');
  foreach($cols as $col){$v=$values[$col]??null;$q->bindValue(':'.$col,$v,$v===null?SQLITE3_NULL:(is_int($v)?SQLITE3_INTEGER:(is_float($v)?SQLITE3_FLOAT:SQLITE3_TEXT)));}
  $q->execute();$id=$db->lastInsertRowID();$db->exec('COMMIT');out(['tipo'=>'FACTURA','mensaje'=>'Factura creada','factura_id'=>$id,'numero'=>$numero,'url'=>'factura.php?id='.$id]);
 }catch(Throwable $e){$db->exec('ROLLBACK');throw $e;}
}catch(Throwable $e){out(['error'=>$e->getMessage()],400);}
