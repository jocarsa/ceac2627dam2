let bichitos = null;

let anchura = 0;
let altura = 0;


onmessage = function(evento){

  const datos = evento.data;


  if(datos.tipo === "iniciar"){

    bichitos = datos.bichitos;

    anchura = datos.anchura;
    altura = datos.altura;

    calcular();

  }


  if(datos.tipo === "continuar"){

    calcular();

  }

};


function calcular(){

  mover();

  colisiones();

  postMessage(bichitos);

}


function mover(){

  for(let i = 0; i < bichitos.length; i++){

    const b = bichitos[i];


    // ==================================
    // MOVIMIENTO MEDIANTE VECTOR
    // ==================================

    b.x += Math.cos(b.angulo) * b.velocidad;

    b.y += Math.sin(b.angulo) * b.velocidad;



    // ==================================
    // COLISIÓN CON PAREDES
    // ==================================


    // Derecha

    if(b.x + b.radio > anchura){

      b.x = anchura - b.radio;

      b.angulo =
        Math.PI - b.angulo;

    }


    // Izquierda

    if(b.x - b.radio < 0){

      b.x = b.radio;

      b.angulo =
        Math.PI - b.angulo;

    }


    // Abajo

    if(b.y + b.radio > altura){

      b.y = altura - b.radio;

      b.angulo =
        -b.angulo;

    }


    // Arriba

    if(b.y - b.radio < 0){

      b.y = b.radio;

      b.angulo =
        -b.angulo;

    }

  }

}



function colisiones(){

  for(let i = 0; i < bichitos.length; i++){

    for(let j = i + 1; j < bichitos.length; j++){

      let a = bichitos[i];
      let b = bichitos[j];


      // Diferencia entre posiciones

      let dx = b.x - a.x;
      let dy = b.y - a.y;


      // Distancia al cuadrado

      let distancia2 =
        dx * dx +
        dy * dy;


      // Distancia mínima para colisionar

      let distanciaMinima =
        a.radio + b.radio;


      // Evitamos sqrt cuando no es necesario

      if(
        distancia2 <
        distanciaMinima * distanciaMinima
      ){

        resolverColision(a,b,dx,dy,distancia2);

      }

    }

  }

}



function resolverColision(a,b,dx,dy,distancia2){

  let distancia =
    Math.sqrt(distancia2);


  // Evitar división por cero

  if(distancia === 0){

    distancia = 0.001;

    dx = 0.001;

  }


  // ==================================
  // VECTOR NORMAL
  // ==================================

  let nx =
    dx / distancia;

  let ny =
    dy / distancia;


  // ==================================
  // SEPARAR LOS BICHITOS
  // ==================================

  let solapamiento =
    (a.radio + b.radio) - distancia;


  a.x -= nx * solapamiento / 2;
  a.y -= ny * solapamiento / 2;

  b.x += nx * solapamiento / 2;
  b.y += ny * solapamiento / 2;



  // ==================================
  // VELOCIDADES CARTESIANAS
  // ==================================

  let avx =
    Math.cos(a.angulo) *
    a.velocidad;

  let avy =
    Math.sin(a.angulo) *
    a.velocidad;


  let bvx =
    Math.cos(b.angulo) *
    b.velocidad;

  let bvy =
    Math.sin(b.angulo) *
    b.velocidad;



  // ==================================
  // VELOCIDAD RELATIVA
  // ==================================

  let rvx = avx - bvx;
  let rvy = avy - bvy;


  let velocidadNormal =
    rvx * nx +
    rvy * ny;


  /*
    Si ya se están separando,
    no hacemos otra colisión.
  */

  if(velocidadNormal <= 0){

    return;

  }



  // ==================================
  // COLISIÓN ELÁSTICA
  // masas iguales
  // ==================================

  avx -= velocidadNormal * nx;
  avy -= velocidadNormal * ny;

  bvx += velocidadNormal * nx;
  bvy += velocidadNormal * ny;



  // ==================================
  // VOLVER A ÁNGULO + VELOCIDAD
  // ==================================

  a.velocidad =
    Math.sqrt(
      avx * avx +
      avy * avy
    );

  b.velocidad =
    Math.sqrt(
      bvx * bvx +
      bvy * bvy
    );


  a.angulo =
    Math.atan2(
      avy,
      avx
    );


  b.angulo =
    Math.atan2(
      bvy,
      bvx
    );

}