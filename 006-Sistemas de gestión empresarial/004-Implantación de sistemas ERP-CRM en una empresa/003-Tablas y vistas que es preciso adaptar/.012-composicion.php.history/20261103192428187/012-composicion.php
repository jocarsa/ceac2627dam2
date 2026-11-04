<?php

class Rueda {

    public $radio;

    public function __construct($miradio) {
        $this->radio = $miradio;
    }

}

class Coche {

    public $color;
    public $ruedas = [];

    public function __construct($micolor) {
        $this->color = $micolor;

        for ($i = 0; $i < 4; $i++) {
            $this->ruedas[] = new Rueda(17);
        }
    }

}

$micoche = new Coche("rojo");

var_dump($micoche);

?>