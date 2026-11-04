class DarkorangeCSV {
  static descargar(nombre, columnas, registros) {
    const campos = columnas.map(c => typeof c === 'string' ? c : c.name);
    const escapar = valor => {
      let texto = String(valor ?? '');
      // Evitar que Excel interprete contenido de la base de datos como fórmulas.
      if (/^[\s\x00-\x1f]*[=+@-]/.test(texto) && !/^-?\d+(?:[.,]\d+)?$/.test(texto.trim())) texto = "'" + texto;
      return '"' + texto.replace(/"/g, '""') + '"';
    };
    const lineas = [campos.map(escapar).join(';'), ...registros.map(fila => campos.map(c => escapar(fila[c])).join(';'))];
    const blob = new Blob(['\uFEFF', lineas.join('\r\n')], {type:'text/csv;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.download = String(nombre).replace(/[^a-zA-Z0-9_-]/g, '_') + '.csv';
    document.body.appendChild(enlace);
    enlace.click(); enlace.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
}
