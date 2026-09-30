package com.example.introduccionkotlin

fun main() {

    println("FOR")

    for (i in 1..5) {
        println(i)
    }

    println("\nUNTIL")

    // No incluye el 5
    for (i in 1 until 5) {
        println(i)
    }

    println("\nDOWNTO")

    for (i in 5 downTo 1) {
        println(i)
    }

    println("\nSTEP")

    for (i in 0..10 step 2) {
        println(i)
    }

    println("\nWHILE")

    var contador = 1

    while (contador <= 5) {
        println(contador)
        contador++
    }

    println("\nDO-WHILE")

    var numero = 1

    do {
        println(numero)
        numero++
    } while (numero <= 5)
}
