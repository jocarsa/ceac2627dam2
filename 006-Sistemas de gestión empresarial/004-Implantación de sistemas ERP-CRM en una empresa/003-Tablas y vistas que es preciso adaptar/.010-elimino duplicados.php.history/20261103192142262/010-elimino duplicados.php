<?php

class Mamifero {

    public $edad;
    public $color;

    public function __construct($miedad, $micolor) {
        $this->edad = $miedad;
        $this->color = $micolor;
    }

}

class Gato extends Mamifero {

}

class Perro extends Mamifero {

}

$micifu = new Gato(0, "naranja");
var_dump($micifu);

?>