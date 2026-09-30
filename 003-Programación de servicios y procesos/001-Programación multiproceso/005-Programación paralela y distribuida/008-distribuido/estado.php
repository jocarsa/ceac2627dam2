<?php
header('Content-Type: application/json; charset=utf-8');
$cola = file_exists('cola.json') ? json_decode(file_get_contents('cola.json'), true) : [];
$estado = ['pendiente'=>0, 'asignado'=>0, 'terminado'=>0];
$total = [];
foreach ($cola as $p) {
    if (isset($estado[$p['estado']])) $estado[$p['estado']]++;
    if ($p['estado'] === 'terminado' && is_array($p['resultado'])) {
        foreach ($p['resultado'] as $numero=>$cantidad) {
            $total[$numero] = ($total[$numero] ?? 0) + $cantidad;
        }
    }
}
$max = $total ? max($total) : 0;
$masFrecuentes = [];
foreach ($total as $numero=>$cantidad) if ($cantidad === $max) $masFrecuentes[] = (int)$numero;
ksort($total, SORT_NUMERIC);
echo json_encode(['estado'=>$estado, 'frecuencias'=>$total, 'maximo'=>$max, 'mas_frecuentes'=>$masFrecuentes]);
