#include <iostream>
#include <fstream>
using namespace std;

int main() {
    ofstream archivo("comunicacion.txt");
    archivo << "Esto lo escribe el programa 1" << endl;
    archivo.close();

    return 0;
}