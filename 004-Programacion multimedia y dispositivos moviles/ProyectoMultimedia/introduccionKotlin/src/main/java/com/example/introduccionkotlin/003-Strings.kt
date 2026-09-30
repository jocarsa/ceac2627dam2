package com.example.introduccionkotlin

fun main() {

    val nombre = "Carlos"
    val edad = 22

    // Concatenación
    println("Hola " + nombre + ", tienes " + edad + " años")

    // Plantillas de String
    println("Hola $nombre, tienes $edad años")

    val precio = 20.0
    val cantidad = 3

    // Podemos introducir expresiones utilizando ${}
    println("Precio: $precio €")
    println("Cantidad: $cantidad")
    println("Precio total: ${precio * cantidad} €")

    // Algunas operaciones con String
    println("Número de caracteres: ${nombre.length}")
    println("Mayúsculas: ${nombre.uppercase()}")
    println("Minúsculas: ${nombre.lowercase()}")
}