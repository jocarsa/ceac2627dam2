package com.example.introduccionkotlin

fun main() {

    // val: su valor no puede cambiar
    val nombre = "Laura"

    // var: su valor puede cambiar
    var edad = 20

    println("Nombre: $nombre")
    println("Edad: $edad")

    // Modificamos una variable
    edad = 21

    println("Nueva edad: $edad")

    // Esto daría error porque nombre está declarado con val
    // nombre = "Carlos"
}