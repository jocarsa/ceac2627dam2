// Vamos a cargar la configuración
fetch("data/config.php")
.then(function(respuesta){return respuesta.json()})
.then(function(datos){
  console.log("Los datos son")
	console.log(datos)
  let titulo = document.querySelector("h1")
  titulo.textContent = datos.nombre
  let cabecera = document.querySelector("header")
  let navegacion1 = document.querySelector("#modulos")
  let navegacion2 = document.querySelector("#entidades")
  // Esto le cambia el color a la variable css
  document.documentElement.style.setProperty('--color_corporativo', datos.color);
})

fetch("api/superapi.php?ruta=modulos")
.then(function(respuesta){return respuesta.json()})
.then(function(datos){
	console.log(datos)
  let menu = document.querySelector("#modulos")
  datos.forEach(function(dato){
  	menu.innerHTML += '<a href="">'+dato+'</a>'
  })
})

fetch("api/superapi.php?ruta=entidades")
.then(function(respuesta){return respuesta.json()})
.then(function(datos){
	console.log(datos)
  let menu = document.querySelector("#entidades")
  datos.forEach(function(dato){
  	menu.innerHTML += '<a href="">'+dato+'</a>'
  })
})

fetch("api/superapi.php?ruta=tabla")
.then(function(respuesta){return respuesta.json()})
.then(function(datos){
	console.log(datos)
 	let seccion = document.querySelector("section")
  let cadenatabla = ""
  cadenatabla += "<table>";
  // Primero pinto las cabeceras de columna
  cadenatabla += "<tr>";
  Object.keys(datos.clientes[0]).forEach(function(clave){
  	cadenatabla += "<th>"+clave+"</th>";
  })
  cadenatabla += "</tr>";
  // Primero pinto las cabeceras de columna
  // Ahora pinto el cuerpo de la tabla
  
  datos.clientes.forEach(function(cliente){
    cadenatabla += "<tr>";
  	Object.keys(cliente).forEach(function(clave){
      cadenatabla += "<td>"+cliente[clave]+"</td>";
    });
    cadenatabla += "</tr>";
  })
  
  // Ahora pinto el cuerpo de la tabla
  cadenatabla += "</table>";
  seccion.innerHTML = cadenatabla
})

