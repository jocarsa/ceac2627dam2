package com.example.introduccionkotlin

data class AlumnoCompleto(
    val nombre: String,
    val edad: Int,
    val matriculado: Boolean,
    val bloqueado: Boolean,
    val nota: Double
)

fun puedeAcceder(alumno: AlumnoCompleto): Boolean {
    return alumno.edad >= 18 &&
            alumno.matriculado &&
            !alumno.bloqueado
}

fun obtenerCalificacion(nota: Double): String {

    return when {
        nota < 0 || nota > 10 -> "Nota no válida"
        nota < 5 -> "Suspenso"
        nota < 6 -> "Aprobado"
        nota < 7 -> "Bien"
        nota < 9 -> "Notable"
        else -> "Sobresaliente"
    }
}

fun main() {

    val alumnos = listOf(
        AlumnoCompleto("Laura", 20, true, false, 8.5),
        AlumnoCompleto("Carlos", 17, true, false, 7.0),
        AlumnoCompleto("Marta", 25, true, true, 9.5),
        AlumnoCompleto("Luis", 22, false, false, 4.0)
    )

    for (alumno in alumnos) {

        println("--------------------------")

        println("Nombre: ${alumno.nombre}")
        println("Edad: ${alumno.edad}")

        val acceso = if (puedeAcceder(alumno)) {
            "Permitido"
        } else {
            "Denegado"
        }

        println("Acceso: $acceso")
        println("Calificación: ${obtenerCalificacion(alumno.nota)}")
    }
}