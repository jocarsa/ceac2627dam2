self.onmessage = function(event){

    const datos = event.data.datos || [];
    const iteraciones = Number(event.data.iteraciones) || 1000000;

    const frecuencias = {};

    datos.forEach(function(fila){
        ["n1","n2","n3","n4","n5"].forEach(function(campo){
            const numero = parseInt(fila[campo]);

            if(!Number.isNaN(numero)){
                frecuencias[numero] =
                    (frecuencias[numero] || 0) + 1;
            }
        });
    });

    /*
       Carga artificial de CPU.

       Se divide en bloques únicamente para poder informar
       del progreso al hilo principal.
    */

    let acumulador = 0.123456789;
    const bloques = 100;
    const porBloque = Math.ceil(iteraciones / bloques);
    let hechas = 0;

    for(let bloque = 0; bloque < bloques && hechas < iteraciones; bloque++){

        const limite = Math.min(
            iteraciones,
            hechas + porBloque
        );

        for(let i = hechas; i < limite; i++){

            /*
               Varias operaciones matemáticas para que el
               navegador tenga trabajo real de CPU.
            */

            const x = (i % 10000) + 1;

            acumulador += Math.sqrt(x) * 0.000001;
            acumulador = Math.sin(acumulador + x * 0.00001);
            acumulador += Math.cos(x * 0.001);
            acumulador = Math.sqrt(Math.abs(acumulador) + 1.000001);
        }

        hechas = limite;

        self.postMessage({
            tipo:"progreso",
            valor:Math.round((hechas / iteraciones) * 100)
        });
    }

    let numeroMasFrecuente = null;
    let frecuenciaMaxima = -1;

    Object.keys(frecuencias).forEach(function(numero){
        if(frecuencias[numero] > frecuenciaMaxima){
            frecuenciaMaxima = frecuencias[numero];
            numeroMasFrecuente = Number(numero);
        }
    });

    self.postMessage({
        tipo:"resultado",
        resultado:{
            frecuencias:frecuencias,
            numero_mas_frecuente:numeroMasFrecuente,
            frecuencia_maxima:frecuenciaMaxima,
            comprobacion:acumulador
        }
    });
};
