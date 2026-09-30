onmessage = function(datos){
  // El worker es quien procesa el negativo
	for(let i = 0;i<datos.data.length;i+=4){
  	datos.data[i] = 255-datos.data[i];
    datos.data[i+1] = 255-datos.data[i+1];
    datos.data[i+2] = 255-datos.data[i+2];
  }
  postMessage(datos.data)
}