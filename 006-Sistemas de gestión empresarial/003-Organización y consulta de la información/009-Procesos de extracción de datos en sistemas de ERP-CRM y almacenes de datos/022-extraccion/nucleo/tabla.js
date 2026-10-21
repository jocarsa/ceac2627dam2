class DarkorangeTabla {
  constructor({contenedor, tabla, columnas, registros}) {
    this.contenedor = typeof contenedor === "string" ? document.querySelector(contenedor) : contenedor;
    this.tabla = tabla;
    this.columnas = columnas || [];
    this.registros = registros || [];
  }

  render() {
    this.contenedor.innerHTML = "";

    const titulo = document.createElement("h3");
    titulo.textContent = "Listado de " + this.tabla;
    const cabecera = document.createElement('div');
    cabecera.className = 'barra';
    const botonCSV = document.createElement('button');
    botonCSV.type = 'button';
    botonCSV.textContent = 'Exportar CSV';
    botonCSV.onclick = () => DarkorangeCSV.descargar(this.tabla, this.columnas, this.registros);
    cabecera.append(titulo, botonCSV);
    this.contenedor.appendChild(cabecera);

    if (!this.columnas.length) {
      this.contenedor.innerHTML += '<p class="vacio">No hay columnas.</p>';
      return;
    }

    const envoltorio = document.createElement("div");
    envoltorio.className = "tabla-contenedor";
    const table = document.createElement("table");
    const thead = document.createElement("thead");
    const tbody = document.createElement("tbody");

    const trh = document.createElement("tr");
    this.columnas.forEach(columna => {
      const th = document.createElement("th");
      th.textContent = columna.name;
      trh.appendChild(th);
    });
    thead.appendChild(trh);

    this.registros.forEach(registro => {
      const tr = document.createElement("tr");
      this.columnas.forEach(columna => {
        const td = document.createElement("td");
        td.textContent = registro[columna.name] ?? "";
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });

    table.append(thead, tbody);
    envoltorio.appendChild(table);
    this.contenedor.appendChild(envoltorio);

    if (!this.registros.length) {
      const vacio = document.createElement("p");
      vacio.className = "vacio";
      vacio.textContent = "Todavía no hay registros.";
      this.contenedor.appendChild(vacio);
    }
    const campo=DarkorangeGraficas.campo(this.registros,this.columnas);
    if(campo&&this.registros.length){const panel=document.createElement('div');panel.className='grafica-card grafica-tabla';this.contenedor.prepend(panel);const frec=DarkorangeGraficas.frecuencia(this.registros,campo.name);DarkorangeGraficas.crear(panel,'barras',frec.map(x=>x[0]),frec.map(x=>x[1]),'Frecuencia de '+campo.name)}
    return table;
  }
}
