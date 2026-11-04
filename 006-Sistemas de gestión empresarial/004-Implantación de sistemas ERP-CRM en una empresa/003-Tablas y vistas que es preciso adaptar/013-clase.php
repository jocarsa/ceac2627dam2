
<?php

abstract class Vista {

    protected $titulo;

    public function __construct($titulo) {
        $this->titulo = $titulo;
    }

    abstract public function renderizar();

    protected function escapar($texto) {
        return htmlspecialchars(
            (string)$texto,
            ENT_QUOTES,
            'UTF-8'
        );
    }

}

class Tabla extends Vista {

    private $columnas;
    private $filas;

    public function __construct($titulo, $columnas, $filas) {
        parent::__construct($titulo);
        $this->columnas = $columnas;
        $this->filas = $filas;
    }

    public function renderizar() {
        $html = "<h2>".$this->escapar($this->titulo)."</h2>";
        $html .= "<table><thead><tr>";

        foreach ($this->columnas as $columna) {
            $html .= "<th>".$this->escapar($columna)."</th>";
        }

        $html .= "</tr></thead><tbody>";

        foreach ($this->filas as $fila) {
            $html .= "<tr>";

            foreach ($fila as $celda) {
                $html .= "<td>".$this->escapar($celda)."</td>";
            }

            $html .= "</tr>";
        }

        $html .= "</tbody></table>";

        return $html;
    }

}

class Calendario extends Vista {

    private $dias;

    public function __construct($titulo, $dias = 30) {
        parent::__construct($titulo);
        $this->dias = $dias;
    }

    public function renderizar() {
        $html = "<h2>".$this->escapar($this->titulo)."</h2>";
        $html .= "<section class='calendario'>";

        for ($i = 1; $i <= $this->dias; $i++) {
            $html .= "<article>".$i."</article>";
        }

        $html .= "</section>";

        return $html;
    }

}

?>

<?php

$productos = new Tabla(
    "Productos jocarsa",
    ["Producto jocarsa", "Descripción", "Color"],
    [
        ["jocarsa | dual", "Aplicación para dualizar", "indigo"],
        ["jocarsa | ia", "Inteligencia artificial", "lightskyblue"],
        ["jocarsa | ventas", "Gestión comercial", "sandybrown"],
        ["jocarsa | calificaciones", "Gestión académica", "greenyellow"]
    ]
);

$calendario = new Calendario("Noviembre", 30);

echo $productos->renderizar();
echo $calendario->renderizar();

?>
