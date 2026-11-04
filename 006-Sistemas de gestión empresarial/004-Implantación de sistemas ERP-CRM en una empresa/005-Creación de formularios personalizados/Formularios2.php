
<?php

class Formularios {

    private $configuracion;

    public function __construct($json) {
        $this->configuracion = is_string($json)
            ? json_decode($json, true, 512, JSON_THROW_ON_ERROR)
            : $json;
    }

    private function escapar($valor) {
        return htmlspecialchars(
            (string)$valor,
            ENT_QUOTES,
            'UTF-8'
        );
    }

    private function atributos($campo, $permitidos) {
        $html = '';

        foreach ($permitidos as $atributo) {
            if (isset($campo[$atributo])) {
                $html .= ' '.$atributo.'="'.
                    $this->escapar($campo[$atributo]).'"';
            }
        }

        if (!empty($campo['required'])) {
            $html .= ' required';
        }

        return $html;
    }

    private function entero($tipo) {

        $limites = [
            'TINYINT'   => [-128, 127, 255],
            'SMALLINT'  => [-32768, 32767, 65535],
            'MEDIUMINT' => [-8388608, 8388607, 16777215],
            'INT'       => [-2147483648, 2147483647, 4294967295],
            'BIGINT'    => [
                '-9223372036854775808',
                '9223372036854775807',
                '18446744073709551615'
            ]
        ];

        $sinSigno = str_contains($tipo, 'UNSIGNED');

        $base = preg_replace(
            '/\s+(UNSIGNED|SIGNED)\b/i',
            '',
            $tipo
        );

        $base = preg_replace('/\(\d+\)/', '', $base);
        $base = trim($base);

        if ($base === 'INTEGER') {
            $base = 'INT';
        }

        if (!isset($limites[$base])) {
            return null;
        }

        [$min, $max, $maxUnsigned] = $limites[$base];

        return [
            'min' => $sinSigno ? 0 : $min,
            'max' => $sinSigno ? $maxUnsigned : $max,
            'step' => 1
        ];
    }

    private function decimal($tipo) {

        $resultado = [
            'step' => 'any'
        ];

        if (preg_match(
            '/^(DECIMAL|NUMERIC)\((\d+),(\d+)\)/',
            $tipo,
            $coincidencias
        )) {

            $precision = (int)$coincidencias[2];
            $decimales = (int)$coincidencias[3];

            if ($precision < 1 || $precision > 65 ||
                $decimales > 30 || $decimales > $precision) {
                throw new InvalidArgumentException(
                    'Precisión DECIMAL no válida'
                );
            }

            $enteros = $precision - $decimales;

            $maximo = str_repeat('9', $enteros);

            if ($enteros === 0) {
                $maximo = '0';
            }

            if ($decimales > 0) {
                $maximo .= '.'.
                    str_repeat('9', $decimales);
            }

            $resultado['min'] = '-'.$maximo;
            $resultado['max'] = $maximo;

            $resultado['step'] = $decimales > 0
                ? '0.'.str_repeat('0', $decimales - 1).'1'
                : '1';

            if (str_contains($tipo, 'UNSIGNED')) {
                $resultado['min'] = 0;
            }
        }

        return $resultado;
    }

    private function longitudTexto($tipo) {

        if (preg_match(
            '/^(CHAR|VARCHAR)\((\d+)\)/',
            $tipo,
            $coincidencias
        )) {
            return (int)$coincidencias[2];
        }

        return match ($tipo) {
            'TINYTEXT' => 255,
            'TEXT' => 65535,
            'MEDIUMTEXT' => 16777215,
            'LONGTEXT' => 4294967295,
            default => null
        };
    }

    private function limiteBinario($tipo) {

        if (preg_match(
            '/^(BINARY|VARBINARY)\((\d+)\)/',
            $tipo,
            $coincidencias
        )) {
            return (int)$coincidencias[2];
        }

        if (preg_match(
            '/^BIT\((\d+)\)/',
            $tipo,
            $coincidencias
        )) {
            return (int)ceil($coincidencias[1] / 8);
        }

        return match ($tipo) {
            'TINYBLOB' => 255,
            'BLOB' => 65535,
            'MEDIUMBLOB' => 16777215,
            'LONGBLOB' => 4294967295,
            default => null
        };
    }

    private function opciones($campo, $tipo) {

        if (isset($campo['opciones'])) {
            return $campo['opciones'];
        }

        // Soporte para ENUM('a','b') y SET('a','b')
        if (preg_match(
            '/^(ENUM|SET)\((.*)\)$/is',
            $tipo,
            $coincidencias
        )) {
            $interior = $coincidencias[2];

            preg_match_all(
                "/'((?:[^'\\\\]|\\\\.)*)'/",
                $interior,
                $valores
            );

            return array_map(
                fn($v) => stripcslashes($v),
                $valores[1]
            );
        }

        return [];
    }

    public function generar() {

        $config = $this->configuracion;

        $metodo = strtoupper($config['metodo'] ?? 'POST');

        if (!in_array($metodo, ['GET', 'POST'], true)) {
            $metodo = 'POST';
        }

        $accion = $this->escapar($config['accion'] ?? '');

        $html = '<form action="'.$accion.
            '" method="'.$metodo.'"';

        $tieneArchivos = false;

        foreach ($config['campos'] ?? [] as $campo) {
            $tipo = strtoupper(trim($campo['tipo'] ?? 'TEXT'));

            if ($this->limiteBinario($tipo) !== null ||
                $tipo === 'FILE') {
                $tieneArchivos = true;
            }
        }

        if ($tieneArchivos) {
            if ($metodo !== 'POST') {
                throw new InvalidArgumentException(
                    'Los archivos requieren método POST'
                );
            }
            $html .= ' enctype="multipart/form-data"';
        }

        $html .= '>';

        foreach ($config['campos'] ?? [] as $campo) {

            $tipo = strtoupper(trim($campo['tipo'] ?? 'TEXT'));
            $nombre = $this->escapar($campo['nombre'] ?? '');
            $titulo = $this->escapar($campo['titulo'] ?? '');
            $valor = $this->escapar($campo['valor'] ?? '');

            $html .= '<fieldset>';
            $html .= '<legend>'.$titulo.'</legend>';

            // ENTEROS
            $entero = $this->entero($tipo);

            if ($entero !== null) {

                $atributos = array_merge($entero, $campo);

                $html .= '<input type="number" name="'.
                    $nombre.'" value="'.$valor.'"';

                $html .= $this->atributos(
                    $atributos,
                    ['min', 'max', 'step', 'placeholder']
                );

                $html .= '>';

            }

            // BOOLEANOS
            elseif (in_array($tipo, ['BOOL', 'BOOLEAN'], true)) {

                $checked = !empty($campo['valor'])
                    ? ' checked'
                    : '';

                $html .= '<input type="hidden" name="'.
                    $nombre.'" value="0">';

                $html .= '<input type="checkbox" name="'.
                    $nombre.'" value="1"'.$checked.'>';

            }

            // DECIMALES
            elseif (preg_match(
                '/^(FLOAT|DOUBLE|DOUBLE PRECISION|REAL|DECIMAL|NUMERIC)\b/',
                $tipo
            )) {

                $atributos = array_merge(
                    $this->decimal($tipo),
                    $campo
                );

                $html .= '<input type="number" name="'.
                    $nombre.'" value="'.$valor.'"';

                $html .= $this->atributos(
                    $atributos,
                    ['min', 'max', 'step', 'placeholder']
                );

                $html .= '>';

            }

            // ENUM Y SET
            elseif (preg_match('/^(ENUM|SET)\b/', $tipo)) {

                $opciones = $this->opciones($campo, $tipo);
                $multiple = str_starts_with($tipo, 'SET');

                $seleccionados = $campo['valor'] ?? [];

                if (!is_array($seleccionados)) {
                    $seleccionados = $multiple
                        ? explode(',', (string)$seleccionados)
                        : [(string)$seleccionados];
                }

                foreach ($opciones as $opcion) {

                    $op = $this->escapar($opcion);

                    $checked = in_array(
                        (string)$opcion,
                        array_map('strval', $seleccionados),
                        true
                    ) ? ' checked' : '';

                    $html .= '<label>';

                    $html .= '<input type="'.
                        ($multiple ? 'checkbox' : 'radio').
                        '" name="'.$nombre.
                        ($multiple ? '[]' : '').
                        '" value="'.$op.'"'.$checked.'>';

                    $html .= ' '.$op.'</label><br>';
                }

            }

            // FECHAS
            elseif (in_array(
                $tipo,
                ['DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR'],
                true
            )) {

                $htmlTipo = match ($tipo) {
                    'DATE' => 'date',
                    'TIME' => 'time',
                    'DATETIME', 'TIMESTAMP' => 'datetime-local',
                    'YEAR' => 'number'
                };

                $valorFecha = $campo['valor'] ?? '';

                if (in_array($tipo, ['DATETIME', 'TIMESTAMP'])) {
                    $valorFecha = str_replace(' ', 'T', $valorFecha);
                }

                $atributos = $campo;

                if ($tipo === 'YEAR') {
                    $atributos = array_merge([
                        'min' => 1901,
                        'max' => 2155,
                        'step' => 1
                    ], $campo);
                }

                if ($tipo === 'TIME' ||
                    $tipo === 'DATETIME' ||
                    $tipo === 'TIMESTAMP') {
                    $atributos = array_merge([
                        'step' => 1
                    ], $campo);
                }

                $html .= '<input type="'.$htmlTipo.
                    '" name="'.$nombre.'" value="'.
                    $this->escapar($valorFecha).'"';

                $html .= $this->atributos(
                    $atributos,
                    ['min', 'max', 'step']
                );

                $html .= '>';

            }

            // BINARIOS
            elseif (($limite = $this->limiteBinario($tipo)) !== null ||
                    $tipo === 'FILE') {

                $limite = $campo['max_bytes'] ?? $limite;

                $html .= '<input type="file" name="'.
                    $nombre.'"';

                if (isset($campo['accept'])) {
                    $html .= ' accept="'.
                        $this->escapar($campo['accept']).'"';
                }

                if (!empty($campo['required'])) {
                    $html .= ' required';
                }

                $html .= '>';

                if ($limite !== null) {
                    $html .= '<small>Máximo: '.
                        $this->escapar($limite).
                        ' bytes</small>';
                }

            }

            // SELECT
            elseif ($tipo === 'SELECT') {

                $html .= '<select name="'.$nombre.'">';

                foreach ($campo['opciones'] ?? [] as $opcion) {
                    $op = $this->escapar($opcion);
                    $selected = (string)$opcion ===
                        (string)($campo['valor'] ?? '')
                        ? ' selected'
                        : '';

                    $html .= '<option value="'.$op.'"'.
                        $selected.'>'.$op.'</option>';
                }

                $html .= '</select>';

            }

            // DATALIST
            elseif ($tipo === 'DATALIST') {

                $id = 'lista_'.preg_replace(
                    '/[^a-zA-Z0-9_-]/',
                    '_',
                    $campo['nombre'] ?? ''
                );

                $html .= '<input type="text" name="'.
                    $nombre.'" list="'.$id.
                    '" value="'.$valor.'">';

                $html .= '<datalist id="'.$id.'">';

                foreach ($campo['opciones'] ?? [] as $opcion) {
                    $html .= '<option value="'.
                        $this->escapar($opcion).'">';
                }

                $html .= '</datalist>';

            }

            // PROGRESS
            elseif ($tipo === 'PROGRESS') {

                $max = $this->escapar($campo['max'] ?? 1);

                $html .= '<progress value="'.$valor.
                    '" max="'.$max.'"></progress>';

            }

            // TEXTO
            elseif (($longitud = $this->longitudTexto($tipo)) !== null ||
                    in_array($tipo, ['TEXT', 'TEXTAREA'], true)) {

                $longitud = $campo['maxlength'] ?? $longitud;

                $atributos = $campo;

                if ($longitud !== null) {
                    $atributos['maxlength'] = $longitud;
                }

                $html .= '<input type="text" name="'.
                    $nombre.'" value="'.$valor.'"';

                $html .= $this->atributos(
                    $atributos,
                    ['maxlength', 'minlength', 'placeholder']
                );

                $html .= '>';

            }

            // HTML NATIVO
            else {

                $tipos = [
                    'TEXT', 'NUMBER', 'COLOR', 'RANGE',
                    'PASSWORD', 'EMAIL', 'URL', 'TEL',
                    'SEARCH', 'HIDDEN'
                ];

                if (in_array($tipo, $tipos, true)) {

                    $html .= '<input type="'.
                        strtolower($tipo).
                        '" name="'.$nombre.
                        '" value="'.$valor.'"';

                    $html .= $this->atributos(
                        $campo,
                        [
                            'min', 'max', 'step',
                            'maxlength', 'placeholder'
                        ]
                    );

                    $html .= '>';
                }
            }

            $html .= '</fieldset>';
        }

        $textoBoton = $this->escapar(
            $config['boton'] ?? 'Enviar'
        );

        $html .= '<button type="submit">'.
            $textoBoton.'</button>';

        $html .= '</form>';

        return $html;
    }
}

?>
