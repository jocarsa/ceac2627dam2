
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/stat.h>
#include <limits.h>
#include <errno.h>
#include <signal.h>

#define PUERTO 8001
#define BUFFER 8192
#define MAX_INCLUSIONES 10
#define MAX_HTML (10 * 1024 * 1024)
#define MAX_RESULTADO (20 * 1024 * 1024)

const char *tipo_mime(const char *ruta) {
    const char *ext = strrchr(ruta, '.');

    if (!ext) return "application/octet-stream";

    if (!strcmp(ext, ".html") || !strcmp(ext, ".htm"))
        return "text/html; charset=utf-8";
    if (!strcmp(ext, ".css")) return "text/css; charset=utf-8";
    if (!strcmp(ext, ".js")) return "application/javascript";
    if (!strcmp(ext, ".json")) return "application/json";
    if (!strcmp(ext, ".png")) return "image/png";
    if (!strcmp(ext, ".jpg")) return "image/jpeg";
    if (!strcmp(ext, ".jpeg")) return "image/jpeg";
    if (!strcmp(ext, ".gif")) return "image/gif";
    if (!strcmp(ext, ".svg")) return "image/svg+xml";
    if (!strcmp(ext, ".ico")) return "image/x-icon";
    if (!strcmp(ext, ".webp")) return "image/webp";
    if (!strcmp(ext, ".woff")) return "font/woff";
    if (!strcmp(ext, ".woff2")) return "font/woff2";
    if (!strcmp(ext, ".pdf")) return "application/pdf";
    if (!strcmp(ext, ".txt")) return "text/plain; charset=utf-8";

    return "application/octet-stream";
}

// Enviar todos los bytes, incluso si send() envía solo una parte
int enviar_todo(int cliente, const void *datos, size_t longitud) {
    const char *p = datos;

    while (longitud > 0) {
        ssize_t n = send(cliente, p, longitud, 0);

        if (n <= 0) {
            if (n < 0 && errno == EINTR) continue;
            return 0;
        }

        p += n;
        longitud -= (size_t)n;
    }

    return 1;
}

// Comprobar que una ruta permanece dentro de la raíz web
int dentro_raiz(const char *ruta, const char *raiz) {
    size_t n = strlen(raiz);

    if (strncmp(ruta, raiz, n) != 0)
        return 0;

    return ruta[n] == '/' || ruta[n] == '\0';
}

// Leer un archivo completo en memoria
int leer_archivo(const char *ruta, char **datos, size_t *longitud) {
    struct stat info;

    if (stat(ruta, &info) != 0 ||
        !S_ISREG(info.st_mode) ||
        info.st_size < 0 ||
        info.st_size > MAX_HTML)
        return 0;

    FILE *f = fopen(ruta, "rb");
    if (!f) return 0;

    size_t tam = (size_t)info.st_size;

    char *buffer = malloc(tam + 1);
    if (!buffer) {
        fclose(f);
        return 0;
    }

    size_t leidos = fread(buffer, 1, tam, f);
    fclose(f);

    if (leidos != tam) {
        free(buffer);
        return 0;
    }

    buffer[tam] = '\0';

    *datos = buffer;
    *longitud = tam;

    return 1;
}

// Añadir bytes a un buffer dinámico
int agregar(
    char **destino,
    size_t *longitud,
    const char *origen,
    size_t cantidad
) {
    if (cantidad > MAX_RESULTADO ||
        *longitud > MAX_RESULTADO - cantidad)
        return 0;

    size_t nuevo = *longitud + cantidad;

    char *tmp = realloc(*destino, nuevo + 1);
    if (!tmp) return 0;

    *destino = tmp;

    memcpy(*destino + *longitud, origen, cantidad);

    *longitud = nuevo;
    (*destino)[nuevo] = '\0';

    return 1;
}

// Procesador recursivo de directivas HTML
int procesar_html(
    const char *ruta,
    const char *raiz,
    int profundidad,
    char **salida,
    size_t *longitud_salida
) {
    if (profundidad > MAX_INCLUSIONES)
        return 0;

    char ruta_real[PATH_MAX];

    if (!realpath(ruta, ruta_real))
        return 0;

    if (!dentro_raiz(ruta_real, raiz))
        return 0;

    char *texto = NULL;
    size_t longitud_texto = 0;

    if (!leer_archivo(ruta_real, &texto, &longitud_texto))
        return 0;

    char *resultado = NULL;
    size_t total = 0;

    const char *marca = "<#incluir \"";
    const char *cierre = "\" #>";

    size_t longitud_marca = strlen(marca);
    size_t longitud_cierre = strlen(cierre);

    char *p = texto;
    char *final_texto = texto + longitud_texto;

    while (p < final_texto) {
        char *inicio = strstr(p, marca);

        if (!inicio) {
            if (!agregar(&resultado, &total, p,
                         (size_t)(final_texto - p)))
                goto error;
            break;
        }

        // Añadir el HTML anterior a la directiva
        if (!agregar(&resultado, &total, p,
                     (size_t)(inicio - p)))
            goto error;

        char *nombre = inicio + longitud_marca;
        char *fin = strstr(nombre, cierre);

        if (!fin) goto error;

        size_t longitud_nombre = (size_t)(fin - nombre);

        if (longitud_nombre == 0 ||
            longitud_nombre >= PATH_MAX)
            goto error;

        char archivo_incluido[PATH_MAX];

        memcpy(archivo_incluido, nombre, longitud_nombre);
        archivo_incluido[longitud_nombre] = '\0';

        // Rechazar rutas absolutas y barras de Windows
        if (archivo_incluido[0] == '/' ||
            strchr(archivo_incluido, '\\'))
            goto error;

        // Obtener el directorio del archivo actual
        char directorio[PATH_MAX];

        snprintf(directorio, sizeof(directorio),
                 "%s", ruta_real);

        char *ultima_barra = strrchr(directorio, '/');

        if (!ultima_barra) goto error;

        *ultima_barra = '\0';

        // Construir ruta relativa al HTML actual
        char destino[PATH_MAX];

        int n = snprintf(
            destino,
            sizeof(destino),
            "%s/%s",
            directorio,
            archivo_incluido
        );

        if (n < 0 || (size_t)n >= sizeof(destino))
            goto error;

        // Procesar recursivamente el archivo incluido
        char *contenido = NULL;
        size_t longitud_contenido = 0;

        if (!procesar_html(
                destino,
                raiz,
                profundidad + 1,
                &contenido,
                &longitud_contenido
            ))
            goto error;

        // Insertar contenido en el HTML resultante
        int correcto = agregar(
            &resultado,
            &total,
            contenido,
            longitud_contenido
        );

        free(contenido);

        if (!correcto) goto error;

        // Continuar después de la directiva
        p = fin + longitud_cierre;
    }

    free(texto);

    if (!resultado) {
        resultado = malloc(1);
        if (!resultado) return 0;
        resultado[0] = '\0';
    }

    *salida = resultado;
    *longitud_salida = total;

    return 1;

error:
    fprintf(stderr,
            "Error procesando inclusion en: %s\n",
            ruta_real);

    free(texto);
    free(resultado);

    return 0;
}

// Enviar errores HTTP
void enviar_error(
    int cliente,
    int codigo,
    const char *mensaje,
    int solo_cabeceras
) {
    char cuerpo[512];

    int longitud = snprintf(
        cuerpo,
        sizeof(cuerpo),
        "<!doctype html>"
        "<html lang=\"es\">"
        "<meta charset=\"utf-8\">"
        "<title>Error %d</title>"
        "<h1>%d %s</h1>"
        "</html>",
        codigo,
        codigo,
        mensaje
    );

    char cabecera[1024];

    snprintf(
        cabecera,
        sizeof(cabecera),
        "HTTP/1.1 %d %s\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "\r\n",
        codigo,
        mensaje,
        longitud
    );

    enviar_todo(cliente, cabecera, strlen(cabecera));

    if (!solo_cabeceras)
        enviar_todo(cliente, cuerpo, (size_t)longitud);
}

// Servir archivos HTML procesados o archivos estáticos
void servir_archivo(
    int cliente,
    const char *ruta,
    const char *raiz,
    int solo_cabeceras
) {
    const char *ext = strrchr(ruta, '.');

    int es_html = ext &&
        (!strcmp(ext, ".html") || !strcmp(ext, ".htm"));

    // HTML: procesar directivas antes de enviar
    if (es_html) {
        char *contenido = NULL;
        size_t longitud = 0;

        if (!procesar_html(
                ruta,
                raiz,
                0,
                &contenido,
                &longitud
            )) {
            enviar_error(
                cliente,
                500,
                "Internal Server Error",
                solo_cabeceras
            );
            return;
        }

        char cabecera[1024];

        snprintf(
            cabecera,
            sizeof(cabecera),
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            "Content-Length: %zu\r\n"
            "Connection: close\r\n"
            "\r\n",
            longitud
        );

        if (enviar_todo(cliente, cabecera, strlen(cabecera)) &&
            !solo_cabeceras)
            enviar_todo(cliente, contenido, longitud);

        free(contenido);
        return;
    }

    // Otros archivos: servir sin modificaciones
    FILE *archivo = fopen(ruta, "rb");

    if (!archivo) {
        enviar_error(cliente, 404, "Not Found", solo_cabeceras);
        return;
    }

    struct stat info;

    if (fstat(fileno(archivo), &info) != 0 ||
        !S_ISREG(info.st_mode)) {
        fclose(archivo);
        enviar_error(cliente, 403, "Forbidden", solo_cabeceras);
        return;
    }

    char cabecera[1024];

    snprintf(
        cabecera,
        sizeof(cabecera),
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %lld\r\n"
        "Connection: close\r\n"
        "\r\n",
        tipo_mime(ruta),
        (long long)info.st_size
    );

    if (!enviar_todo(cliente, cabecera, strlen(cabecera))) {
        fclose(archivo);
        return;
    }

    if (!solo_cabeceras) {
        char buffer[BUFFER];
        size_t leidos;

        while ((leidos = fread(
                    buffer, 1, sizeof(buffer), archivo
                )) > 0) {
            if (!enviar_todo(cliente, buffer, leidos))
                break;
        }
    }

    fclose(archivo);
}

int main(void) {
    // Evitar que una desconexión del navegador cierre el servidor
    signal(SIGPIPE, SIG_IGN);

    char raiz[PATH_MAX];

    if (!realpath("web", raiz)) {
        perror("No existe la carpeta web");
        return 1;
    }

    struct stat info_raiz;

    if (stat(raiz, &info_raiz) != 0 ||
        !S_ISDIR(info_raiz.st_mode)) {
        fprintf(stderr, "web no es un directorio\n");
        return 1;
    }

    int servidor = socket(AF_INET, SOCK_STREAM, 0);

    if (servidor < 0) {
        perror("socket");
        return 1;
    }

    int opcion = 1;

    setsockopt(
        servidor,
        SOL_SOCKET,
        SO_REUSEADDR,
        &opcion,
        sizeof(opcion)
    );

    struct sockaddr_in direccion = {0};

    direccion.sin_family = AF_INET;
    direccion.sin_port = htons(PUERTO);
    direccion.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (bind(
            servidor,
            (struct sockaddr *)&direccion,
            sizeof(direccion)
        ) < 0) {
        perror("bind");
        close(servidor);
        return 1;
    }

    if (listen(servidor, 10) < 0) {
        perror("listen");
        close(servidor);
        return 1;
    }

    printf("Servidor: http://localhost:%d\n", PUERTO);
    printf("Directorio: %s\n", raiz);
    printf("Directiva: <#incluir \"archivo.html\" #>\n");
    fflush(stdout);

    while (1) {
        int cliente = accept(servidor, NULL, NULL);

        if (cliente < 0) {
            if (errno == EINTR) continue;
            perror("accept");
            continue;
        }

        char peticion[4096] = {0};

        ssize_t recibidos = recv(
            cliente,
            peticion,
            sizeof(peticion) - 1,
            0
        );

        if (recibidos <= 0) {
            close(cliente);
            continue;
        }

        char metodo[16] = {0};
        char url[2048] = {0};

        if (sscanf(
                peticion,
                "%15s %2047s",
                metodo,
                url
            ) != 2) {
            enviar_error(cliente, 400, "Bad Request", 0);
            close(cliente);
            continue;
        }

        int es_head = strcmp(metodo, "HEAD") == 0;

        printf("%s %s\n", metodo, url);
        fflush(stdout);

        if (strcmp(metodo, "GET") != 0 && !es_head) {
            enviar_error(
                cliente,
                405,
                "Method Not Allowed",
                0
            );
            close(cliente);
            continue;
        }

        // Eliminar parámetros GET y fragmentos
        char *fin_url = strpbrk(url, "?#");
        if (fin_url) *fin_url = '\0';

        // Comprobar ruta
        if (url[0] != '/' ||
            strstr(url, "..") ||
            strchr(url, '\\')) {
            enviar_error(
                cliente, 403, "Forbidden", es_head
            );
            close(cliente);
            continue;
        }

        // Página de inicio
        if (strcmp(url, "/") == 0)
            strcpy(url, "/index.html");

        char candidata[PATH_MAX];

        int n = snprintf(
            candidata,
            sizeof(candidata),
            "%s%s",
            raiz,
            url
        );

        if (n < 0 || (size_t)n >= sizeof(candidata)) {
            enviar_error(
                cliente, 414, "URI Too Long", es_head
            );
            close(cliente);
            continue;
        }

        char ruta[PATH_MAX];

        if (!realpath(candidata, ruta)) {
            enviar_error(
                cliente, 404, "Not Found", es_head
            );
            close(cliente);
            continue;
        }

        if (!dentro_raiz(ruta, raiz)) {
            enviar_error(
                cliente, 403, "Forbidden", es_head
            );
            close(cliente);
            continue;
        }

        struct stat info;

        if (stat(ruta, &info) != 0) {
            enviar_error(
                cliente, 404, "Not Found", es_head
            );
            close(cliente);
            continue;
        }

        if (S_ISDIR(info.st_mode)) {
            char indice[PATH_MAX];

            n = snprintf(
                indice,
                sizeof(indice),
                "%s/index.html",
                ruta
            );

            if (n < 0 || (size_t)n >= sizeof(indice)) {
                enviar_error(
                    cliente, 414, "URI Too Long", es_head
                );
                close(cliente);
                continue;
            }

            char indice_real[PATH_MAX];

            if (!realpath(indice, indice_real)) {
                enviar_error(
                    cliente, 404, "Not Found", es_head
                );
            } else if (!dentro_raiz(indice_real, raiz)) {
                enviar_error(
                    cliente, 403, "Forbidden", es_head
                );
            } else {
                servir_archivo(
                    cliente,
                    indice_real,
                    raiz,
                    es_head
                );
            }
        } else {
            servir_archivo(
                cliente,
                ruta,
                raiz,
                es_head
            );
        }

        close(cliente);
    }

    close(servidor);
    return 0;
}
