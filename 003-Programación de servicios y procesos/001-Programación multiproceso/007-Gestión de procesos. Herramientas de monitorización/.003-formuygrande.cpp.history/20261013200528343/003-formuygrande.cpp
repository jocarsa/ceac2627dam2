#include <stdio.h>
#include <omp.h>

int main() {
		// Establezco numero de operaciones
    const long long iteraciones = 100000000;
    // Dame el tiempo de inicio
    double inicio = omp_get_wtime();
		// todo esto se ejecuta en paralelo
    #pragma omp parallel
    {
        int hilo = omp_get_thread_num();
        int total = omp_get_num_threads();
        double numero = 1.000000065;
        for (long long i = 0; i < iteraciones; i++) {
            numero *= 1.0000000534;
        }
        printf("Hilo %d de %d | Resultado: %.10e\n",
            hilo, total, numero);
    }
		// Ahora toma el tiempo al final 
    double fin = omp_get_wtime();
		// Y sacame una comparacion
    printf("\nTiempo total: %.4f segundos\n", fin - inicio);

    return 0;
}