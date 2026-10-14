#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main() {
    ifstream archivo("comunicacion.txt");

    // Leemos el archivo línea a línea
    string linea;

    while (getline(archivo, linea)) {
        cout << linea << endl;
    }

    // Todo lo que se abre se cierra
    archivo.close();

    return 0;
}