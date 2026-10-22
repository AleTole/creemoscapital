<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');

$url = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json?timezone=America%2FBogota';
$cacheFile = __DIR__ . '/.cache/calendar-cache.json';
$cacheMaxAge = 900; // 15 minutos

$context = stream_context_create(['http' => ['timeout' => 8]]);
$data = @file_get_contents($url, false, $context);

if ($data !== false && json_decode($data) !== null) {
    if (is_dir(dirname($cacheFile)) || @mkdir(dirname($cacheFile), 0755, true)) {
        @file_put_contents($cacheFile, $data);
    }
    echo $data;
    exit;
}

// Fuente caída o rate-limiteada: servir el último resultado bueno que tengamos.
if (file_exists($cacheFile)) {
    echo file_get_contents($cacheFile);
    exit;
}

http_response_code(503);
echo json_encode(['error' => 'Calendario no disponible temporalmente']);
