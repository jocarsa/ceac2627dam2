// ============================================================
// VARIABLES
// ============================================================

let particulas;

let numero;

let inicio;
let fin;

let anchura;
let altura;

let tamanoCelda;

let datosPorBichito;


// ============================================================
// MENSAJES
// ============================================================

onmessage = function(evento){

    const datos =
        evento.data;


    // --------------------------------------------------------
    // INICIALIZACIÓN
    // --------------------------------------------------------

    if(
        datos.tipo ===
        "inicializar"
    ){

        particulas =
            new Float32Array(
                datos.buffer
            );


        numero =
            datos.numero;


        inicio =
            datos.inicio;

        fin =
            datos.fin;


        anchura =
            datos.anchura;

        altura =
            datos.altura;


        tamanoCelda =
            datos.tamanoCelda;


        datosPorBichito =
            datos.datosPorBichito;

    }


    // --------------------------------------------------------
    // FRAME
    // --------------------------------------------------------

    else if(
        datos.tipo ===
        "calcular"
    ){

        calcular();

        postMessage({
            tipo:"listo"
        });

    }


    // --------------------------------------------------------
    // RESIZE
    // --------------------------------------------------------

    else if(
        datos.tipo ===
        "resize"
    ){

        anchura =
            datos.anchura;

        altura =
            datos.altura;

    }

};


// ============================================================
// FRAME
// ============================================================

function calcular(){

    mover();

    const grid =
        construirGrid();

    colisiones(grid);

}


// ============================================================
// MOVIMIENTO
// ============================================================

function mover(){

    for(
        let i = inicio;
        i < fin;
        i++
    ){

        const base =
            i *
            datosPorBichito;


        let x =
            particulas[base];

        let y =
            particulas[base+1];

        let vx =
            particulas[base+2];

        let vy =
            particulas[base+3];

        const radio =
            particulas[base+4];


        // ----------------------------------------
        // MOVIMIENTO
        // ----------------------------------------

        x += vx;
        y += vy;


        // ----------------------------------------
        // PARED IZQUIERDA
        // ----------------------------------------

        if(
            x-radio < 0
        ){

            x = radio;

            vx =
                Math.abs(vx);

        }


        // ----------------------------------------
        // PARED DERECHA
        // ----------------------------------------

        if(
            x+radio >
            anchura
        ){

            x =
                anchura-radio;

            vx =
                -Math.abs(vx);

        }


        // ----------------------------------------
        // PARED SUPERIOR
        // ----------------------------------------

        if(
            y-radio < 0
        ){

            y =
                radio;

            vy =
                Math.abs(vy);

        }


        // ----------------------------------------
        // PARED INFERIOR
        // ----------------------------------------

        if(
            y+radio >
            altura
        ){

            y =
                altura-radio;

            vy =
                -Math.abs(vy);

        }


        particulas[base] =
            x;

        particulas[base+1] =
            y;

        particulas[base+2] =
            vx;

        particulas[base+3] =
            vy;

    }

}


// ============================================================
// CONSTRUIR SPATIAL GRID
// ============================================================

function construirGrid(){

    const grid =
        new Map();


    for(
        let i = 0;
        i < numero;
        i++
    ){

        const base =
            i *
            datosPorBichito;


        const x =
            particulas[base];

        const y =
            particulas[base+1];


        const cx =
            Math.floor(
                x /
                tamanoCelda
            );


        const cy =
            Math.floor(
                y /
                tamanoCelda
            );


        const clave =
            cx + "," + cy;


        let celda =
            grid.get(clave);


        if(
            celda === undefined
        ){

            celda = [];

            grid.set(
                clave,
                celda
            );

        }


        celda.push(i);

    }


    return grid;

}


// ============================================================
// COLISIONES
// ============================================================

function colisiones(grid){

    for(
        let i = inicio;
        i < fin;
        i++
    ){

        const base =
            i *
            datosPorBichito;


        const x =
            particulas[base];

        const y =
            particulas[base+1];


        const cx =
            Math.floor(
                x /
                tamanoCelda
            );


        const cy =
            Math.floor(
                y /
                tamanoCelda
            );


        // ----------------------------------------
        // CELDA ACTUAL + 8 VECINAS
        // ----------------------------------------

        for(
            let ox = -1;
            ox <= 1;
            ox++
        ){

            for(
                let oy = -1;
                oy <= 1;
                oy++
            ){

                const clave =
                    (cx+ox) +
                    "," +
                    (cy+oy);


                const celda =
                    grid.get(clave);


                if(
                    celda === undefined
                ){
                    continue;
                }


                for(
                    let k = 0;
                    k < celda.length;
                    k++
                ){

                    const j =
                        celda[k];


                    if(
                        j === i
                    ){
                        continue;
                    }


                    comprobarColision(
                        i,
                        j
                    );

                }

            }

        }

    }

}


// ============================================================
// COLISIÓN
// ============================================================

function comprobarColision(i,j){

    const ai =
        i *
        datosPorBichito;

    const bi =
        j *
        datosPorBichito;


    let ax =
        particulas[ai];

    let ay =
        particulas[ai+1];


    const bx =
        particulas[bi];

    const by =
        particulas[bi+1];


    let avx =
        particulas[ai+2];

    let avy =
        particulas[ai+3];


    const bvx =
        particulas[bi+2];

    const bvy =
        particulas[bi+3];


    const ar =
        particulas[ai+4];

    const br =
        particulas[bi+4];


    // --------------------------------------------------------
    // DISTANCIA
    // --------------------------------------------------------

    let dx =
        bx-ax;

    let dy =
        by-ay;


    let distancia2 =
        dx*dx +
        dy*dy;


    const distanciaMinima =
        ar+br;


    if(
        distancia2 >=
        distanciaMinima *
        distanciaMinima
    ){
        return;
    }


    // --------------------------------------------------------
    // EVITAR DIVISIÓN ENTRE CERO
    // --------------------------------------------------------

    if(
        distancia2 <
        0.000001
    ){

        dx = 0.001;
        dy = 0;

        distancia2 =
            dx*dx;

    }


    const distancia =
        Math.sqrt(
            distancia2
        );


    const nx =
        dx /
        distancia;

    const ny =
        dy /
        distancia;


    // --------------------------------------------------------
    // SEPARAR
    // --------------------------------------------------------

    const solapamiento =
        distanciaMinima -
        distancia;


    /*
        IMPORTANTE:

        Este worker solo modifica
        SU partícula.

        No modificamos j porque puede
        pertenecer a otro worker.

        Así evitamos que dos workers
        escriban simultáneamente sobre
        la misma partícula.
    */


    ax -=
        nx *
        solapamiento;


    ay -=
        ny *
        solapamiento;


    // --------------------------------------------------------
    // VELOCIDAD RELATIVA
    // --------------------------------------------------------

    const rvx =
        avx-bvx;

    const rvy =
        avy-bvy;


    const velocidadNormal =
        rvx*nx +
        rvy*ny;


    /*
        Con nuestra definición de normal:

        si > 0 se están aproximando.
    */

    if(
        velocidadNormal >
        0
    ){

        // ----------------------------------------
        // COLISIÓN ELÁSTICA
        // MASAS IGUALES
        // ----------------------------------------

        avx -=
            velocidadNormal *
            nx;


        avy -=
            velocidadNormal *
            ny;

    }


    // --------------------------------------------------------
    // GUARDAR ÚNICAMENTE PARTÍCULA PROPIA
    // --------------------------------------------------------

    particulas[ai] =
        ax;

    particulas[ai+1] =
        ay;

    particulas[ai+2] =
        avx;

    particulas[ai+3] =
        avy;

}