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