
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

    public function generar() {

        $config = $this->configuracion;

        $metodo = strtoupper($config['metodo'] ?? 'POST');
        if (!in_array($metodo, ['GET', 'POST'])) {
            $metodo = 'POST';
        }

        $accion = $this->escapar($config['accion'] ?? '');

        $html = '<form action="'.$accion.'" method="'.$metodo.'">';

        foreach ($config['campos'] ?? [] as $campo) {

            $tipo = $campo['tipo'] ?? 'text';
            $nombre = $this->escapar($campo['nombre'] ?? '');
            $titulo = $this->escapar($campo['titulo'] ?? '');
            $valor = $this->escapar($campo['valor'] ?? '');

            $html .= '<fieldset>';
            $html .= '<legend>'.$titulo.'</legend>';

            switch ($tipo) {

                case 'textarea':
                    $html .= '<textarea name="'.$nombre.'">'
                           .$valor.'</textarea>';
                    break;

                case 'select':
                    $html .= '<select name="'.$nombre.'">';

                    foreach ($campo['opciones'] ?? [] as $opcion) {
                        $op = $this->escapar($opcion);
                        $selected = ((string)$opcion === (string)($campo['valor'] ?? ''))
                            ? ' selected' : '';

                        $html .= '<option value="'.$op.'"'.$selected.'>'
                               .$op.'</option>';
                    }

                    $html .= '</select>';
                    break;

                case 'checkbox':
                case 'radio':

                    foreach ($campo['opciones'] ?? [] as $opcion) {
                        $op = $this->escapar($opcion);

                        $name = $tipo === 'checkbox'
                            ? $nombre.'[]'
                            : $nombre;

                        $html .= '<label>';
                        $html .= '<input type="'.$tipo.'" name="'.$name
                               .'" value="'.$op.'"> ';
                        $html .= $op;
                        $html .= '</label><br>';
                    }
                    break;

                case 'datalist':

                    $id = 'lista_'.preg_replace(
                        '/[^a-zA-Z0-9_-]/',
                        '_',
                        $campo['nombre'] ?? ''
                    );

                    $html .= '<input type="text" name="'.$nombre
                           .'" list="'.$id.'" value="'.$valor.'">';

                    $html .= '<datalist id="'.$id.'">';

                    foreach ($campo['opciones'] ?? [] as $opcion) {
                        $html .= '<option value="'
                               .$this->escapar($opcion).'">';
                    }

                    $html .= '</datalist>';
                    break;

                case 'progress':

                    $max = $this->escapar($campo['max'] ?? 1);
                    $html .= '<progress value="'.$valor
                           .'" max="'.$max.'"></progress>';
                    break;

                default:

                    $tipos = [
                        'text', 'number', 'date',
                        'time', 'color', 'range'
                    ];

                    if (in_array($tipo, $tipos)) {

                        $html .= '<input type="'.$tipo
                               .'" name="'.$nombre.'" value="'.$valor.'"';

                        foreach (['min', 'max', 'step', 'placeholder'] as $atributo) {
                            if (isset($campo[$atributo])) {
                                $html .= ' '.$atributo.'="'
                                       .$this->escapar($campo[$atributo]).'"';
                            }
                        }

                        if (!empty($campo['required'])) {
                            $html .= ' required';
                        }

                        $html .= '>';
                    }
            }

            $html .= '</fieldset>';
        }

        $textoBoton = $this->escapar(
            $config['boton'] ?? 'Enviar'
        );

        $html .= '<button type="submit">'
               .$textoBoton.'</button>';

        $html .= '</form>';

        return $html;
    }
}

?>
