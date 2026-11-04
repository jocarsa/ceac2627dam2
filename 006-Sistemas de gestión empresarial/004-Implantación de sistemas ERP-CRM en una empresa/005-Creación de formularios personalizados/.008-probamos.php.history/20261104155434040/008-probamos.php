
<?php

require_once 'Formularios2.php';

$configuracion = [
    'accion' => 'procesar.php',
    'metodo' => 'POST',
    'boton' => 'Guardar registro',

    'campos' => [

        [
            'tipo' => 'VARCHAR(100)',
            'nombre' => 'nombre',
            'titulo' => 'Nombre completo',
            'required' => true
        ],

        [
            'tipo' => 'TINYINT UNSIGNED',
            'nombre' => 'edad',
            'titulo' => 'Edad'
        ],

        [
            'tipo' => 'INT',
            'nombre' => 'cantidad',
            'titulo' => 'Cantidad'
        ],

        [
            'tipo' => 'DECIMAL(10,2)',
            'nombre' => 'precio',
            'titulo' => 'Precio',
            'valor' => '19.99'
        ],

        [
            'tipo' => 'FLOAT',
            'nombre' => 'temperatura',
            'titulo' => 'Temperatura',
            'min' => -100,
            'max' => 100
        ],

        [
            'tipo' => 'ENUM',
            'nombre' => 'estado',
            'titulo' => 'Estado',
            'opciones' => [
                'Pendiente',
                'En proceso',
                'Completado'
            ]
        ],

        [
            'tipo' => 'SET',
            'nombre' => 'permisos',
            'titulo' => 'Permisos',
            'opciones' => [
                'Leer',
                'Escribir',
                'Eliminar'
            ]
        ],

        [
            'tipo' => 'DATE',
            'nombre' => 'nacimiento',
            'titulo' => 'Fecha de nacimiento'
        ],

        [
            'tipo' => 'DATETIME',
            'nombre' => 'registro',
            'titulo' => 'Fecha de registro'
        ],

        [
            'tipo' => 'YEAR',
            'nombre' => 'fabricacion',
            'titulo' => 'Año de fabricación'
        ],

        [
            'tipo' => 'BOOLEAN',
            'nombre' => 'activo',
            'titulo' => 'Activo',
            'valor' => 1
        ],

        [
            'tipo' => 'BLOB',
            'nombre' => 'documento',
            'titulo' => 'Documento adjunto'
        ],

        [
            'tipo' => 'VARBINARY(1024)',
            'nombre' => 'archivo',
            'titulo' => 'Archivo binario'
        ]
    ]
];

$formulario = new Formularios($configuracion);

echo $formulario->generar();

?>
