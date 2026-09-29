onmessage = function(datos){
  console.log(datos)
	postMessage("He recibido el mensaje del jefe y le digo algo")
}