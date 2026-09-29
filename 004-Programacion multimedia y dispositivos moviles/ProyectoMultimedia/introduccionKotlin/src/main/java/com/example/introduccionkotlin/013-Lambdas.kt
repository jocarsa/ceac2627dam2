package com.example.introduccionkotlin

fun main() {

    // Lambda sencilla
    val saludar = {
        println("Hola desde una lambda")
    }

    saludar()


    // Lambda con un parámetro
    val mostrarNombre = { nombre: String ->
        println("Hola $nombre")
    }

    mostrarNombre("Laura")


    // Lambda que devuelve un resultado
    val duplicar = { numero: Int ->
        numero * 2
    }

    val resultado = duplicar(5)

    println("Resultado: $resultado")
}