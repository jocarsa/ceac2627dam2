const productos = [

    {
        nombre: "Teclado",
        precio: 79.99,
        stock: 10
    },

    {
        nombre: "Ratón",
        precio: 39.99,
        stock: 0
    },

    {
        nombre: "Monitor",
        precio: 199.99,
        stock: 5
    }

];


console.log(productos);

console.log(productos[0]);

console.log(
    productos[0].nombre
);


productos.forEach(producto => {

    console.log(
        `${producto.nombre}: ${producto.precio} €`
    );

});