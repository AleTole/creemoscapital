<?php
// Proxy del calendario económico (misma página, mismo origen: no necesita CORS abierto).
header('Content-Type: application/json');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: public, max-age=300');

$url = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json?timezone=America%2FBogota';
$cacheFile = __DIR__ . '/.cache/calendar-cache.json';
$cacheMaxAge = 900; // 15 minutos

// 1) Copia reciente: se sirve sin consultar la fuente externa (así las visitas no la saturan ni gastan tiempo del servidor)
if (is_file($cacheFile) && (time() - filemtime($cacheFile)) < $cacheMaxAge) {
    readfile($cacheFile);
    exit;
}

// 2) Copia vencida o inexistente: se consulta la fuente
$context = stream_context_create(['http' => ['timeout' => 8]]);
$data = @file_get_contents($url, false, $context);

if ($data !== false && json_decode($data) !== null) {
    if (is_dir(dirname($cacheFile)) || @mkdir(dirname($cacheFile), 0755, true)) {
        @file_put_contents($cacheFile, $data);
    }
    echo $data;
    exit;
}

// 3) Fuente caída o rate-limiteada: servir el último resultado bueno que tengamos, aunque sea viejo
if (is_file($cacheFile)) {
    readfile($cacheFile);
    exit;
}

http_response_code(503);
echo json_encode(['error' => 'Calendario no disponible temporalmente']);
