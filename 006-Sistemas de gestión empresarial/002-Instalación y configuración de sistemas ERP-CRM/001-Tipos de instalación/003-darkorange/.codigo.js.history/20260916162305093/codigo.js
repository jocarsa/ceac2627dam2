fetch("api/superapi.php?ruta=entidades")
.then(function(respuesta){return respuesta.json()})
.then(function(datos){
	console.log(datos)
  let menu = document.querySelector("nav")
  datos.forEach(function(dato){
  	menu.innerHTML += '<a href="">'+dato+'</a>'
  })
})

fetch("api/superapi.php?ruta=tabla")
.then(function(respuesta){return respuesta.json()})
.then(function(datos){
	console.log(datos)
 	let seccion = document.querySelector("section")
  seccion.innerHTML += "<table>";
  // Primero pinto las cabeceras de columna
  seccion.innerHTML += "<tr>";
  datos.clientes[0].forEach(function(columna){
  	seccion.innerHTML += "<th>"+columna+"</th>";
  })
  seccion.innerHTML += "</tr>";
  // Primero pinto las cabeceras de columna
  seccion.innerHTML += "</table>";
})