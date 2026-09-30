package com.example.introduccionkotlin

data class Producto(
    val nombre: String,
    val precio: Double,
    val disponible: Boolean
)


fun main() {

    val producto1 = Producto(
        "Teclado",
        49.99,
        true
    )

    val producto2 = Producto(
        "Ratón",
        25.50,
        false
    )

    println(producto1)
    println(producto2)

    println()

    println("Producto: ${producto1.nombre}")
    println("Precio: ${producto1.precio} €")
    println("Disponible: ${producto1.disponible}")
}