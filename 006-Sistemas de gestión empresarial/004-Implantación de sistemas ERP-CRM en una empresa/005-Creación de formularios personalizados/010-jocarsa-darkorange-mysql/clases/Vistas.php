<?php
// jocarsa | vistas — archivo único, PHP 8+
declare(strict_types=1);

abstract class Vista {
    public function __construct(protected string $titulo) {}
    abstract public function renderizar(): string;
    protected function escapar(string $texto): string {
        return htmlspecialchars($texto, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }
}

class Tabla extends Vista {
    public function __construct(string $titulo, private array $columnas, private array $filas) {
        parent::__construct($titulo);
    }
    public function renderizar(): string {
        $html = '<div class="vista"><h2>'.$this->escapar($this->titulo).'</h2><div class="tabla-scroll"><table><thead><tr>';
        foreach ($this->columnas as $columna) $html .= '<th>'.$this->escapar((string)$columna).'</th>';
        $html .= '</tr></thead><tbody>';
        foreach ($this->filas as $fila) {
            $html .= '<tr>';
            foreach ($this->columnas as $i => $_) {
                $valor = array_values($fila)[$i] ?? '';
                $html .= '<td>'.$this->escapar((string)$valor).'</td>';
            }
            $html .= '</tr>';
        }
        return $html.'</tbody></table></div></div>';
    }
}

abstract class Calendario extends Vista {
    protected DateTimeImmutable $fecha;
    private const DIAS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
    private const MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];

    public function __construct(string $titulo, ?DateTimeImmutable $fecha = null) {
        parent::__construct($titulo);
        $this->fecha = $fecha ?? new DateTimeImmutable('today');
    }
    protected function cabecera(): string { return '<h2>'.$this->escapar($this->titulo).'</h2>'; }
    protected function nombreMes(DateTimeImmutable $fecha): string {
        return self::MESES[(int)$fecha->format('n') - 1];
    }
    protected function diasSemana(): string {
        $html = '';
        foreach (self::DIAS as $dia) $html .= '<div class="dia-nombre">'.$dia.'</div>';
        return $html;
    }
    protected function cuadriculaMes(DateTimeImmutable $fecha): string {
        $inicio = $fecha->modify('first day of this month');
        $desplazamiento = (int)$inicio->format('N') - 1;
        $total = (int)$inicio->format('t');
        $hoy = (new DateTimeImmutable('today'))->format('Y-m-d');
        $html = '<div class="cuadricula">'.$this->diasSemana();
        for ($i=0; $i<$desplazamiento; $i++) $html .= '<div class="dia vacio"></div>';
        for ($d=1; $d<=$total; $d++) {
            $dia = $inicio->setDate((int)$inicio->format('Y'), (int)$inicio->format('n'), $d);
            $clase = $dia->format('Y-m-d') === $hoy ? ' hoy' : '';
            $html .= '<div class="dia'.$clase.'">'.$d.'</div>';
        }
        return $html.'</div>';
    }
}

class CalendarioAnual extends Calendario {
    public function renderizar(): string {
        $html = '<div class="vista">'.$this->cabecera().'<p class="subtitulo">'.$this->fecha->format('Y').'</p><div class="anual">';
        for ($m=1; $m<=12; $m++) {
            $fecha = $this->fecha->setDate((int)$this->fecha->format('Y'), $m, 1);
            $html .= '<div class="mini-mes"><h3>'.ucfirst($this->nombreMes($fecha)).'</h3>'.$this->cuadriculaMes($fecha).'</div>';
        }
        return $html.'</div></div>';
    }
}

class CalendarioMensual extends Calendario {
    public function renderizar(): string {
        return '<div class="vista">'.$this->cabecera().'<p class="subtitulo">'.ucfirst($this->nombreMes($this->fecha)).' de '.$this->fecha->format('Y').'</p>'.$this->cuadriculaMes($this->fecha).'</div>';
    }
}

class CalendarioSemanal extends Calendario {
    public function renderizar(): string {
        $lunes = $this->fecha->modify('-'.((int)$this->fecha->format('N')-1).' days');
        $html = '<div class="vista">'.$this->cabecera().'<p class="subtitulo">Semana del '.$lunes->format('d/m/Y').'</p><div class="semana">';
        foreach (['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'] as $i=>$nombre) {
            $dia = $lunes->modify('+'.$i.' days');
            $html .= '<article><strong>'.$nombre.'</strong><span>'.$dia->format('d/m').'</span></article>';
        }
        return $html.'</div></div>';
    }
}

class CalendarioDiario extends Calendario {
    public function renderizar(): string {
        $html = '<div class="vista">'.$this->cabecera().'<p class="subtitulo">'.$this->fecha->format('d/m/Y').'</p><div class="horas">';
        for ($h=0; $h<24; $h++) $html .= '<article><span>'.sprintf('%02d:00', $h).'</span></article>';
        return $html.'</div></div>';
    }
}

