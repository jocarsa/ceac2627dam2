(()=>{'use strict';
const KEY='entity-universe-v2',OLD='entity-universe-v1';
const categoriesLayer=document.querySelector('#categoriesLayer'),viewport=document.querySelector('#viewport'),world=document.querySelector('#world'),nodes=document.querySelector('#nodes'),svg=document.querySelector('#wires'),dialog=document.querySelector('#editor');
const uid=()=>globalThis.crypto?.randomUUID?.()||`${Date.now()}-${Math.random()}`;
const empty=()=>({entities:[],links:[]});
const PROJECT_KEY='entity-universe-projects-v7';
let data=empty(),selected=null,editing=null,drag=null,view={x:Math.round(innerWidth/2-130),y:110,z:1};
let store=null;
const freshProject=(name,content=empty())=>({id:uid(),name,data:content,view:{x:Math.round(innerWidth/2-130),y:110,z:1}});
try{
 const saved=JSON.parse(localStorage.getItem(PROJECT_KEY)||'null');
 if(saved&&Array.isArray(saved.projects)&&saved.projects.length){store=saved;}
}catch{}
if(!store){
 let legacy=empty();
 try{const old=JSON.parse(localStorage.getItem(KEY)||localStorage.getItem(OLD)||'null');if(old&&Array.isArray(old.entities)&&Array.isArray(old.links))legacy=old;}catch{}
 const first=freshProject('Mi primer proyecto',legacy);
 store={activeId:first.id,projects:[first]};
}
store.projects=store.projects.filter(p=>p&&typeof p.id==='string'&&p.data&&Array.isArray(p.data.entities)&&Array.isArray(p.data.links));
if(!store.projects.length){const first=freshProject('Mi primer proyecto');store.projects=[first];store.activeId=first.id;}
if(!store.projects.some(p=>p.id===store.activeId))store.activeId=store.projects[0].id;
const activeProject=()=>store.projects.find(p=>p.id===store.activeId);
function loadProject(){const p=activeProject();data=p.data;view={...p.view};selected=null;drag=null;lastTap=null;transform();render();refreshProjectSelect();}
let syncTimer=null, syncBusy=false, syncAgain=false;
async function syncServer(){if(syncBusy){syncAgain=true;return;}syncBusy=true;try{const response=await fetch('api/index.php?action=save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({store})});const result=await response.json();if(!result.ok)throw Error(result.error);document.querySelector('#syncStatus').textContent='Guardado en SQLite';}catch(err){document.querySelector('#syncStatus').textContent='Error: '+err.message;console.error(err);}finally{syncBusy=false;if(syncAgain){syncAgain=false;syncServer();}}}
function persist(){const p=activeProject();p.data=data;p.view={...view};localStorage.setItem(PROJECT_KEY,JSON.stringify(store));document.querySelector('#syncStatus').textContent='Guardando…';clearTimeout(syncTimer);syncTimer=setTimeout(syncServer,650);}
function refreshProjectSelect(){const select=document.querySelector('#projectSelect');select.replaceChildren();for(const p of store.projects){const option=document.createElement('option');option.value=p.id;option.textContent=p.name;select.append(option);}select.value=store.activeId;document.querySelector('#deleteProject').disabled=store.projects.length===1;}
function normalizeProps(props){return (props||[]).map(p=>typeof p==='string'?{id:uid(),text:p}:p).filter(p=>p&&typeof p.id==='string'&&typeof p.text==='string');}
data.entities.forEach(n=>{n.properties=normalizeProps(n.properties);n.categories=normalizeCategories(n.categories);});
function normalizeCategories(value){return [...new Set((Array.isArray(value)?value.join(','):String(value||'')).split(',').map(x=>x.trim()).filter(Boolean))];}
const save=()=>persist();
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const find=id=>data.entities.find(n=>n.id===id);
function transform(){world.style.transform=`translate(${view.x}px,${view.y}px) scale(${view.z})`;viewport.style.backgroundPosition=`${view.x}px ${view.y}px`;viewport.style.backgroundSize=`${28*view.z}px ${28*view.z}px`;}
function pos(e){const r=viewport.getBoundingClientRect();return{x:(e.clientX-r.left-view.x)/view.z,y:(e.clientY-r.top-view.y)/view.z};}
function endpoint(entityId,propId,side){const slot=Array.from(nodes.querySelectorAll('.slot')).find(s=>s.dataset.entity===entityId&&s.dataset.prop===propId&&s.dataset.side===side);if(!slot)return null;const sr=slot.getBoundingClientRect(),vr=viewport.getBoundingClientRect();return{x:(sr.left+sr.width/2-vr.left-view.x)/view.z,y:(sr.top+sr.height/2-vr.top-view.y)/view.z};}
function curve(a,b){const d=Math.max(55,Math.abs(b.x-a.x)*.48);return`M${a.x},${a.y} C${a.x+d},${a.y} ${b.x-d},${b.y} ${b.x},${b.y}`;}
function wire(a,b,color,dashed=false){const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',curve(a,b));p.setAttribute('fill','none');p.setAttribute('stroke',color);p.setAttribute('stroke-width','3');p.setAttribute('stroke-linecap','round');if(dashed)p.setAttribute('stroke-dasharray','7 6');svg.append(p);}
// Contornos orgánicos: envolvente convexa de muestras elípticas y suavizado Chaikin.
function convexHull(points){
 const cross=(o,a,b)=>(a.x-o.x)*(b.y-o.y)-(a.y-o.y)*(b.x-o.x);
 const sorted=points.sort((a,b)=>a.x-b.x||a.y-b.y),lower=[],upper=[];
 for(const p of sorted){while(lower.length>1&&cross(lower[lower.length-2],lower[lower.length-1],p)<=0)lower.pop();lower.push(p);}
 for(const p of [...sorted].reverse()){while(upper.length>1&&cross(upper[upper.length-2],upper[upper.length-1],p)<=0)upper.pop();upper.push(p);}
 lower.pop();upper.pop();return lower.concat(upper);
}
function soften(points,rounds=3){
 for(let k=0;k<rounds;k++){const next=[];for(let i=0;i<points.length;i++){const a=points[i],b=points[(i+1)%points.length];next.push({x:a.x*.75+b.x*.25,y:a.y*.75+b.y*.25},{x:a.x*.25+b.x*.75,y:a.y*.25+b.y*.75});}points=next;}return points;
}
function drawCategories(){
 categoriesLayer.replaceChildren();
 const groups=new Map();
 for(const n of data.entities)for(const category of normalizeCategories(n.categories)){
  const key=category.toLocaleLowerCase();if(!groups.has(key))groups.set(key,{name:category,entities:[]});groups.get(key).entities.push(n);
 }
 let index=0;
 for(const group of groups.values()){
  const boxes=group.entities.map(n=>{const el=Array.from(nodes.children).find(e=>e.dataset.id===n.id);return{x:n.x,y:n.y,w:el?.offsetWidth||260,h:el?.offsetHeight||110};});
  if(!boxes.length)continue;
  const pad=35+(index%3)*8, samples=[];
  for(const b of boxes){const cx=b.x+b.w/2,cy=b.y+b.h/2,rx=b.w/2+pad,ry=b.h/2+pad;
   for(let i=0;i<32;i++){const t=2*Math.PI*i/32;samples.push({x:cx+rx*Math.cos(t),y:cy+ry*Math.sin(t)});}
  }
  const contour=soften(convexHull(samples));
  if(contour.length<3)continue;
  const d='M'+contour.map(p=>`${p.x.toFixed(2)},${p.y.toFixed(2)}`).join(' L')+' Z';
  const hue=(index*71+210)%360,color=`hsl(${hue} 75% 65%)`;
  const path=document.createElementNS('http://www.w3.org/2000/svg','path');
  for(const [k,v] of Object.entries({d,fill:color,'fill-opacity':'.075',stroke:color,'stroke-width':'2.5','stroke-dasharray':'9 7','stroke-opacity':'.85','stroke-linejoin':'round'}))path.setAttribute(k,v);
  categoriesLayer.append(path);
  const top=contour.reduce((a,b)=>b.y<a.y?b:a);
  const label=document.createElementNS('http://www.w3.org/2000/svg','text');
  for(const [k,v] of Object.entries({x:top.x,y:top.y-10,fill:color,'font-size':'15','font-weight':'700','text-anchor':'middle'}))label.setAttribute(k,v);
  label.textContent=group.name;categoriesLayer.append(label);
  index++;
 }
}
function drawWires(){drawCategories();svg.replaceChildren();for(const l of data.links){const a=endpoint(l.from,l.fromProp,'out'),b=endpoint(l.to,l.toProp,'in');if(a&&b)wire(a,b,'#91a1ff');}if(drag?.type==='link'){const a=endpoint(drag.from,drag.fromProp,drag.side);if(a)wire(drag.side==='out'?a:drag.to,drag.side==='out'?drag.to:a,'#69e7b8',true);}}
function render(){nodes.replaceChildren();for(const n of data.entities){const el=document.createElement('div');el.className='node'+(selected===n.id?' selected':'');el.dataset.id=n.id;el.style.left=n.x+'px';el.style.top=n.y+'px';el.innerHTML=`<div class="node-head"><span>${esc(n.title)}</span><button type="button" class="records-btn" data-records="${esc(n.id)}" title="Ver y editar datos de ${esc(n.title)}" aria-label="Abrir registros de ${esc(n.title)}">▦ <span>${(n.rows||[]).length}</span></button></div><div class="node-props">${n.properties.map(p=>{const i=p.text.indexOf(':');return`<div class="prop" data-prop="${esc(p.id)}"><span class="slot in" data-entity="${esc(n.id)}" data-prop="${esc(p.id)}" data-side="in" title="Entrada: ${esc(p.text)}"></span><span class="prop-name">${esc(i<0?p.text:p.text.slice(0,i))}</span><span class="prop-type">${esc(i<0?'':p.text.slice(i+1).trim())}</span><span class="slot out" data-entity="${esc(n.id)}" data-prop="${esc(p.id)}" data-side="out" title="Salida: ${esc(p.text)}"></span></div>`}).join('')||'<div class="no-props">Añade propiedades para conectar entidades</div>'}</div>`;nodes.append(el);}drawWires();document.querySelector('.hint').textContent=data.entities.length?'Arrastra entre conectores de propiedades para relacionarlas · Arrastra el título para mover · Doble clic para editar · Rueda para ampliar':'El espacio está vacío. Pulsa + Entidad para crear la primera.';}
function edit(id){editing=id;const n=find(id);document.querySelector('#formTitle').textContent=n?'Editar entidad':'Nueva entidad';document.querySelector('#title').value=n?.title||'';document.querySelector('#categories').value=normalizeCategories(n?.categories).join(', ');document.querySelector('#properties').value=n?.properties.map(p=>p.text).join('\n')||'';document.querySelector('#deleteEntity').hidden=!n;dialog.showModal();document.querySelector('#title').focus();}
document.querySelector('#add').onclick=()=>edit(null);document.querySelector('#cancel').onclick=()=>dialog.close();
document.querySelector('#entityForm').onsubmit=e=>{e.preventDefault();const title=document.querySelector('#title').value.trim();if(!title)return;const lines=document.querySelector('#properties').value.split('\n').map(x=>x.trim()).filter(Boolean);if(editing){const n=find(editing);const old=n.properties;const used=new Set();n.title=title;n.categories=normalizeCategories(document.querySelector('#categories').value);n.properties=lines.map((text,i)=>{let p=old[i];if(!p||used.has(p.id))p={id:uid(),text};used.add(p.id);return{id:p.id,text};});const valid=new Set(n.properties.map(p=>p.id));data.links=data.links.filter(l=>(l.from!==n.id||valid.has(l.fromProp))&&(l.to!==n.id||valid.has(l.toProp)));}else{const r=viewport.getBoundingClientRect(),p=pos({clientX:r.left+r.width/2,clientY:r.top+r.height/2});const n={id:uid(),title,categories:normalizeCategories(document.querySelector('#categories').value),properties:lines.map(text=>({id:uid(),text})),x:p.x-130,y:p.y-65};data.entities.push(n);selected=n.id;}save();render();dialog.close();};
document.querySelector('#deleteEntity').onclick=()=>{if(!editing)return;data.entities=data.entities.filter(n=>n.id!==editing);data.links=data.links.filter(l=>l.from!==editing&&l.to!==editing);selected=null;save();render();dialog.close();};

nodes.addEventListener('click',e=>{const b=e.target.closest('.records-btn');if(b){e.stopPropagation();openRecords(b.dataset.records);}});
viewport.addEventListener('pointerdown',e=>{if(e.target.closest('.records-btn'))return;if(e.button!==0&&e.button!==1)return;const slot=e.target.closest('.slot'),node=e.target.closest('.node');if(slot&&e.button===0){drag={type:'link',from:slot.dataset.entity,fromProp:slot.dataset.prop,side:slot.dataset.side,to:pos(e)};e.preventDefault();}else if(node&&e.button===0){selected=node.dataset.id;const n=find(selected);drag={type:'node',id:n.id,start:pos(e),x:n.x,y:n.y,clientX:e.clientX,clientY:e.clientY};nodes.querySelectorAll('.node').forEach(el=>el.classList.toggle('selected',el.dataset.id===selected));}else{drag={type:'pan',x:e.clientX,y:e.clientY,vx:view.x,vy:view.y};viewport.classList.add('panning');}viewport.setPointerCapture(e.pointerId);});
viewport.addEventListener('pointermove',e=>{if(!drag)return;if(drag.type==='pan'){view.x=drag.vx+e.clientX-drag.x;view.y=drag.vy+e.clientY-drag.y;transform();}else if(drag.type==='node'){const n=find(drag.id),p=pos(e);n.x=drag.x+p.x-drag.start.x;n.y=drag.y+p.y-drag.start.y;const el=Array.from(nodes.children).find(el=>el.dataset.id===n.id);if(el){el.style.left=n.x+'px';el.style.top=n.y+'px';}drawWires();}else{drag.to=pos(e);drawWires();}});
let lastTap=null;
function end(e){
 if(!drag)return;
 const action=drag;
 if(viewport.hasPointerCapture(e.pointerId))viewport.releasePointerCapture(e.pointerId);
 if(action.type==='link'&&e.type==='pointerup'){
   const target=document.elementsFromPoint(e.clientX,e.clientY).map(el=>el.closest?.('.slot')).find(Boolean);
   if(target&&target.dataset.entity!==action.from&&target.dataset.side!==action.side){
     const from=action.side==='out'?{id:action.from,prop:action.fromProp}:{id:target.dataset.entity,prop:target.dataset.prop};
     const to=action.side==='out'?{id:target.dataset.entity,prop:target.dataset.prop}:{id:action.from,prop:action.fromProp};
     if(!data.links.some(l=>l.from===from.id&&l.fromProp===from.prop&&l.to===to.id&&l.toProp===to.prop))data.links.push({id:uid(),from:from.id,fromProp:from.prop,to:to.id,toProp:to.prop});
   }
 }
 if(action.type==='node'&&e.type==='pointerup'){
   const distance=Math.hypot(e.clientX-action.clientX,e.clientY-action.clientY);
   if(distance<6){
     const now=Date.now();
     if(lastTap&&lastTap.id===action.id&&now-lastTap.time<450){lastTap=null;drag=null;edit(action.id);return;}
     lastTap={id:action.id,time:now};
   }else lastTap=null;
 }
 drag=null;viewport.classList.remove('panning');
 if(action.type==='node'||action.type==='link')save();
 // Do not recreate nodes on pointerup: that prevents native double-click.
 drawWires();
}
viewport.addEventListener('pointerup',end);viewport.addEventListener('pointercancel',end);
viewport.addEventListener('wheel',e=>{e.preventDefault();const r=viewport.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top,old=view.z;view.z=Math.max(.3,Math.min(2.5,view.z*Math.exp(-e.deltaY*.001)));view.x=x-(x-view.x)*view.z/old;view.y=y-(y-view.y)*view.z/old;transform();drawWires();},{passive:false});
document.querySelector('#fit').onclick=()=>{if(!data.entities.length){view={x:viewport.clientWidth/2-130,y:100,z:1};transform();save();return;}const minX=Math.min(...data.entities.map(n=>n.x)),maxX=Math.max(...data.entities.map(n=>n.x+260)),minY=Math.min(...data.entities.map(n=>n.y)),maxY=Math.max(...data.entities.map(n=>n.y+75+n.properties.length*36));view.z=Math.min(1.2,Math.max(.3,Math.min((viewport.clientWidth-90)/(maxX-minX),(viewport.clientHeight-90)/(maxY-minY))));view.x=(viewport.clientWidth-(minX+maxX)*view.z)/2;view.y=(viewport.clientHeight-(minY+maxY)*view.z)/2;transform();drawWires();save();};
document.querySelector('#export').onclick=()=>{const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=(activeProject().name.replace(/[^a-z0-9áéíóúñ_-]+/gi,'-')||'proyecto')+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
// Exportación SQL: respeta los tipos y longitudes escritos en cada propiedad.
function sqlIdentifier(name,engine){const q=engine==='mysql'?'`':'"';return q+String(name).replaceAll(q,q+q)+q;}
function sqlType(raw,engine){
 const t=String(raw||'').trim();if(!t)return engine==='mysql'?'TEXT':'TEXT';
 const match=t.match(/^([\p{L}_][\p{L}\p{N}_ ]*)(?:\s*\(\s*(\d+)\s*(?:,\s*(\d+)\s*)?\))?(.*)$/u);
 if(!match)throw Error('Tipo no válido: '+t);
 const base=match[1].trim().toUpperCase().replace(/\s+/g,' '),length=match[2],scale=match[3],suffix=match[4].trim();
 if(suffix&&!/^(NOT NULL|NULL|UNIQUE|DEFAULT\s+(?:NULL|CURRENT_TIMESTAMP|[-+]?\d+(?:\.\d+)?|'(?:[^']|'')*')|UNSIGNED)(?:\s+(?:NOT NULL|NULL|UNIQUE|DEFAULT\s+(?:NULL|CURRENT_TIMESTAMP|[-+]?\d+(?:\.\d+)?|'(?:[^']|'')*')|UNSIGNED))*$/i.test(suffix))throw Error('Modificador de tipo no admitido: '+suffix);
 const aliases={ENTERO:'INTEGER',ENTIER:'INTEGER',INT:'INTEGER',TEXTO:'TEXT',CADENA:'VARCHAR',STRING:'VARCHAR',BOOLEANO:'BOOLEAN',BOOL:'BOOLEAN',REAL:'REAL',DECIMAL:'DECIMAL',FECHA:'DATE',FECHAHORA:'DATETIME',NUMERO:'NUMERIC'};
 const b=aliases[base]||base;
 const allowed=new Set(['INTEGER','INT','BIGINT','SMALLINT','TINYINT','VARCHAR','CHAR','TEXT','LONGTEXT','MEDIUMTEXT','TINYTEXT','DECIMAL','NUMERIC','FLOAT','DOUBLE','REAL','BOOLEAN','DATE','DATETIME','TIMESTAMP','TIME','BLOB','JSON','BINARY','VARBINARY']);
 if(!allowed.has(b))throw Error('Tipo SQL no reconocido: '+base);
 if(length&&(!Number.isSafeInteger(Number(length))||Number(length)<1||Number(length)>65535))throw Error('Longitud fuera de rango: '+length);
 if(scale&&(Number(scale)>Number(length)))throw Error('Escala decimal mayor que precisión');
 let type=b;
 if(engine==='mysql'){
   if(b==='BOOLEAN')type='BOOLEAN';
   else if(b==='REAL')type='DOUBLE';
   else if(b==='VARCHAR'&&!length)type='VARCHAR(255)';
   else if(b==='TEXT'&&length)type='VARCHAR';
 }else{
   if(['INT','TINYINT','SMALLINT','BIGINT','BOOLEAN'].includes(b))type='INTEGER';
   else if(['VARCHAR','CHAR','TEXT','LONGTEXT','MEDIUMTEXT','TINYTEXT','JSON'].includes(b))type='TEXT';
   else if(['DECIMAL','NUMERIC','FLOAT','DOUBLE','REAL'].includes(b))type='REAL';
   else if(['DATE','DATETIME','TIMESTAMP','TIME'].includes(b))type='TEXT';
   else if(['BINARY','VARBINARY','BLOB'].includes(b))type='BLOB';
 }
 const dimensions=length?(scale?`(${length},${scale})`:`(${length})`):'';
 return (engine==='sqlite'?type:(type==='VARCHAR'&&b==='TEXT'&&length?type:type+dimensions))+(suffix?' '+(engine==='sqlite'?suffix.replace(/\bUNSIGNED\b/gi,'').trim():suffix):'');
}
function parseProperty(prop){const text=String(prop.text||'').trim();const i=text.indexOf(':');if(i<1)throw Error('La propiedad «'+text+'» debe tener formato nombre: tipo');const name=text.slice(0,i).trim(),type=text.slice(i+1).trim();if(!name||!type)throw Error('Propiedad incompleta: '+text);return {id:prop.id,name,type};}
function generateSQL(engine){
 const q=s=>sqlIdentifier(s,engine),lines=[`-- Universo de entidades · ${engine==='mysql'?'MySQL':'SQLite'}`,`-- Proyecto: ${activeProject().name.replace(/[\r\n]/g,' ')}`,''];
 if(engine==='sqlite')lines.push('PRAGMA foreign_keys = ON;','');
 const schemas=data.entities.map(n=>({entity:n,cols:n.properties.map(parseProperty)}));
 const tables=new Set();for(const s of schemas){if(tables.has(s.entity.title.toLowerCase()))throw Error('Nombre de entidad duplicado: '+s.entity.title);tables.add(s.entity.title.toLowerCase());}
 const foreign=[];
 for(const s of schemas){
  if(!s.cols.length)throw Error('La entidad «'+s.entity.title+'» no tiene propiedades');
  const names=new Set(),cols=[];
  for(const c of s.cols){if(names.has(c.name.toLowerCase()))throw Error('Propiedad duplicada en '+s.entity.title+': '+c.name);names.add(c.name.toLowerCase());cols.push('  '+q(c.name)+' '+sqlType(c.type,engine));}
  const pk=s.cols.find(c=>c.name.toLowerCase()==='id');if(pk)cols.push('  PRIMARY KEY ('+q(pk.name)+')');
  if(engine==='sqlite')for(const link of data.links){const a=schemas.find(x=>x.entity.id===link.from);if(!a||link.to!==s.entity.id)continue;const ac=a.cols.find(c=>c.id===link.fromProp),bc=s.cols.find(c=>c.id===link.toProp);if(ac?.name.toLowerCase()==='id'&&bc)cols.push('  FOREIGN KEY ('+q(bc.name)+') REFERENCES '+q(a.entity.title)+' ('+q(ac.name)+')');}
  lines.push('CREATE TABLE '+(engine==='mysql'?'IF NOT EXISTS ':'IF NOT EXISTS ')+q(s.entity.title)+' (',cols.join(',\n'),')'+(engine==='mysql'?' ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;':';'),'');
 }
 // Enlaces entre propiedades se exportan como claves foráneas cuando el origen apunta a una columna id.
 for(const link of data.links){const a=schemas.find(s=>s.entity.id===link.from),b=schemas.find(s=>s.entity.id===link.to);if(!a||!b)continue;const ac=a.cols.find(c=>c.id===link.fromProp),bc=b.cols.find(c=>c.id===link.toProp);if(!ac||!bc||ac.name.toLowerCase()!=='id')continue;
  foreign.push({table:b.entity.title,col:bc.name,ref:a.entity.title,refCol:ac.name});
 }
 if(foreign.length){lines.push('-- Relaciones detectadas (id → propiedad vinculada)');for(const f of foreign){if(engine==='mysql')lines.push(`ALTER TABLE ${q(f.table)} ADD FOREIGN KEY (${q(f.col)}) REFERENCES ${q(f.ref)} (${q(f.refCol)});`);else lines.push(`-- ${q(f.table)}.${q(f.col)} → ${q(f.ref)}.${q(f.refCol)} (incluida en CREATE TABLE)`);}lines.push('');}
 return lines.join('\n');
}
function downloadText(content,filename,mime){const url=URL.createObjectURL(new Blob([content],{type:mime}));const a=document.createElement('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1500);}
document.querySelector('#exportSql').onclick=()=>{if(!data.entities.length){alert('Crea alguna entidad antes de exportar SQL.');return;}const engine=prompt('Motor SQL: escribe mysql o sqlite','mysql')?.trim().toLowerCase();if(!engine)return;if(!['mysql','sqlite'].includes(engine)){alert('Selecciona mysql o sqlite.');return;}try{const sql=generateSQL(engine),name=activeProject().name.replace(/[^a-z0-9_-]+/gi,'-')||'proyecto';downloadText(sql,`${name}-${engine}.sql`,'application/sql;charset=utf-8');}catch(err){alert('No se pudo exportar SQL: '+err.message);}};
document.querySelector('#import').onchange=async e=>{const f=e.target.files?.[0];if(!f)return;try{const d=JSON.parse(await f.text());if(!Array.isArray(d.entities)||!Array.isArray(d.links)||!d.entities.every(n=>typeof n.id==='string'&&typeof n.title==='string'&&Array.isArray(n.properties)&&Number.isFinite(n.x)&&Number.isFinite(n.y)))throw Error('Formato no válido');d.entities.forEach(n=>{n.properties=normalizeProps(n.properties);n.categories=normalizeCategories(n.categories);});d.links=d.links.filter(l=>l.fromProp&&l.toProp);data=d;selected=null;save();render();}catch(err){alert('No se pudo importar: '+err.message);}e.target.value='';};
document.querySelector('#clear').onclick=()=>{if(confirm('¿Eliminar todas las entidades y conexiones?')){data=empty();selected=null;save();render();}};
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&drag?.type==='link'){drag=null;drawWires();}if((e.key==='Delete'||e.key==='Backspace')&&!document.querySelector('#dataDialog').open&&!dialog.open&&selected&&!['INPUT','TEXTAREA'].includes(document.activeElement?.tagName)){data.entities=data.entities.filter(n=>n.id!==selected);data.links=data.links.filter(l=>l.from!==selected&&l.to!==selected);selected=null;save();render();}});
document.querySelector('#projectSelect').addEventListener('change',e=>{persist();store.activeId=e.target.value;loadProject();persist();});
document.querySelector('#newProject').onclick=()=>{const name=prompt('Nombre del nuevo proyecto:','Nuevo proyecto');if(!name?.trim())return;persist();const p=freshProject(name.trim());store.projects.push(p);store.activeId=p.id;loadProject();persist();};
document.querySelector('#renameProject').onclick=()=>{const p=activeProject();const name=prompt('Nuevo nombre del proyecto:',p.name);if(!name?.trim())return;p.name=name.trim();refreshProjectSelect();persist();};
document.querySelector('#deleteProject').onclick=()=>{if(store.projects.length===1)return;const p=activeProject();if(!confirm(`¿Eliminar el proyecto «${p.name}» y todas sus entidades y conexiones? Esta acción no se puede deshacer.`))return;store.projects=store.projects.filter(item=>item.id!==p.id);store.activeId=store.projects[0].id;loadProject();persist();};

// Registros por entidad. Las claves de cada fila son los identificadores estables de las propiedades.
const dataDialog=document.querySelector('#dataDialog');
let recordsEntityId=null;
const colName=p=>p.text.split(':')[0].trim();
// Las conexiones entre propiedades identifican referencias entre tablas.
// La columna vinculada a un identificador de otra entidad se edita con un desplegable.
function foreignReference(entityId,propId){
 for(const link of data.links){
  let sourceId,sourceProp;
  if(link.to===entityId&&link.toProp===propId){sourceId=link.from;sourceProp=link.fromProp;}
  else if(link.from===entityId&&link.fromProp===propId){sourceId=link.to;sourceProp=link.toProp;}
  else continue;
  const entity=find(sourceId),property=entity?.properties.find(p=>p.id===sourceProp);
  if(entity&&property&&colName(property).toLowerCase()==='id')return {entity,property};
 }
 return null;
}
function foreignLabel(entity,row,property){
 const value=String(row[property.id]??'');
 const descriptive=entity.properties.filter(p=>p.id!==property.id).map(p=>String(row[p.id]??'').trim()).find(Boolean);
 return descriptive?`${value} — ${descriptive}`:value;
}
function openRecords(id){recordsEntityId=id;renderRecords();dataDialog.showModal();}
function renderRecords(){
 const n=find(recordsEntityId);if(!n)return;
 n.rows ||= [];
 document.querySelector('#dataTitle').textContent='Datos · '+n.title;
 document.querySelector('#dataCount').textContent=n.rows.length+' registros · '+n.properties.length+' columnas';
 const head=document.querySelector('#dataTable thead'),body=document.querySelector('#dataTable tbody');
 head.replaceChildren();body.replaceChildren();
 const hr=document.createElement('tr');for(const prop of n.properties){const th=document.createElement('th');th.textContent=colName(prop);th.title=prop.text;hr.append(th);}const actions=document.createElement('th');actions.textContent='Acciones';hr.append(actions);head.append(hr);
 n.rows.forEach((row,index)=>{const tr=document.createElement('tr');for(const prop of n.properties){const td=document.createElement('td'),ref=foreignReference(n.id,prop.id);
 let input;
 if(ref){
  input=document.createElement('select');input.className='foreign-select';
  const blank=document.createElement('option');blank.value='';blank.textContent='— Sin seleccionar —';input.append(blank);
  const current=String(row[prop.id]??'');let matched=current==='';
  for(const foreignRow of (ref.entity.rows||[])){
   const value=String(foreignRow[ref.property.id]??'').trim();if(!value)continue;
   const option=document.createElement('option');option.value=value;option.textContent=foreignLabel(ref.entity,foreignRow,ref.property);
   if(value===current)matched=true;input.append(option);
  }
  if(!matched){const missing=document.createElement('option');missing.value=current;missing.textContent=current+' (registro no encontrado)';input.append(missing);}
  input.value=current;input.title='Clave foránea → '+ref.entity.title+'.'+colName(ref.property);
 }else{
  input=document.createElement('input');input.type='text';input.value=row[prop.id]??'';
  input.placeholder=prop.text.includes(':')?prop.text.split(':').slice(1).join(':').trim():'';
 }
 input.dataset.row=String(index);input.dataset.prop=prop.id;
 input.setAttribute('aria-label',colName(prop)+' · fila '+(index+1));td.append(input);tr.append(td);}const td=document.createElement('td'),del=document.createElement('button');del.type='button';del.className='delete-row';del.textContent='Eliminar';del.dataset.deleteRow=String(index);td.append(del);tr.append(td);body.append(tr);});
 if(!n.rows.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=n.properties.length+1;td.className='empty-data';td.textContent='Todavía no hay registros. Pulsa «Añadir registro».';tr.append(td);body.append(tr);}
}
document.querySelector('#addRow').onclick=()=>{const n=find(recordsEntityId);if(!n)return;n.rows ||= [];n.rows.push({});save();renderRecords();const last=document.querySelector('#dataTable tbody tr:last-child input');last?.focus();};
document.querySelector('#closeData').onclick=()=>dataDialog.close();
document.querySelector('#dataTable').addEventListener('input',e=>{const input=e.target.closest('input[data-row]');if(!input)return;const n=find(recordsEntityId),row=n?.rows?.[Number(input.dataset.row)];if(!row)return;row[input.dataset.prop]=input.value;save();});
document.querySelector('#dataTable').addEventListener('click',e=>{const btn=e.target.closest('[data-delete-row]');if(!btn)return;const n=find(recordsEntityId);if(!n)return;n.rows.splice(Number(btn.dataset.deleteRow),1);save();renderRecords();});
document.querySelector('#dataTable').addEventListener('change',e=>{
 const input=e.target.closest('select[data-row]');if(!input)return;
 const n=find(recordsEntityId),row=n?.rows?.[Number(input.dataset.row)];if(!row)return;
 row[input.dataset.prop]=input.value;save();
});
dataDialog.addEventListener('close',()=>{recordsEntityId=null;render();});

window.addEventListener('resize',drawWires);
async function boot(){try{const response=await fetch('api/index.php?action=load');const result=await response.json();if(!result.ok)throw Error(result.error);if(result.store.projects.length){store=result.store;}else{document.querySelector('#syncStatus').textContent='Proyecto inicial';}for(const p of store.projects)for(const n of p.data.entities){n.properties=normalizeProps(n.properties);n.categories=normalizeCategories(n.categories);}loadProject();save();}catch(err){document.querySelector('#syncStatus').textContent='Sin conexión: '+err.message;loadProject();}}
boot();
})();
