package com.example.introduccionkotlin

fun main() {

    val opcion = 2

    when (opcion) {
        1 -> println("Añadir")
        2 -> println("Modificar")
        3 -> println("Eliminar")
        else -> println("Opción no válida")
    }

    val dia = 6

    when (dia) {
        1, 2, 3, 4, 5 -> println("Día laborable")
        6, 7 -> println("Fin de semana")
        else -> println("Día no válido")
    }

    val nota = 8

    val calificacion = when (nota) {
        in 0..4 -> "Suspenso"
        in 5..6 -> "Aprobado"
        in 7..8 -> "Notable"
        in 9..10 -> "Sobresaliente"
        else -> "Nota no válida"
    }

    println("Calificación: $calificacion")
}