
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main() {
    int servidor = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in direccion = {0};
    direccion.sin_family = AF_INET;
    direccion.sin_port = htons(8001);
    direccion.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    bind(servidor, (struct sockaddr*)&direccion, sizeof(direccion));
    listen(servidor, 10);

    printf("Servidor en http://localhost:8001\n");

    while (1) {
        int cliente = accept(servidor, NULL, NULL);

        char peticion[4096];
        recv(cliente, peticion, sizeof(peticion) - 1, 0);

        char *respuesta =
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            "Connection: close\r\n"
            "\r\n"
            "<h1>Hola desde C</h1>";

        send(cliente, respuesta, strlen(respuesta), 0);
        close(cliente);
    }

    close(servidor);
    return 0;
}
