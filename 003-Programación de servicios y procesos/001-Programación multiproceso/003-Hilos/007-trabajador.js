// Radio del Gaussian Blur
// 2 = ligero
// 5 = medio
// 10 = fuerte y bastante más costoso
const RADIO = 16

onmessage = function(datos){

  let x = datos.data.x
  let y = datos.data.y
  let ancho = datos.data.ancho
  let alto = datos.data.alto
  let pixeles = datos.data.pixeles

  // Creo una copia para no modificar los píxeles
  // mientras todavía los estoy utilizando
  let original = new Uint8ClampedArray(pixeles)

  // Recorro todos los píxeles
  for(let py = 0; py < alto; py++){

    for(let px = 0; px < ancho; px++){

      let rojo = 0
      let verde = 0
      let azul = 0
      let pesoTotal = 0

      // Recorro los píxeles vecinos
      for(let dy = -RADIO; dy <= RADIO; dy++){

        for(let dx = -RADIO; dx <= RADIO; dx++){

          let vecinoX = px + dx
          let vecinoY = py + dy

          // Compruebo límites del bucket
          if(
            vecinoX >= 0 &&
            vecinoX < ancho &&
            vecinoY >= 0 &&
            vecinoY < alto
          ){

            // Distancia al píxel central
            let distancia = dx*dx + dy*dy

            // Peso gaussiano
            let sigma = RADIO / 2

            let peso = Math.exp(
              -distancia / (2*sigma*sigma)
            )

            let posicion = (vecinoY*ancho + vecinoX)*4

            rojo += original[posicion] * peso
            verde += original[posicion+1] * peso
            azul += original[posicion+2] * peso

            pesoTotal += peso
          }
        }
      }

      let posicion = (py*ancho + px)*4

      pixeles[posicion] = rojo / pesoTotal
      pixeles[posicion+1] = verde / pesoTotal
      pixeles[posicion+2] = azul / pesoTotal

      // Mantengo el alpha
      pixeles[posicion+3] = original[posicion+3]
    }
  }

  postMessage({
    x:x,
    y:y,
    ancho:ancho,
    alto:alto,
    pixeles:pixeles
  })
}