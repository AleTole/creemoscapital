<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');
$url = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json?timezone=America%2FBogota';
$data = file_get_contents($url);
echo $data;
