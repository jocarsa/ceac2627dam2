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
  seccion.innerHTML += "<tr>";
  datos.clientes[0].forEach(columna){
  	seccion.innerHTML += "<th>"+columna+"</th>";
  }
  seccion.innerHTML += "</tr>";
  seccion.innerHTML += "</table>";
})