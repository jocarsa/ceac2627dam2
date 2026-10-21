class DarkorangeReporting {
  constructor({contenedor="section", api="api/superapi.php"} = {}) {
    this.contenedor = typeof contenedor === "string" ? document.querySelector(contenedor) : contenedor;
    this.api = api;
  }

  esNumerica(columna) {
    const tipo = (columna.type || "").toUpperCase();
    return ["INT","REAL","NUM","DECIMAL","FLOAT","DOUBLE"].some(t => tipo.includes(t));
  }

  formatoNumero(valor) {
    return new Intl.NumberFormat("es-ES", {maximumFractionDigits:2}).format(valor);
  }

  async cargarTodo() {
    const tablas = await fetch(this.api + "?ruta=entidades").then(r => r.json());
    return Promise.all(tablas.map(tabla =>
      fetch(this.api + "?ruta=tabla&tabla=" + encodeURIComponent(tabla)).then(r => r.json())
    ));
  }

  async render() {
    this.contenedor.innerHTML = '<div class="vacio">Generando informe completo…</div>';
    const entidades = await this.cargarTodo();
    const totalRegistros = entidades.reduce((s,e) => s + e.registros.length, 0);
    const fecha = new Intl.DateTimeFormat("es-ES", {dateStyle:"long", timeStyle:"short"}).format(new Date());

    this.contenedor.innerHTML = `
      <div class="reporting-toolbar">
        <div><strong>Reporting</strong><small> ${entidades.length} tablas · ${totalRegistros} registros</small></div>
        <button type="button" id="reporting-imprimir">Imprimir / PDF</button>
      </div>
      <div class="reporting-documento">
        <article class="reporting-a4">
          <header class="reporting-cabecera">
            <div><small>JOCARSA · DARKORANGE</small><h1>Reporte general</h1></div>
            <div class="reporting-fecha">${fecha}</div>
          </header>
          <div class="reporting-resumen">
            <div><strong>${entidades.length}</strong><span>tablas</span></div>
            <div><strong>${totalRegistros}</strong><span>registros</span></div>
          </div>
          <div id="reporting-tablas"></div>
        </article>
      </div>`;

    const zona = this.contenedor.querySelector("#reporting-tablas");
    entidades.forEach(entidad => zona.appendChild(this.crearTabla(entidad)));
    this.contenedor.querySelector("#reporting-imprimir").onclick = () => window.print();
  }

  crearTabla(datos) {
    const bloque = document.createElement("section");
    bloque.className = "reporting-bloque";
    const numericas = datos.columnas.map((c,i) => this.esNumerica(c) ? i : -1).filter(i => i >= 0);

    bloque.innerHTML = `
      <div class="reporting-titulo-tabla">
        <div><small>TABLA</small><h2>${this.esc(datos.tabla)}</h2></div>
        <span class="reporting-contador">${datos.registros.length} filas</span>
      </div>
      <div class="reporting-tabla-scroll"><table><thead></thead><tbody></tbody><tfoot></tfoot></table></div>`;

    const thead = bloque.querySelector("thead");
    const filtros = document.createElement("tr");
    filtros.className = "reporting-filtros";
    const nombres = document.createElement("tr");
    datos.columnas.forEach((columna, indice) => {
      const thf = document.createElement("th");
      const input = document.createElement("input");
      input.type = "search"; input.placeholder = "Filtrar"; input.dataset.indice = indice;
      thf.appendChild(input); filtros.appendChild(thf);

      const th = document.createElement("th");
      th.textContent = columna.name; th.dataset.indice = indice; th.dataset.asc = "1";
      nombres.appendChild(th);
    });
    thead.append(filtros, nombres);

    const tbody = bloque.querySelector("tbody");
    datos.registros.forEach(registro => {
      const tr = document.createElement("tr");
      datos.columnas.forEach(c => { const td=document.createElement("td"); td.textContent=registro[c.name] ?? ""; tr.appendChild(td); });
      tbody.appendChild(tr);
    });

    const actualizar = () => {
      const inputs = [...bloque.querySelectorAll("thead input")];
      const visibles = [...tbody.rows].filter(fila => {
        const ok = inputs.every((input,i) => fila.cells[i].textContent.toLowerCase().includes(input.value.toLowerCase().trim()));
        fila.style.display = ok ? "" : "none"; return ok;
      });
      bloque.querySelector(".reporting-contador").textContent = visibles.length + " filas";
      this.resumen(bloque, datos.columnas, visibles, numericas);
    };

    bloque.querySelectorAll("thead input").forEach(i => i.oninput = actualizar);
    nombres.querySelectorAll("th").forEach(th => th.onclick = () => {
      const i = +th.dataset.indice, asc = th.dataset.asc === "1";
      [...tbody.rows].sort((a,b) => {
        let A=a.cells[i].textContent.trim(), B=b.cells[i].textContent.trim();
        if (numericas.includes(i)) { A=parseFloat(A)||0; B=parseFloat(B)||0; return asc ? A-B : B-A; }
        return asc ? A.localeCompare(B,"es",{numeric:true}) : B.localeCompare(A,"es",{numeric:true});
      }).forEach(f => tbody.appendChild(f));
      th.dataset.asc = asc ? "0" : "1";
    });
    actualizar();
    return bloque;
  }

  resumen(bloque, columnas, filas, numericas) {
    const tfoot = bloque.querySelector("tfoot"); tfoot.innerHTML = "";
    if (!numericas.length) return;
    for (const [etiqueta, promedio] of [["Suma",false],["Promedio",true]]) {
      const tr=document.createElement("tr");
      columnas.forEach((c,i) => {
        const td=document.createElement("td");
        if (i===0) { td.textContent=etiqueta; td.className="reporting-resumen-label"; }
        if (numericas.includes(i)) {
          const valores=filas.map(f=>parseFloat(f.cells[i].textContent)).filter(Number.isFinite);
          const suma=valores.reduce((a,b)=>a+b,0);
          td.textContent=this.formatoNumero(promedio ? (valores.length ? suma/valores.length : 0) : suma);
          td.classList.add("numero");
        }
        tr.appendChild(td);
      }); tfoot.appendChild(tr);
    }
  }

  esc(v) { const d=document.createElement("div"); d.textContent=v; return d.innerHTML; }
}
