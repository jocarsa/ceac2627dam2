<?php
require_once __DIR__ . "/jocarsa-vistas-clases.php";

$fecha = new DateTimeImmutable('2026-11-03');
$productos = new Tabla('Productos jocarsa', ['Producto jocarsa','Descripción','Color'], [
    ['jocarsa | dual','Aplicación para dualizar','indigo'],
    ['jocarsa | ia','Inteligencia artificial','lightskyblue'],
    ['jocarsa | ventas','Gestión comercial','sandybrown'],
    ['jocarsa | calificaciones','Gestión académica','greenyellow'],
]);
$vistas = [
    'tabla' => $productos,
    'anual' => new CalendarioAnual('Calendario anual', $fecha),
    'mensual' => new CalendarioMensual('Calendario mensual', $fecha),
    'semanal' => new CalendarioSemanal('Calendario semanal', $fecha),
    'diario' => new CalendarioDiario('Calendario diario', $fecha),
];
$seleccion = $_GET['vista'] ?? 'mensual';
if (!array_key_exists($seleccion, $vistas)) $seleccion = 'mensual';
?>
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>jocarsa | vistas</title>
<?= estilosJocarsaVistas() ?>
</head>
<body>
<div class="contenedor">
<header>
<h1>jocarsa | vistas</h1>
<nav>
<?php foreach (['tabla'=>'Tabla','anual'=>'Anual','mensual'=>'Mensual','semanal'=>'Semanal','diario'=>'Diario'] as $clave=>$etiqueta): ?>
<a href="?vista=<?= urlencode($clave) ?>" class="<?= $seleccion === $clave ? 'activo' : '' ?>"><?= htmlspecialchars($etiqueta) ?></a>
<?php endforeach; ?>
</nav>
</header>
<main><?= $vistas[$seleccion]->renderizar() ?></main>
</div>
</body>
</html>
