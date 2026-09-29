package com.example.introduccionkotlin

fun main() {

    val numero1 = 10
    val numero2 = 3

    // Operadores aritméticos
    println("Suma: ${numero1 + numero2}")
    println("Resta: ${numero1 - numero2}")
    println("Multiplicación: ${numero1 * numero2}")
    println("División: ${numero1 / numero2}")
    println("Resto: ${numero1 % numero2}")

    println()

    val edad = 20

    // Operadores de comparación
    println("¿Es mayor de edad? ${edad >= 18}")
    println("¿Tiene exactamente 18 años? ${edad == 18}")
    println("¿Tiene una edad diferente de 30? ${edad != 30}")

    println()

    val tieneMatricula = true
    val bloqueado = false

    // Operadores lógicos
    println("Matriculado y no bloqueado: ${tieneMatricula && !bloqueado}")
    println("Matriculado o bloqueado: ${tieneMatricula || bloqueado}")
}