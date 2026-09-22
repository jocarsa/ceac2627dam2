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
  
  seccion.innerHTML += "</tr>";
  seccion.innerHTML += "</table>";
})