onmessage = function(datos){

  let x = datos.data.x
  let y = datos.data.y
  let ancho = datos.data.ancho
  let alto = datos.data.alto
  let pixeles = datos.data.pixeles

  // El worker procesa el negativo
  for(let i = 0;i<pixeles.length;i+=4){

    pixeles[i] = 255-pixeles[i]
    pixeles[i+1] = 255-pixeles[i+1]
    pixeles[i+2] = 255-pixeles[i+2]

  }

  // Devuelvo el resultado
  postMessage({
    x:x,
    y:y,
    ancho:ancho,
    alto:alto,
    pixeles:pixeles
  })
}