package com.example.introduccionkotlin

fun main() {

    val nombre: String = "Laura"
    val edad: Int = 20
    val precio: Double = 19.99
    val descuento: Float = 10.5f
    val disponible: Boolean = true
    val inicial: Char = 'L'

    println("Nombre: $nombre")
    println("Edad: $edad")
    println("Precio: $precio")
    println("Descuento: $descuento")
    println("Disponible: $disponible")
    println("Inicial: $inicial")

    // Kotlin también puede inferir automáticamente el tipo
    val ciudad = "Valencia"
    val codigoPostal = 46001

    println("Ciudad: $ciudad")
    println("Código postal: $codigoPostal")
}