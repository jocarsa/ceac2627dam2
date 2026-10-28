let tablaActual='', proyectoActual=localStorage.getItem('darkorange-proyecto')||'';
const api=(ruta,params={})=>'api/superapi.php?'+new URLSearchParams({ruta,proyecto:proyectoActual,...params});
async function get(ruta,params={}){const r=await fetch(api(ruta,params));const j=await r.json();if(!r.ok||j.ok===false)throw Error(j.error||'Error de API');return j;}
async function iniciar(){
 const proyectos=await get('proyectos');
 if(!proyectos.some(p=>p.id===proyectoActual))proyectoActual=proyectos[0]?.id||'';
 const sel=document.createElement('select');sel.id='selector-proyecto';
 for(const p of proyectos){const o=document.createElement('option');o.value=p.id;o.textContent=p.name;sel.append(o)}
 sel.value=proyectoActual;sel.onchange=()=>{localStorage.setItem('darkorange-proyecto',sel.value);location.reload()};
 document.querySelector('header').prepend(sel);
 const config=await fetch('data/config.php').then(r=>r.json()).catch(()=>({nombre:'jocarsa | darkorange',color:'darkorange'}));
 document.querySelector('h1').textContent=config.nombre||'jocarsa | darkorange';
 document.documentElement.style.setProperty('--color_corporativo',config.color||'darkorange');
 const modulos=await get('modulos'),entidades=await get('entidades');
 const menuMod=document.querySelector('#modulos'),menuEnt=document.querySelector('#entidades');
 function mostrar(tables){menuEnt.replaceChildren();for(const tabla of tables){const a=document.createElement('a');a.href='#';a.textContent=tabla;a.onclick=e=>{e.preventDefault();menuEnt.querySelectorAll('a').forEach(x=>x.classList.remove('activo'));a.classList.add('activo');cargarEntidad(tabla)};menuEnt.append(a)}}
 const todos=document.createElement('a');todos.href='#';todos.textContent='Todas las entidades';todos.onclick=e=>{e.preventDefault();mostrar(entidades)};menuMod.append(todos);
 for(const [nombre,tablas] of Object.entries(modulos)){const a=document.createElement('a');a.href='#';a.textContent=nombre;a.onclick=e=>{e.preventDefault();menuMod.querySelectorAll('a').forEach(x=>x.classList.remove('activo'));a.classList.add('activo');mostrar(tablas)};menuMod.append(a)}
 mostrar(entidades);
 document.querySelector('#boton-reporting').onclick=()=>new DarkorangeReporting({contenedor:'section'}).render();
 const dash=document.createElement('a');dash.href='#';dash.textContent='Dashboard';dash.onclick=e=>{e.preventDefault();new DarkorangeDashboard().render()};menuMod.prepend(dash);
 new DarkorangeDashboard().render();
}
async function cargarEntidad(tabla){
 tablaActual=tabla;const datos=await get('tabla',{tabla}),relaciones=await get('relaciones',{tabla});
 const seccion=document.querySelector('section');seccion.innerHTML='<div class="barra"><div><small>ENTIDAD</small><h2></h2></div></div><div id="zona-formulario"></div><div id="zona-tabla"></div>';
 seccion.querySelector('h2').textContent=tabla;
 new DarkorangeFormulario({contenedor:'#zona-formulario',tabla,columnas:datos.columnas,api:api('crear'),relaciones,alGuardar:()=>cargarEntidad(tabla)}).render();
 new DarkorangeTabla({contenedor:'#zona-tabla',tabla,columnas:datos.columnas,registros:datos.registros}).render();
}
iniciar().catch(e=>{document.querySelector('section').textContent='Error de conexión: '+e.message;console.error(e)});
