class DarkorangeDashboard {
 constructor(contenedor='section'){this.contenedor=document.querySelector(contenedor)}
 async render(){const zona=this.contenedor;zona.innerHTML='<div class="vacio">Cargando dashboard…</div>';try{
 const nombres=await fetch('api/superapi.php?ruta=entidades').then(r=>r.json());const entidades=await Promise.all(nombres.map(async n=>{const r=await fetch('api/superapi.php?ruta=tabla&tabla='+encodeURIComponent(n));return r.json()}));
 const total=entidades.reduce((a,e)=>a+e.registros.length,0);
 zona.innerHTML=`<div class="barra"><div><small>VISIÓN GENERAL · DEMOSTRACIÓN</small><h2>Dashboard</h2></div><span class="demo-aviso">Indicadores simulados</span></div><div class="dashboard-kpis"><div><small>Ingresos estimados</small><strong>2,48 M€</strong><span>↑ 12,8% ficticio</span></div><div><small>Operaciones mensuales</small><strong>1.284</strong><span>↑ 8,4% ficticio</span></div><div><small>Satisfacción</small><strong>94,2%</strong><span>Datos de muestra</span></div><div><small>Registros reales</small><strong>${total}</strong><span>${entidades.length} entidades</span></div></div><div class="dashboard-grid"><div class="grafica-card" id="dg1"></div><div class="grafica-card" id="dg2"></div><div class="grafica-card" id="dg3"></div><div class="grafica-card" id="dg4"></div></div>`;
 DarkorangeGraficas.crear('#dg1','barras',['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago'],[42,54,49,67,74,70,86,98],'Evolución comercial · simulación');
 DarkorangeGraficas.crear('#dg2','anillo',['Ventas','Servicios','Otros'],[58,29,13],'Distribución de ingresos · simulación');
 DarkorangeGraficas.crear('#dg3','tarta',entidades.map(e=>e.tabla),entidades.map(e=>e.registros.length),'Registros por entidad · datos reales');
 const pedidos=entidades.find(e=>e.tabla==='pedidos');const f=pedidos?DarkorangeGraficas.frecuencia(pedidos.registros,'estado'):[];
 DarkorangeGraficas.crear('#dg4','barras',f.length?f.map(x=>x[0]):['Pendiente','Activo','Finalizado'],f.length?f.map(x=>x[1]):[14,26,35],f.length?'Pedidos por estado · datos reales':'Estados operativos · simulación');
 }catch(e){zona.textContent='No se pudo cargar el dashboard: '+e.message}}
}
