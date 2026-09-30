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

  for(let i = 0; i < bichitos.length; i++){

    let b = bichitos[i];

    b.x += (Math.random() - 0.5) * 10;
    b.y += (Math.random() - 0.5) * 10;


    if(b.x < 0)
      b.x = anchura;

    if(b.x > anchura)
      b.x = 0;

    if(b.y < 0)
      b.y = altura;

    if(b.y > altura)
      b.y = 0;

  }


  /*
    Enviamos los datos.

    Y PARAMOS.

    No hacemos:

        setTimeout(bucle, 0)

    El worker no vuelve a calcular
    hasta recibir "continuar".
  */

  postMessage(bichitos);

}