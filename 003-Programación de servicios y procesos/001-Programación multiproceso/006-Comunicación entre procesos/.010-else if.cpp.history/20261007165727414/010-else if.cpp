#include <iostream>

int main() {
    int edad = 48;
    if(edad < 10){
    	std::cout << "Eres un niño" << std::endl;
    }else if(edad >= 10 && edad < 20){
    	std::cout << "Eres un adolescente" << std::endl;
    }
    return 0;
}