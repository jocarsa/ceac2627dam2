
// Cada hilo tiene su propia imagen.
// No existen escrituras simultáneas en el mismo buffer.

int hilos = omp_get_max_threads();

vector<Mat> buffers(hilos);

for (int i = 0; i < hilos; i++) {
    buffers[i] = Mat::zeros(ALTO, ANCHO, CV_8UC3);
}

// Renderizado paralelo
#pragma omp parallel
{
    int hilo = omp_get_thread_num();
    Mat &buffer = buffers[hilo];

    #pragma omp for schedule(static)
    for (int i = 0; i < total; i++) {

        const Particula &p = particulas[i];

        int x = p.pantallaX;
        int y = p.pantallaY;

        if (x < 0 || x >= ANCHO ||
            y < 0 || y >= ALTO)
            continue;

        Vec3b &pixel = buffer.at<Vec3b>(y, x);

        int b = p.intensidad;

        pixel[0] = max((int)pixel[0], (int)(b * 0.7));
        pixel[1] = max((int)pixel[1], (int)(b * 0.85));
        pixel[2] = max((int)pixel[2], b);
    }
}

// Combinar buffers
Mat resultado = Mat::zeros(ALTO, ANCHO, CV_8UC3);

for (int i = 0; i < hilos; i++) {
    max(resultado, buffers[i], resultado);
}
