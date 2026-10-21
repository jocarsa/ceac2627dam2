// Instalar libreria: sudo apt install libopencv-dev
#include <opencv2/opencv.hpp>
using namespace cv;

int main() {
    // Crear una imagen negra de 800x600
    Mat imagen = Mat::zeros(600, 800, CV_8UC3);

    // Dibujar un círculo
    circle(
        imagen,
        Point(400, 300),     // Centro (x, y)
        100,                 // Radio
        Scalar(0, 0, 255),   // Color rojo (BGR)
        -1                   // Relleno
    );

    // Mostrar ventana
    imshow("Mi ventana", imagen);

    // Esperar hasta pulsar una tecla
    waitKey(0);

    return 0;
}

// compilar: g++ 006-opencv.cpp $(pkg-config --cflags --libs opencv4)