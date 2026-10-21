#include <opencv2/opencv.hpp>
#include <vector>
#include <cmath>
#include <random>
#include <iostream>

using namespace cv;
using namespace std;

const int ANCHO = 1200;
const int ALTO = 800;
const int PARTICULAS = 12000;

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
};

int main() {

    vector<Particula> particulas;

    mt19937 generador(random_device{}());
    uniform_real_distribution<double> azar(0.0, 1.0);

    // Crear partículas en órbitas alrededor del centro
    for (int i = 0; i < PARTICULAS; i++) {

        double angulo = azar(generador) * 2.0 * CV_PI;

        double radio = RADIO_MIN +
            azar(generador) * (RADIO_MAX - RADIO_MIN);

        // Crear algunos huecos entre anillos
        if (radio > 190 && radio < 210)
            continue;

        if (radio > 275 && radio < 285)
            continue;

        Particula p;

        p.x = cos(angulo) * radio;
        p.y = sin(angulo) * radio;

        // Velocidad orbital circular: v = sqrt(GM/r)
        double velocidad = sqrt(G * MASA / radio);

        p.vx = -sin(angulo) * velocidad;
        p.vy = cos(angulo) * velocidad;

        p.brillo = 0.4 + azar(generador) * 0.6;
        p.tamano = azar(generador) > 0.97 ? 2 : 1;

        particulas.push_back(p);
    }

    namedWindow("Simulacion Saturno", WINDOW_AUTOSIZE);

    while (true) {

        Mat imagen(ALTO, ANCHO, CV_8UC3, Scalar(5, 5, 12));

        // Actualizar física
        for (auto &p : particulas) {

            double r2 = p.x * p.x + p.y * p.y + 25.0;
            double r = sqrt(r2);

            // Aceleración gravitatoria
            double aceleracion = G * MASA / (r2 * r);

            double ax = -p.x * aceleracion;
            double ay = -p.y * aceleracion;

            // Integración semiimplícita de Euler
            p.vx += ax * DT;
            p.vy += ay * DT;

            p.x += p.vx * DT;
            p.y += p.vy * DT;
        }

        // Dibujar mitad posterior del anillo
        for (auto &p : particulas) {

            if (p.y >= 0)
                continue;

            int pantallaX = ANCHO / 2 + p.x;
            int pantallaY = ALTO / 2 + p.y * INCLINACION;

            int brillo = 120 + p.brillo * 135;

            circle(
                imagen,
                Point(pantallaX, pantallaY),
                p.tamano,
                Scalar(brillo * 0.7, brillo * 0.85, brillo),
                -1,
                LINE_AA
            );
        }

        // Dibujar planeta central
        Point centro(ANCHO / 2, ALTO / 2);

        circle(
            imagen,
            centro,
            65,
            Scalar(80, 150, 210),
            -1,
            LINE_AA
        );

        // Iluminación del planeta
        circle(
            imagen,
            Point(centro.x - 15, centro.y - 15),
            45,
            Scalar(110, 185, 235),
            -1,
            LINE_AA
        );

        // Dibujar mitad delantera del anillo
        for (auto &p : particulas) {

            if (p.y < 0)
                continue;

            int pantallaX = ANCHO / 2 + p.x;
            int pantallaY = ALTO / 2 + p.y * INCLINACION;

            int brillo = 120 + p.brillo * 135;

            circle(
                imagen,
                Point(pantallaX, pantallaY),
                p.tamano,
                Scalar(brillo * 0.7, brillo * 0.85, brillo),
                -1,
                LINE_AA
            );
        }

        putText(
            imagen,
            "Simulacion gravitatoria - 12000 particulas",
            Point(20, 35),
            FONT_HERSHEY_SIMPLEX,
            0.7,
            Scalar(220, 220, 220),
            1,
            LINE_AA
        );

        imshow("Simulacion Saturno", imagen);

        // ESC para salir
        if (waitKey(16) == 27)
            break;
    }

    destroyAllWindows();

    return 0;
}