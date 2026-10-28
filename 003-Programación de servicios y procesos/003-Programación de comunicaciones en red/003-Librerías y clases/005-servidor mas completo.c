
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/stat.h>
#include <limits.h>
#include <errno.h>

#define PUERTO 8001
#define BUFFER 8192

// Determinar el tipo de archivo
const char *tipo_mime(const char *ruta) {
    const char *extension = strrchr(ruta, '.');

    if (!extension) return "application/octet-stream";

    if (strcmp(extension, ".html") == 0) return "text/html; charset=utf-8";
    if (strcmp(extension, ".css") == 0) return "text/css";
    if (strcmp(extension, ".js") == 0) return "application/javascript";
    if (strcmp(extension, ".json") == 0) return "application/json";
    if (strcmp(extension, ".png") == 0) return "image/png";
    if (strcmp(extension, ".jpg") == 0) return "image/jpeg";
    if (strcmp(extension, ".jpeg") == 0) return "image/jpeg";
    if (strcmp(extension, ".gif") == 0) return "image/gif";
    if (strcmp(extension, ".svg") == 0) return "image/svg+xml";
    if (strcmp(extension, ".ico") == 0) return "image/x-icon";
    if (strcmp(extension, ".webp") == 0) return "image/webp";
    if (strcmp(extension, ".woff2") == 0) return "font/woff2";
    if (strcmp(extension, ".pdf") == 0) return "application/pdf";
    if (strcmp(extension, ".txt") == 0) return "text/plain; charset=utf-8";

    return "application/octet-stream";
}

// Enviar una respuesta de error
void enviar_error(int cliente, int codigo, const char *mensaje) {
    char respuesta[1024];

    snprintf(respuesta, sizeof(respuesta),
        "HTTP/1.1 %d %s\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        "Connection: close\r\n"
        "\r\n"
        "<h1>%d %s</h1>",
        codigo, mensaje, codigo, mensaje);

    send(cliente, respuesta, strlen(respuesta), 0);
}

// Servir un archivo
void servir_archivo(int cliente, const char *ruta, int solo_cabeceras) {
    FILE *archivo = fopen(ruta, "rb");

    if (!archivo) {
        enviar_error(cliente, 404, "Not Found");
        return;
    }

    struct stat info;
    if (fstat(fileno(archivo), &info) != 0 || !S_ISREG(info.st_mode)) {
        fclose(archivo);
        enviar_error(cliente, 403, "Forbidden");
        return;
    }

    char cabecera[1024];

    snprintf(cabecera, sizeof(cabecera),
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %lld\r\n"
        "Connection: close\r\n"
        "\r\n",
        tipo_mime(ruta),
        (long long)info.st_size);

    send(cliente, cabecera, strlen(cabecera), 0);

    if (!solo_cabeceras) {
        char buffer[BUFFER];
        size_t leidos;

        while ((leidos = fread(buffer, 1, sizeof(buffer), archivo)) > 0) {
            size_t enviados = 0;

            while (enviados < leidos) {
                ssize_t n = send(cliente,
                    buffer + enviados,
                    leidos - enviados, 0);

                if (n <= 0) {
                    fclose(archivo);
                    return;
                }

                enviados += n;
            }
        }
    }

    fclose(archivo);
}

int main() {
    char raiz[PATH_MAX];

    if (!realpath("web", raiz)) {
        perror("No existe la carpeta web");
        return 1;
    }

    int servidor = socket(AF_INET, SOCK_STREAM, 0);

    if (servidor < 0) {
        perror("socket");
        return 1;
    }

    int opcion = 1;
    setsockopt(servidor, SOL_SOCKET, SO_REUSEADDR,
               &opcion, sizeof(opcion));

    struct sockaddr_in direccion = {0};
    direccion.sin_family = AF_INET;
    direccion.sin_port = htons(PUERTO);
    direccion.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (bind(servidor, (struct sockaddr*)&direccion,
             sizeof(direccion)) < 0) {
        perror("bind");
        close(servidor);
        return 1;
    }

    if (listen(servidor, 10) < 0) {
        perror("listen");
        close(servidor);
        return 1;
    }

    printf("Servidor en http://localhost:%d\n", PUERTO);
    printf("Sirviendo archivos desde: %s\n", raiz);

    while (1) {
        int cliente = accept(servidor, NULL, NULL);

        if (cliente < 0) continue;

        char peticion[4096] = {0};
        ssize_t recibidos = recv(cliente, peticion,
                                 sizeof(peticion) - 1, 0);

        if (recibidos <= 0) {
            close(cliente);
            continue;
        }

        char metodo[16] = {0};
        char url[2048] = {0};

        if (sscanf(peticion, "%15s %2047s", metodo, url) != 2) {
            enviar_error(cliente, 400, "Bad Request");
            close(cliente);
            continue;
        }

        printf("%s %s\n", metodo, url);

        if (strcmp(metodo, "GET") != 0 &&
            strcmp(metodo, "HEAD") != 0) {
            enviar_error(cliente, 405, "Method Not Allowed");
            close(cliente);
            continue;
        }

        // Eliminar parametros GET
        char *interrogacion = strchr(url, '?');
        if (interrogacion) *interrogacion = '\0';

        // Evitar salir de la carpeta web
        if (strstr(url, "..") || strchr(url, '\\') ||
            url[0] != '/') {
            enviar_error(cliente, 403, "Forbidden");
            close(cliente);
            continue;
        }

        char ruta[PATH_MAX];

        // Si se solicita /, servir index.html
        if (strcmp(url, "/") == 0) {
            strcpy(url, "/index.html");
        }

        char candidata[PATH_MAX];

        if (strlen(raiz) + strlen(url) + 1 >= sizeof(candidata)) {
            enviar_error(cliente, 414, "URI Too Long");
            close(cliente);
            continue;
        }

        snprintf(candidata, sizeof(candidata), "%s%s", raiz, url);

        // Resolver la ruta y comprobar que sigue dentro de web
        if (!realpath(candidata, ruta)) {
            enviar_error(cliente, 404, "Not Found");
            close(cliente);
            continue;
        }

        size_t longitud_raiz = strlen(raiz);

        if (strncmp(ruta, raiz, longitud_raiz) != 0 ||
            (ruta[longitud_raiz] != '/' &&
             ruta[longitud_raiz] != '\0')) {
            enviar_error(cliente, 403, "Forbidden");
            close(cliente);
            continue;
        }

        struct stat info;

        if (stat(ruta, &info) == 0 && S_ISDIR(info.st_mode)) {
            char indice[PATH_MAX];

            if (strlen(ruta) + strlen("/index.html") + 1 >= sizeof(indice)) {
                enviar_error(cliente, 414, "URI Too Long");
                close(cliente);
                continue;
            }

            snprintf(indice, sizeof(indice), "%s/index.html", ruta);
            servir_archivo(cliente, indice,
                           strcmp(metodo, "HEAD") == 0);
        } else {
            servir_archivo(cliente, ruta,
                           strcmp(metodo, "HEAD") == 0);
        }

        close(cliente);
    }

    close(servidor);
    return 0;
}
