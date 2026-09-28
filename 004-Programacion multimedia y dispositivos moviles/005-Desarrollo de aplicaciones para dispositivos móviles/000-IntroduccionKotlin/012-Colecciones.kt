package com.example.introduccionkotlin

fun main() {

    // Lista
    val nombres = listOf(
        "Ana",
        "Luis",
        "Marta"
    )

    println(nombres)

    println("Primer alumno: ${nombres[0]}")

    println("\nTodos los alumnos:")

    for (nombre in nombres) {
        println(nombre)
    }


    // Lista modificable
    val asignaturas = mutableListOf(
        "Programación",
        "Bases de datos"
    )

    asignaturas.add("Desarrollo móvil")
    asignaturas.remove("Bases de datos")

    println("\nAsignaturas:")

    for (asignatura in asignaturas) {
        println(asignatura)
    }


    // Set
    val numeros = setOf(1, 2, 2, 3, 3, 3)

    println("\nSet:")
    println(numeros)


    // Map
    val edades = mapOf(
        "Ana" to 20,
        "Luis" to 25,
        "Marta" to 22
    )

    println("\nEdad de Ana:")
    println(edades["Ana"])
}