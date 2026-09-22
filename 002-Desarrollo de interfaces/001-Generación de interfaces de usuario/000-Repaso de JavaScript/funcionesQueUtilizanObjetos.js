const producto = {

    nombre: "Teclado",

    precio: 80,

    stock: 5

};


function mostrarProducto(producto) {

    console.log(
        `${producto.nombre} - ${producto.precio} €`
    );

}


mostrarProducto(producto);

function hayStock(producto) {

    return producto.stock > 0;

}


console.log(
    hayStock(producto)
);