<?php
require_once("../TrackNMeBuilder.class.php");
require_once("../OdooConnection.class.php");
$odooConnection = new OdooConnection();
$trackNMe = TrackNMeBuilder::getInstance();

echo "<pre>";
$um 	= @$_GET['um'];
$dois 	= @$_GET['dois'];
$tres 	= @$_GET['tres'];

// $response = $trackNMe->getDeviceByImei('4700241467');
// $response = $odooConnection->getEntityById(21, 'project.task');
$response = $odooConnection->searchCompanies();

var_dump($response);
echo "</pre>";
?>