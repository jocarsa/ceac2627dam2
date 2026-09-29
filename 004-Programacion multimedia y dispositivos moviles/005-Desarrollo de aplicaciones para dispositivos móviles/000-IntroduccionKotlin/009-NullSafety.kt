package com.example.introduccionkotlin

fun main() {

    // No puede almacenar null
    var nombre: String = "Laura"

    println(nombre)

    // Esto produciría un error:
    // nombre = null


    // Esta variable sí puede almacenar null
    var telefono: String? = "600123123"

    println("Teléfono: $telefono")

    telefono = null

    println("Teléfono: $telefono")


    // Acceso seguro
    val email: String? = "alumno@ejemplo.com"

    println("Longitud del email: ${email?.length}")


    // Operador Elvis
    val ciudad: String? = null

    val ciudadMostrar = ciudad ?: "Ciudad desconocida"

    println("Ciudad: $ciudadMostrar")
}