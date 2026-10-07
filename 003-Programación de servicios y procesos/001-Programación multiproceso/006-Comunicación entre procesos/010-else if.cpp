#include <iostream>

int main() {
    int edad = 48;
    if(edad < 10){
    	std::cout << "Eres un niño" << std::endl;
    }else if(edad >= 10 && edad < 20){
    	std::cout << "Eres un adolescente" << std::endl;
    }else if(edad >= 20 && edad < 30){
    	std::cout << "Eres un joven" << std::endl;
    }else if(edad >= 30 && edad < 40){
    	std::cout << "Eres un adulto" << std::endl;
    }else{
    	std::cout << "Eres ya un viejo" << std::endl;
    }
    return 0;
}