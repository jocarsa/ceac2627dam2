package com.example.introduccionkotlin

fun saludar() {
    println("Hola")
}

fun saludarPersona(nombre: String) {
    println("Hola $nombre")
}

fun sumar(numero1: Int, numero2: Int): Int {
    return numero1 + numero2
}

fun esMayorEdad(edad: Int): Boolean {
    return edad >= 18
}

// Función simplificada
fun multiplicar(a: Int, b: Int): Int = a * b


fun main() {

    saludar()

    saludarPersona("Laura")
    saludarPersona("Carlos")

    val resultado = sumar(10, 5)
    println("Resultado de la suma: $resultado")

    val edad = 20

    if (esMayorEdad(edad)) {
        println("Puede acceder")
    } else {
        println("No puede acceder")
    }

    println("Resultado multiplicación: ${multiplicar(4, 5)}")
}