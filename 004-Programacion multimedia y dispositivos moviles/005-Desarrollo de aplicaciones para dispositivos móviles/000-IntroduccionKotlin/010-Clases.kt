package com.example.introduccionkotlin

class Alumno(
    val nombre: String,
    var edad: Int,
    var matriculado: Boolean
) {

    fun mostrarInformacion() {
        println("Nombre: $nombre")
        println("Edad: $edad")
        println("Matriculado: $matriculado")
    }

    fun esMayorEdad(): Boolean {
        return edad >= 18
    }
}


fun main() {

    val alumno1 = Alumno(
        "Laura",
        20,
        true
    )

    alumno1.mostrarInformacion()

    println("¿Es mayor de edad? ${alumno1.esMayorEdad()}")

    // Podemos modificar propiedades declaradas con var
    alumno1.edad = 21

    println("Nueva edad: ${alumno1.edad}")
}