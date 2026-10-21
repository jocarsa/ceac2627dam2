let tablaActual = "";

fetch("data/config.php")
.then(r => r.json())
.then(datos => {
  document.querySelector("h1").textContent = datos.nombre;
  document.documentElement.style.setProperty("--color_corporativo", datos.color);
});

fetch("api/superapi.php?ruta=modulos")
.then(r => r.json())
.then(datos => {
  const menu = document.querySelector("#modulos");
  datos.forEach(dato => {
    const a = document.createElement("a");
    a.href = "#";
    a.textContent = dato;
    menu.appendChild(a);
  });
});

fetch("api/superapi.php?ruta=entidades")
.then(r => r.json())
.then(datos => {
  const menu = document.querySelector("#entidades");
  datos.forEach(tabla => {
    const a = document.createElement("a");
    a.href = "#";
    a.textContent = tabla;
    a.onclick = evento => {
      evento.preventDefault();
      document.querySelectorAll("#entidades a").forEach(x => x.classList.remove("activo"));
      a.classList.add("activo");
      cargarEntidad(tabla);
    };
    menu.appendChild(a);
  });
});

async function cargarEntidad(tabla) {
  tablaActual = tabla;
  const respuesta = await fetch("api/superapi.php?ruta=tabla&tabla=" + encodeURIComponent(tabla));
  const datos = await respuesta.json();

  const seccion = document.querySelector("section");
  seccion.innerHTML = `
    <div class="barra">
      <div><small>ENTIDAD</small><h2></h2></div>
    </div>
    <div id="zona-formulario"></div>
    <div id="zona-tabla"></div>
  `;
  seccion.querySelector("h2").textContent = tabla;

  new DarkorangeFormulario({
    contenedor: "#zona-formulario",
    tabla,
    columnas: datos.columnas,
    alGuardar: () => cargarEntidad(tabla)
  }).render();

  new DarkorangeTabla({
    contenedor: "#zona-tabla",
    tabla,
    columnas: datos.columnas,
    registros: datos.registros
  }).render();
}
