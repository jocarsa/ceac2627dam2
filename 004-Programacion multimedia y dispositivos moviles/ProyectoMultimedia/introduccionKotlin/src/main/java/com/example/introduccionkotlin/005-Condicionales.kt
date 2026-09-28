package com.example.introduccionkotlin

fun main() {

    val edad = 20
    val tieneMatricula = true
    val bloqueado = false

    // Condicional sencillo
    if (edad >= 18) {
        println("Es mayor de edad")
    } else {
        println("Es menor de edad")
    }

    // Varias condiciones
    if (edad >= 18 && tieneMatricula && !bloqueado) {
        println("Puede acceder")
    } else {
        println("No puede acceder")
    }

    val nota = 7.5

    if (nota < 0 || nota > 10) {
        println("Nota no válida")
    } else if (nota < 5) {
        println("Suspenso")
    } else if (nota < 7) {
        println("Aprobado")
    } else if (nota < 9) {
        println("Notable")
    } else {
        println("Sobresaliente")
    }

    // if puede devolver directamente un valor
    val mensaje = if (edad >= 18) {
        "Mayor de edad"
    } else {
        "Menor de edad"
    }

    println(mensaje)
}