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


function estilosJocarsaVistas(): string {
    return '<style>' . <<<'CSS'

:root{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#263445;background:#f3f6fa}
*{box-sizing:border-box}body{margin:0}.contenedor{max-width:1150px;margin:auto;padding:30px 20px}
header{display:flex;align-items:center;justify-content:space-between;gap:15px;flex-wrap:wrap;margin-bottom:24px}
header h1{margin:0;font-size:24px}nav{display:flex;gap:7px;flex-wrap:wrap}nav a{padding:9px 14px;border-radius:8px;text-decoration:none;background:white;color:#42526a;border:1px solid #dce3ed;font-size:14px}
nav a.activo{background:#263445;color:white;border-color:#263445}
.vista{background:white;border:1px solid #dce3ed;border-radius:14px;padding:22px;box-shadow:0 4px 18px #2533480a}
h2{font-size:20px;margin:0 0 12px}.subtitulo{margin:0 0 20px;color:#637389}
.tabla-scroll{overflow:auto}table{width:100%;border-collapse:collapse;text-align:left}th,td{padding:13px;border-bottom:1px solid #e5eaf1}th{background:#f2f5f9}
.cuadricula{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:3px}.dia-nombre{text-align:center;padding:9px 0;color:#69788c;font-size:12px;font-weight:700}.dia{min-height:80px;border:1px solid #e7edf4;border-radius:5px;padding:8px;background:#fbfcfe}.dia.vacio{background:#f5f7fa}.dia.hoy{background:#dceefe;border-color:#83bdf2;font-weight:700}
.anual{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.mini-mes{border:1px solid #e1e7ef;border-radius:10px;padding:12px}.mini-mes h3{font-size:14px;margin:0 0 8px}.mini-mes .dia{min-height:28px;padding:5px;font-size:11px;text-align:center}.mini-mes .dia-nombre{padding:5px 0;font-size:10px}
.semana{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px}.semana article{min-height:200px;border:1px solid #e1e7ef;border-radius:7px;padding:10px;display:flex;flex-direction:column;gap:12px}.semana strong{font-size:12px}.semana span{font-size:20px}
.horas{border:1px solid #e1e7ef;border-radius:8px;overflow:hidden}.horas article{height:48px;border-bottom:1px solid #e7edf4;padding:12px}.horas article:last-child{border:0}.horas span{color:#637389;font-size:13px}
@media(max-width:750px){.anual{grid-template-columns:repeat(2,minmax(0,1fr))}.semana{overflow-x:auto;grid-template-columns:repeat(7,minmax(100px,1fr))}.dia{min-height:50px}}
@media(max-width:480px){.anual{grid-template-columns:1fr}.dia{min-height:40px;padding:4px}}

CSS
    . '</style>';
}
