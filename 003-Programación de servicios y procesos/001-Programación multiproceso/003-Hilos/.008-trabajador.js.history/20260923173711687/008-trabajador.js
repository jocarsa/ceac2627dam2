const RADIO = 16


onmessage = function(datos){

  let x = datos.data.x
  let y = datos.data.y

  let ancho = datos.data.ancho
  let alto = datos.data.alto

  let pixeles = datos.data.pixeles

  let filtro = datos.data.filtro


  // Selecciono algoritmo

  if(filtro == "negativo"){
    negativo(pixeles)
  }

  if(filtro == "grises"){
    grises(pixeles)
  }

  if(filtro == "sepia"){
    sepia(pixeles)
  }

  if(filtro == "brillo"){
    brillo(pixeles)
  }

  if(filtro == "contraste"){
    contraste(pixeles)
  }

  if(filtro == "posterizar"){
    posterizar(pixeles)
  }

  if(filtro == "pixelar"){
    pixelar(pixeles,ancho,alto)
  }

  if(filtro == "gaussian"){
    gaussian(pixeles,ancho,alto)
  }

  if(filtro == "bordes"){
    bordes(pixeles,ancho,alto)
  }


  postMessage({

    x:x,
    y:y,

    ancho:ancho,
    alto:alto,

    pixeles:pixeles

  })

}



// ============================================
// NEGATIVO
// ============================================

function negativo(pixeles){

  for(let i = 0;i < pixeles.length;i += 4){

    pixeles[i]   = 255-pixeles[i]
    pixeles[i+1] = 255-pixeles[i+1]
    pixeles[i+2] = 255-pixeles[i+2]

  }

}



// ============================================
// ESCALA DE GRISES
// ============================================

function grises(pixeles){

  for(let i = 0;i < pixeles.length;i += 4){

    let gris =
      pixeles[i]*0.299 +
      pixeles[i+1]*0.587 +
      pixeles[i+2]*0.114

    pixeles[i] = gris
    pixeles[i+1] = gris
    pixeles[i+2] = gris

  }

}



// ============================================
// SEPIA
// ============================================

function sepia(pixeles){

  for(let i = 0;i < pixeles.length;i += 4){

    let r = pixeles[i]
    let g = pixeles[i+1]
    let b = pixeles[i+2]

    pixeles[i] =
      r*0.393 +
      g*0.769 +
      b*0.189

    pixeles[i+1] =
      r*0.349 +
      g*0.686 +
      b*0.168

    pixeles[i+2] =
      r*0.272 +
      g*0.534 +
      b*0.131

  }

}



// ============================================
// BRILLO
// ============================================

function brillo(pixeles){

  let cantidad = 50

  for(let i = 0;i < pixeles.length;i += 4){

    pixeles[i] += cantidad
    pixeles[i+1] += cantidad
    pixeles[i+2] += cantidad

  }

}



// ============================================
// CONTRASTE
// ============================================

function contraste(pixeles){

  let contraste = 80

  let factor =
    (259*(contraste+255)) /
    (255*(259-contraste))

  for(let i = 0;i < pixeles.length;i += 4){

    pixeles[i] =
      factor*(pixeles[i]-128)+128

    pixeles[i+1] =
      factor*(pixeles[i+1]-128)+128

    pixeles[i+2] =
      factor*(pixeles[i+2]-128)+128

  }

}



// ============================================
// POSTERIZAR
// ============================================

function posterizar(pixeles){

  let niveles = 4

  let salto = 255/(niveles-1)

  for(let i = 0;i < pixeles.length;i += 4){

    pixeles[i] =
      Math.round(pixeles[i]/salto)*salto

    pixeles[i+1] =
      Math.round(pixeles[i+1]/salto)*salto

    pixeles[i+2] =
      Math.round(pixeles[i+2]/salto)*salto

  }

}



// ============================================
// PIXELAR
// ============================================

function pixelar(pixeles,ancho,alto){

  let tamano = 16

  for(let y = 0;y < alto;y += tamano){

    for(let x = 0;x < ancho;x += tamano){

      let posicion =
        (y*ancho+x)*4

      let r = pixeles[posicion]
      let g = pixeles[posicion+1]
      let b = pixeles[posicion+2]

      for(let dy = 0;dy < tamano;dy++){

        for(let dx = 0;dx < tamano;dx++){

          let px = x+dx
          let py = y+dy

          if(px < ancho && py < alto){

            let p =
              (py*ancho+px)*4

            pixeles[p] = r
            pixeles[p+1] = g
            pixeles[p+2] = b

          }

        }

      }

    }

  }

}



// ============================================
// GAUSSIAN BLUR
// ============================================

function gaussian(pixeles,ancho,alto){

  let original =
    new Uint8ClampedArray(pixeles)

  let sigma = RADIO/2

  for(let py = 0;py < alto;py++){

    for(let px = 0;px < ancho;px++){

      let rojo = 0
      let verde = 0
      let azul = 0

      let pesoTotal = 0

      for(let dy = -RADIO;dy <= RADIO;dy++){

        for(let dx = -RADIO;dx <= RADIO;dx++){

          let vecinoX = px+dx
          let vecinoY = py+dy

          if(
            vecinoX >= 0 &&
            vecinoX < ancho &&
            vecinoY >= 0 &&
            vecinoY < alto
          ){

            let distancia =
              dx*dx +
              dy*dy

            let peso =
              Math.exp(
                -distancia /
                (2*sigma*sigma)
              )

            let posicion =
              (vecinoY*ancho+vecinoX)*4

            rojo +=
              original[posicion]*peso

            verde +=
              original[posicion+1]*peso

            azul +=
              original[posicion+2]*peso

            pesoTotal += peso

          }

        }

      }

      let posicion =
        (py*ancho+px)*4

      pixeles[posicion] =
        rojo/pesoTotal

      pixeles[posicion+1] =
        verde/pesoTotal

      pixeles[posicion+2] =
        azul/pesoTotal

      pixeles[posicion+3] =
        original[posicion+3]

    }

  }

}



// ============================================
// DETECCIÓN DE BORDES
// SOBEL
// ============================================

function bordes(pixeles,ancho,alto){

  let original =
    new Uint8ClampedArray(pixeles)

  let gx = [
    -1,0,1,
    -2,0,2,
    -1,0,1
  ]

  let gy = [
    -1,-2,-1,
     0, 0, 0,
     1, 2, 1
  ]


  for(let y = 1;y < alto-1;y++){

    for(let x = 1;x < ancho-1;x++){

      let sumaX = 0
      let sumaY = 0

      let k = 0

      for(let dy = -1;dy <= 1;dy++){

        for(let dx = -1;dx <= 1;dx++){

          let posicion =
            ((y+dy)*ancho+(x+dx))*4

          let gris =
            original[posicion]*0.299 +
            original[posicion+1]*0.587 +
            original[posicion+2]*0.114

          sumaX += gris*gx[k]
          sumaY += gris*gy[k]

          k++

        }

      }

      let intensidad =
        Math.sqrt(
          sumaX*sumaX +
          sumaY*sumaY
        )

      let posicion =
        (y*ancho+x)*4

      pixeles[posicion] =
        intensidad

      pixeles[posicion+1] =
        intensidad

      pixeles[posicion+2] =
        intensidad

      pixeles[posicion+3] = 255

    }

  }

}