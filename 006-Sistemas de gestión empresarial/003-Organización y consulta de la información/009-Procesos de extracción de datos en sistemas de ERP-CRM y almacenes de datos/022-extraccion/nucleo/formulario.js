class DarkorangeFormulario {
  constructor({contenedor, tabla, columnas, api="api/superapi.php", alGuardar=null}) {
    this.contenedor = typeof contenedor === "string" ? document.querySelector(contenedor) : contenedor;
    this.tabla = tabla;
    this.columnas = columnas || [];
    this.api = api;
    this.alGuardar = alGuardar;
    this.formulario = null;
  }

  tipoInput(columna) {
    const nombre = columna.name.toLowerCase();
    const tipo = (columna.type || "").toUpperCase();
    if (nombre.includes("email")) return "email";
    if (nombre.includes("telefono") || nombre.includes("teléfono")) return "tel";
    if (nombre.includes("fecha") || tipo.includes("DATE")) return "date";
    if (tipo.includes("INT") || tipo.includes("REAL") || tipo.includes("NUM") ||
        tipo.includes("DECIMAL") || tipo.includes("FLOAT") || tipo.includes("DOUBLE")) return "number";
    return "text";
  }

  render() {
    this.contenedor.innerHTML = "";

    const titulo = document.createElement("h3");
    titulo.textContent = "Nuevo registro";
    this.contenedor.appendChild(titulo);

    const form = document.createElement("form");
    form.className = "componente-formulario";

    this.columnas.forEach(columna => {
      // La PK/id autogenerada no forma parte del CREATE.
      if (columna.pk || columna.name === "id") return;

      const control = document.createElement("div");
      control.className = "control";

      const label = document.createElement("label");
      label.textContent = columna.name;
      label.htmlFor = "campo_" + columna.name;

      const input = document.createElement("input");
      input.type = this.tipoInput(columna);
      input.name = columna.name;
      input.id = "campo_" + columna.name;
      input.placeholder = columna.name;
      if (input.type === "number") input.step = "any";

      control.append(label, input);
      form.appendChild(control);
    });

    const boton = document.createElement("button");
    boton.type = "submit";
    boton.textContent = "Guardar";
    form.appendChild(boton);

    form.addEventListener("submit", evento => this.guardar(evento));
    this.contenedor.appendChild(form);
    this.formulario = form;
    return form;
  }

  async guardar(evento) {
    evento.preventDefault();
    const datos = Object.fromEntries(new FormData(this.formulario).entries());

    const respuesta = await fetch(this.api + "?ruta=crear", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({tabla: this.tabla, datos})
    });
    const resultado = await respuesta.json();
    if (!respuesta.ok || resultado.ok === false) {
      throw new Error(resultado.error || "No se pudo guardar el registro");
    }

    this.formulario.reset();
    if (this.alGuardar) await this.alGuardar(resultado);
  }
}
