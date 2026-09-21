function saludar() {

    console.log("Hola");

}


saludar();

function saludarConParametro(nombre) {

    console.log(`Hola ${nombre}`);

}


saludarConParametro("Ana");

saludarConParametro("Luis");

function sumar(a, b) {

    return a + b;

}


const resultado = sumar(5, 7);

console.log(resultado);


function calcularPrecioFinal(precio, descuento) {

    const rebaja =
        precio * descuento / 100;

    return precio - rebaja;

}


const precioFinal =
    calcularPrecioFinal(100, 20);


console.log(
    `Precio final: ${precioFinal} €`
);