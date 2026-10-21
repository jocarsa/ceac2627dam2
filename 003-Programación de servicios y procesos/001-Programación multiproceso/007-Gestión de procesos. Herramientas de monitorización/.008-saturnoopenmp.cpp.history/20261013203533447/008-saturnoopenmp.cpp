
#include <opencv2/opencv.hpp>
#include <omp.h>
#include <vector>
#include <cmath>
#include <random>
#include <iostream>

using namespace cv;
using namespace std;

const int ANCHO = 1200;
const int ALTO = 800;
const int PARTICULAS = 1200000;

const double G = 1.0;
const double MASA = 120000.0;
const double DT = 0.15;

const double RADIO_MIN = 110.0;
const double RADIO_MAX = 340.0;
const double INCLINACION = 0.35;

struct Particula {
    double x, y;
    double vx, vy;
    double brillo;
    int tamano;

    // Posiciones precalculadas para dibujar
    int pantallaX, pantallaY;
    int intensidad;
    bool delante;
};

int main() {

    // Utilizar todos los núcleos disponibles
    int nucleos = omp_get_max_threads();
    cout << "OpenMP: " << nucleos << " hilos disponibles\n";

    vector<Particula> particulas;
    particulas.reserve(PARTICULAS);

    mt19937 generador(random_device{}());
    uniform_real_distribution<double> azar(0.0, 1.0);

    // Inicialización de partículas
    for (int i = 0; i < PARTICULAS; i++) {

        double angulo = azar(generador) * 2.0 * CV_PI;

        double radio = RADIO_MIN +
            azar(generador) * (RADIO_MAX - RADIO_MIN);

        if (radio > 190 && radio < 210)
            continue;

        if (radio > 275 && radio < 285)
            continue;

        Particula p;

        p.x = cos(angulo) * radio;
        p.y = sin(angulo) * radio;

        double velocidad = sqrt(G * MASA / radio);

        p.vx = -sin(angulo) * velocidad;
        p.vy = cos(angulo) * velocidad;

        p.brillo = 0.4 + azar(generador) * 0.6;
        p.tamano = azar(generador) > 0.97 ? 2 : 1;

        particulas.push_back(p);
    }

    int total = static_cast<int>(particulas.size());

    cout << "Particulas creadas: " << total << endl;

    namedWindow("Saturno OpenMP", WINDOW_AUTOSIZE);

    double tiempoAnterior = omp_get_wtime();
    double fps = 0.0;

    while (true) {

        Mat imagen(ALTO, ANCHO, CV_8UC3, Scalar(5, 5, 12));

        double inicioFisica = omp_get_wtime();

        // ============================================
        // FÍSICA PARALELA CON OPENMP
        // ============================================

        #pragma omp parallel for schedule(static)
        for (int i = 0; i < total; i++) {

            Particula &p = particulas[i];

            double r2 = p.x * p.x + p.y * p.y + 25.0;
            double r = sqrt(r2);

            double aceleracion = G * MASA / (r2 * r);

            double ax = -p.x * aceleracion;
            double ay = -p.y * aceleracion;

            p.vx += ax * DT;
            p.vy += ay * DT;

            p.x += p.vx * DT;
            p.y += p.vy * DT;

            // Proyección a pantalla
            p.pantallaX = ANCHO / 2 + static_cast<int>(p.x);
            p.pantallaY = ALTO / 2 +
                static_cast<int>(p.y * INCLINACION);

            p.intensidad = static_cast<int>(
                120 + p.brillo * 135
            );

            p.delante = p.y >= 0;
        }

        double tiempoFisica = omp_get_wtime() - inicioFisica;

        // ============================================
        // DIBUJAR PARTE POSTERIOR
        // ============================================

        for (const auto &p : particulas) {

            if (p.delante)
                continue;

            if (p.pantallaX < 0 || p.pantallaX >= ANCHO ||
                p.pantallaY < 0 || p.pantallaY >= ALTO)
                continue;

            int b = p.intensidad;

            circle(
                imagen,
                Point(p.pantallaX, p.pantallaY),
                p.tamano,
                Scalar(b * 0.7, b * 0.85, b),
                -1,
                LINE_AA
            );
        }

        // ============================================
        // PLANETA CENTRAL
        // ============================================

        Point centro(ANCHO / 2, ALTO / 2);

        circle(
            imagen,
            centro,
            65,
            Scalar(80, 150, 210),
            -1,
            LINE_AA
        );

        circle(
            imagen,
            Point(centro.x - 15, centro.y - 15),
            45,
            Scalar(110, 185, 235),
            -1,
            LINE_AA
        );

        // ============================================
        // DIBUJAR PARTE DELANTERA
        // ============================================

        for (const auto &p : particulas) {

            if (!p.delante)
                continue;

            if (p.pantallaX < 0 || p.pantallaX >= ANCHO ||
                p.pantallaY < 0 || p.pantallaY >= ALTO)
                continue;

            int b = p.intensidad;

            circle(
                imagen,
                Point(p.pantallaX, p.pantallaY),
                p.tamano,
                Scalar(b * 0.7, b * 0.85, b),
                -1,
                LINE_AA
            );
        }

        // ============================================
        // ESTADÍSTICAS
        // ============================================

        double ahora = omp_get_wtime();
        double delta = ahora - tiempoAnterior;
        tiempoAnterior = ahora;

        if (delta > 0)
            fps = 0.9 * fps + 0.1 * (1.0 / delta);

        putText(
            imagen,
            "SATURNO - OPENMP",
            Point(20, 35),
            FONT_HERSHEY_SIMPLEX,
            0.8,
            Scalar(255, 255, 255),
            2,
            LINE_AA
        );

        putText(
            imagen,
            "Particulas: " + to_string(total),
            Point(20, 70),
            FONT_HERSHEY_SIMPLEX,
            0.55,
            Scalar(180, 220, 255),
            1,
            LINE_AA
        );

        putText(
            imagen,
            "Hilos OpenMP: " + to_string(nucleos),
            Point(20, 95),
            FONT_HERSHEY_SIMPLEX,
            0.55,
            Scalar(180, 220, 255),
            1,
            LINE_AA
        );

        putText(
            imagen,
            "FPS: " + to_string(static_cast<int>(fps)),
            Point(20, 120),
            FONT_HERSHEY_SIMPLEX,
            0.55,
            Scalar(180, 255, 180),
            1,
            LINE_AA
        );

        putText(
            imagen,
            "Fisica: " + to_string(tiempoFisica * 1000.0).substr(0, 6) + " ms",
            Point(20, 145),
            FONT_HERSHEY_SIMPLEX,
            0.55,
            Scalar(180, 255, 180),
            1,
            LINE_AA
        );

        imshow("Saturno OpenMP", imagen);

        if (waitKey(1) == 27)
            break;
    }

    destroyAllWindows();
    return 0;
}

/*
	Compilar:
  g++ 008-saturnoopenmp.cpp -o saturno \
    -O3 -march=native -fopenmp \
    $(pkg-config --cflags --libs opencv4)
*/