function grafica(elemento){
      	let datos = elemento.getAttribute("data")
        console.log(datos)
        datos = eval(datos)
        console.log(datos)
        let contenedor = elemento
        datos.forEach(function(dato){
          contenedor.innerHTML += `
            <div class="barra" style="height:`+dato+`px;">
              `+dato+`
            </div>`;
        })
      }