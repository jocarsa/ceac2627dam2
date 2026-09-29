onmessage = function(evento){

    const datos =
        evento.data;

    const todos =
        datos.bichitos;

    const inicio =
        datos.inicio;

    const fin =
        datos.fin;

    const anchura =
        datos.anchura;

    const altura =
        datos.altura;


    let resultado = [];


    for(
        let i = inicio;
        i < fin;
        i++
    ){

        let b =
            todos[i];


        // ==================================
        // MOVIMIENTO
        // ==================================

        b.x +=
            Math.cos(b.angulo) *
            b.velocidad;

        b.y +=
            Math.sin(b.angulo) *
            b.velocidad;



        // ==================================
        // PARED DERECHA
        // ==================================

        if(
            b.x+b.radio >
            anchura
        ){

            b.x =
                anchura-b.radio;

            b.angulo =
                Math.PI-b.angulo;

        }



        // ==================================
        // PARED IZQUIERDA
        // ==================================

        if(
            b.x-b.radio <
            0
        ){

            b.x =
                b.radio;

            b.angulo =
                Math.PI-b.angulo;

        }



        // ==================================
        // PARED INFERIOR
        // ==================================

        if(
            b.y+b.radio >
            altura
        ){

            b.y =
                altura-b.radio;

            b.angulo =
                -b.angulo;

        }



        // ==================================
        // PARED SUPERIOR
        // ==================================

        if(
            b.y-b.radio <
            0
        ){

            b.y =
                b.radio;

            b.angulo =
                -b.angulo;

        }


        resultado.push(b);

    }


    postMessage({

        inicio:inicio,

        bichitos:resultado

    });

};