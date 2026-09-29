let bichitos = [];

let anchura = 0;
let altura = 0;


onmessage = function(evento){

  let datos = evento.data;


  if(datos.tipo == "iniciar"){

    bichitos = datos.bichitos;

    anchura = datos.anchura;
    altura = datos.altura;

    bucle();

  }

};


function bucle(){

  for(let i = 0; i < bichitos.length; i++){

    bichitos[i].x +=
      (Math.random() - 0.5) * 10;

    bichitos[i].y +=
      (Math.random() - 0.5) * 10;


    // Opcional:
    // hacer que reaparezcan por el otro lado

    if(bichitos[i].x < 0)
      bichitos[i].x = anchura;

    if(bichitos[i].x > anchura)
      bichitos[i].x = 0;

    if(bichitos[i].y < 0)
      bichitos[i].y = altura;

    if(bichitos[i].y > altura)
      bichitos[i].y = 0;

  }


  // Devolver posiciones al hilo principal

  postMessage(bichitos);


  setTimeout(bucle, 0);

}