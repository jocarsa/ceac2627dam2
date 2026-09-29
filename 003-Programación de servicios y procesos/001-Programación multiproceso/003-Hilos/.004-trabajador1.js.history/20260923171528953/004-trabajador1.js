onmessage = function(datos){
  console.log("Yo soy el trabajador y los datos que he recibido son:")
	postMessage(datos.data)
}