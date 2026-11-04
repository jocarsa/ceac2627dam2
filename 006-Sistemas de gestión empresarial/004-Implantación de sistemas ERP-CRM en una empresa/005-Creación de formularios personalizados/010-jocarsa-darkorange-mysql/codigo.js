let tablaActual='';
const api=(ruta,tabla='')=>'api/index.php?'+new URLSearchParams({ruta,...(tabla?{tabla}:{})});
async function obtener(ruta,tabla=''){const r=await fetch(api(ruta,tabla));const j=await r.json();if(!r.ok||j.ok===false)throw Error(j.error||'Error de API');return j}
async function cargarVista(ruta,tabla=''){
 const zona=document.querySelector('main section');zona.innerHTML='<p class="vacio">Cargando…</p>';
 try{const datos=await obtener(ruta,tabla);zona.innerHTML=datos.html;if(ruta==='tabla'){
  const form=await obtener('formulario',tabla);const cont=document.createElement('div');cont.innerHTML=form.html;zona.prepend(cont);
  const formulario=cont.querySelector('form');formulario.addEventListener('submit',async e=>{e.preventDefault();try{const respuesta=await fetch(formulario.action,{method:'POST',body:new FormData(formulario)});const j=await respuesta.json();if(!respuesta.ok||!j.ok)throw Error(j.error||'Error al guardar');await cargarVista('tabla',tabla)}catch(err){alert(err.message)}});
 }}catch(e){zona.textContent='Error: '+e.message}
}
async function iniciar(){const entidades=await obtener('entidades');const mod=document.querySelector('#modulos'),menu=document.querySelector('#entidades');mod.innerHTML='';menu.innerHTML='';
 for(const [nombre,ruta] of [['Dashboard','dashboard'],['Reporting','reporting']]){const a=document.createElement('a');a.href='#';a.textContent=nombre;a.onclick=e=>{e.preventDefault();cargarVista(ruta)};mod.append(a)}
 for(const tabla of entidades){const a=document.createElement('a');a.href='#';a.textContent=tabla;a.onclick=e=>{e.preventDefault();tablaActual=tabla;menu.querySelectorAll('a').forEach(x=>x.classList.remove('activo'));a.classList.add('activo');cargarVista('tabla',tabla)};menu.append(a)}
 document.querySelector('#boton-reporting').onclick=()=>cargarVista('reporting');await cargarVista('dashboard');
}
iniciar().catch(e=>document.querySelector('main section').textContent=e.message);
