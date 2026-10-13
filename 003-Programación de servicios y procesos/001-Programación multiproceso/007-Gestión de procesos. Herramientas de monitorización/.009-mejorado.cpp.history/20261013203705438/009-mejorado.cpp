
#include <opencv2/opencv.hpp>
#include <omp.h>
#include <vector>
#include <cmath>
#include <random>
#include <iostream>
#include <algorithm>
#include <string>

using namespace cv;
using namespace std;

// ============================================
// CONFIGURACIÓN
// ============================================

constexpr int ANCHO = 1200;
constexpr int ALTO = 800;
constexpr int PARTICULAS = 1200000;

constexpr float G = 1.0f;
constexpr float MASA = 120000.0f;
constexpr float RADIO_MIN = 110.0f;
constexpr float RADIO_MAX = 340.0f;
constexpr float INCLINACION = 0.35f;
constexpr float PI = 3.14159265358979323846f;

struct Particula {
    float x, y;
    float vx, vy;
    unsigned char brillo;
    unsigned char tamano;
};

struct PixelParticula {
    int x, y;
    unsigned char brillo;
    unsigned char tamano;
};

// ============================================
// DIBUJO DIRECTO EN MEMORIA
// ============================================

// Cada hilo dibuja exclusivamente en su franja.
// No hay condiciones de carrera.

inline void pintarPixel(
    Mat &imagen,
    int x,
    int y,
    int brillo
) {
    if ((unsigned)x >= ANCHO ||
        (unsigned)y >= ALTO)
        return;

    Vec3b &pixel = imagen.ptr<Vec3b>(y)[x];

    int b = brillo * 7 / 10;
    int g = brillo * 85 / 100;

    pixel[0] = max((int)pixel[0], b);
    pixel[1] = max((int)pixel[1], g);
    pixel[2] = max((int)pixel[2], brillo);
}

inline void pintarParticula(
    Mat &imagen,
    const PixelParticula &p,
    int yMin,
    int yMax
) {
    if ((unsigned)p.x >= ANCHO ||
        p.y < yMin || p.y >= yMax)
        return;

    pintarPixel(imagen, p.x, p.y, p.brillo);

    // Partículas grandes: pequeño destello
    if (p.tamano == 2) {
        if (p.x > 0)
            pintarPixel(imagen, p.x - 1, p.y, p.brillo);

        if (p.x < ANCHO - 1)
            pintarPixel(imagen, p.x + 1, p.y, p.brillo);

        if (p.y > yMin)
            pintarPixel(imagen, p.x, p.y - 1, p.brillo);

        if (p.y + 1 < yMax)
            pintarPixel(imagen, p.x, p.y + 1, p.brillo);
    }
}

// ============================================
// RENDERIZADO PARALELO POR FRANJAS
// ============================================

// Las partículas se agrupan por franja.
// Cada hilo procesa una franja independiente.

void renderizarAnillo(
    Mat &imagen,
    const vector<PixelParticula> &puntos,
    const vector<int> &indices,
    const vector<int> &offsets,
    int franjas
) {
    #pragma omp parallel for schedule(static)
    for (int f = 0; f < franjas; f++) {

        int yMin = f * ALTO / franjas;
        int yMax = (f + 1) * ALTO / franjas;

        for (int j = offsets[f]; j < offsets[f + 1]; j++) {
            pintarParticula(
                imagen,
                puntos[indices[j]],
                yMin,
                yMax
            );
        }
    }
}

// ============================================
// CLASIFICAR PARTÍCULAS POR FRANJA
// ============================================

// Se utilizan buffers reutilizables para evitar
// millones de asignaciones de memoria por frame.

void clasificar(
    const vector<PixelParticula> &puntos,
    const vector<int> &seleccion,
    vector<int> &indices,
    vector<int> &offsets,
    int franjas
) {
    fill(offsets.begin(), offsets.end(), 0);

    // Contar partículas por franja
    for (int idx : seleccion) {
        int y = puntos[idx].y;

        if ((unsigned)y >= ALTO ||
            (unsigned)puntos[idx].x >= ANCHO)
            continue;

        int f = min(franjas - 1, y * franjas / ALTO);
        offsets[f + 1]++;
    }

    // Sumas acumuladas
    for (int f = 1; f <= franjas; f++)
        offsets[f] += offsets[f - 1];

    indices.resize(offsets[franjas]);

    vector<int> cursor = offsets;

    // Distribuir índices
    for (int idx : seleccion) {
        int y = puntos[idx].y;

        if ((unsigned)y >= ALTO ||
            (unsigned)puntos[idx].x >= ANCHO)
            continue;

        int f = min(franjas - 1, y * franjas / ALTO);
        indices[cursor[f]++] = idx;
    }
}

// ============================================
// PROGRAMA PRINCIPAL
// ============================================

int main() {

    // Evitar paralelismo anidado de OpenCV
    cv::setNumThreads(1);

    int hilos = omp_get_max_threads();

    cout << "OpenMP: " << hilos << " hilos\n";

    vector<Particula> particulas;
    particulas.reserve(PARTICULAS);

    mt19937 generador(random_device{}());
    uniform_real_distribution<float> azar(0.0f, 1.0f);

    // ========================================
    // GENERACIÓN DE PARTÍCULAS
    // ========================================

    for (int i = 0; i < PARTICULAS; i++) {

        float angulo = azar(generador) * 2.0f * PI;

        float radio = RADIO_MIN +
            azar(generador) * (RADIO_MAX - RADIO_MIN);

        // Divisiones entre anillos
        if (radio > 190 && radio < 210)
            continue;

        if (radio > 275 && radio < 285)
            continue;

        Particula p;

        p.x = cos(angulo) * radio;
        p.y = sin(angulo) * radio;

        float velocidad = sqrt(G * MASA / radio);

        p.vx = -sin(angulo) * velocidad;
        p.vy = cos(angulo) * velocidad;

        p.brillo = static_cast<unsigned char>(
            120 + azar(generador) * 135
        );

        p.tamano = azar(generador) > 0.97f ? 2 : 1;

        particulas.push_back(p);
    }

    const int total = static_cast<int>(particulas.size());

    cout << "Particulas: " << total << endl;

    // ========================================
    // BUFFERS
    // ========================================

    vector<PixelParticula> puntos(total);

    vector<int> posteriores;
    vector<int> anteriores;

    posteriores.reserve(total);
    anteriores.reserve(total);

    vector<int> indicesPosteriores;
    vector<int> indicesAnteriores;

    vector<int> offsetsPosteriores(hilos + 1);
    vector<int> offsetsAnteriores(hilos + 1);

    Mat imagen(ALTO, ANCHO, CV_8UC3);

    namedWindow("Saturno OpenMP", WINDOW_AUTOSIZE);

    float dt = 0.15f;
    bool pausado = false;

    double fps = 0.0;
    double anterior = omp_get_wtime();

    // ========================================
    // BUCLE PRINCIPAL
    // ========================================

    while (true) {

        double inicioFrame = omp_get_wtime();

        imagen.setTo(Scalar(5, 5, 12));

        // ====================================
        // 1. FÍSICA PARALELA
        // ====================================

        double inicioFisica = omp_get_wtime();

        #pragma omp parallel for schedule(static)
        for (int i = 0; i < total; i++) {

            Particula &p = particulas[i];

            if (!pausado) {

                float r2 = p.x * p.x +
                           p.y * p.y + 25.0f;

                float r = sqrt(r2);

                float aceleracion =
                    G * MASA / (r2 * r);

                float ax = -p.x * aceleracion;
                float ay = -p.y * aceleracion;

                p.vx += ax * dt;
                p.vy += ay * dt;

                p.x += p.vx * dt;
                p.y += p.vy * dt;
            }

            PixelParticula &q = puntos[i];

            q.x = ANCHO / 2 + static_cast<int>(p.x);
            q.y = ALTO / 2 +
                static_cast<int>(p.y * INCLINACION);

            q.brillo = p.brillo;
            q.tamano = p.tamano;
        }

        double msFisica =
            (omp_get_wtime() - inicioFisica) * 1000.0;

        // ====================================
        // 2. SEPARAR CAPAS
        // ====================================

        double inicioRender = omp_get_wtime();

        posteriores.clear();
        anteriores.clear();

        for (int i = 0; i < total; i++) {

            if (particulas[i].y < 0)
                posteriores.push_back(i);
            else
                anteriores.push_back(i);
        }

        // ====================================
        // 3. ANILLO POSTERIOR
        // ====================================

        clasificar(
            puntos,
            posteriores,
            indicesPosteriores,
            offsetsPosteriores,
            hilos
        );

        renderizarAnillo(
            imagen,
            puntos,
            indicesPosteriores,
            offsetsPosteriores,
            hilos
        );

        // ====================================
        // 4. PLANETA CENTRAL
        // ====================================

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

        // ====================================
        // 5. ANILLO DELANTERO
        // ====================================

        clasificar(
            puntos,
            anteriores,
            indicesAnteriores,
            offsetsAnteriores,
            hilos
        );

        renderizarAnillo(
            imagen,
            puntos,
            indicesAnteriores,
            offsetsAnteriores,
            hilos
        );

        double msRender =
            (omp_get_wtime() - inicioRender) * 1000.0;

        // ====================================
        // 6. ESTADÍSTICAS
        // ====================================

        double ahora = omp_get_wtime();
        double delta = ahora - anterior;
        anterior = ahora;

        if (delta > 0) {
            double fpsInstantaneo = 1.0 / delta;
            fps = fps == 0
                ? fpsInstantaneo
                : fps * 0.9 + fpsInstantaneo * 0.1;
        }

        Scalar blanco(240, 240, 240);
        Scalar verde(140, 240, 140);

        putText(imagen, "SATURNO - OPENMP",
            Point(20, 35),
            FONT_HERSHEY_SIMPLEX,
            0.8, blanco, 2, LINE_AA);

        putText(imagen,
            "Particulas: " + to_string(total),
            Point(20, 65),
            FONT_HERSHEY_SIMPLEX,
            0.55, blanco, 1, LINE_AA);

        putText(imagen,
            "Hilos: " + to_string(hilos),
            Point(20, 90),
            FONT_HERSHEY_SIMPLEX,
            0.55, blanco, 1, LINE_AA);

        putText(imagen,
            "FPS: " + to_string((int)fps),
            Point(20, 115),
            FONT_HERSHEY_SIMPLEX,
            0.55, verde, 1, LINE_AA);

        putText(imagen,
            "Fisica: " +
            to_string(msFisica).substr(0, 6) + " ms",
            Point(20, 140),
            FONT_HERSHEY_SIMPLEX,
            0.55, verde, 1, LINE_AA);

        putText(imagen,
            "Render: " +
            to_string(msRender).substr(0, 6) + " ms",
            Point(20, 165),
            FONT_HERSHEY_SIMPLEX,
            0.55, verde, 1, LINE_AA);

        putText(imagen,
            "DT: " + to_string(dt).substr(0, 5),
            Point(20, 190),
            FONT_HERSHEY_SIMPLEX,
            0.55, blanco, 1, LINE_AA);

        putText(imagen,
            "ESPACIO: pausa  |  +/-: velocidad  |  ESC: salir",
            Point(20, ALTO - 20),
            FONT_HERSHEY_SIMPLEX,
            0.45, Scalar(160, 160, 160),
            1, LINE_AA);

        imshow("Saturno OpenMP", imagen);

        // ====================================
        // 7. CONTROLES
        // ====================================

        int tecla = waitKey(1);

        if (tecla == 27)
            break;

        if (tecla == ' ')
            pausado = !pausado;

        if (tecla == '+' || tecla == '=')
            dt = min(1.0f, dt + 0.025f);

        if (tecla == '-')
            dt = max(0.025f, dt - 0.025f);

        if (getWindowProperty(
                "Saturno OpenMP",
                WND_PROP_VISIBLE) < 1)
            break;
    }

    destroyAllWindows();
    return 0;
}
