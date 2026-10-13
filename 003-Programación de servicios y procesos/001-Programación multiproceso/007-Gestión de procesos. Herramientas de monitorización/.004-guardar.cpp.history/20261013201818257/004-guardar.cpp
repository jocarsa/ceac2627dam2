#include <iostream>
#include <fstream>
using namespace std;

int main() {
		// Abrimos un archivo
    ofstream archivo("resultado.txt");
		// Guardamos lineas dentro del archivo
    archivo << "Hola mundo" << endl;
    archivo << "Este texto se guarda en un archivo" << endl;
    archivo << 12345 << endl;

    archivo.close();

    cout << "Archivo guardado correctamente" << endl;

    return 0;
}
