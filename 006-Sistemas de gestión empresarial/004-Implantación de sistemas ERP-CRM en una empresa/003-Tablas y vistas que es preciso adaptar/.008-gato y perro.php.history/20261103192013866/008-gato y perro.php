<?php

class Gato {

    public function __construct($miedad,$micolor) {
        $this->edad = $miedad;
        $this->color = $micolor;
    }

}

class Perro {

    public function __construct($miedad,$micolor) {
        $this->edad = $miedad;
        $this->color = $micolor;
    }

}

$micifu = new Gato(0,"naranja");
var_dump($micifu);

?>