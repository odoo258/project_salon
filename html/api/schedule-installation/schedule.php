<?php
header('Access-Control-Allow-Origin: *');
//header('Content-Type: charset=utf-8');

require_once("../OdooConnection.class.php");
$odooConnection = new OdooConnection();

$order      = (int)$_POST['order_id'];
$customer   = (int)$_POST['partner_id'];
$date       = $_POST['dataInstalacao'];
$dateDB     = implode("-",array_reverse(explode("/",$date)));
$company    = $_POST['localInstalacao'];
$time       = $_POST['horaInstalacao'];

$id = $odooConnection->createTask($order, $customer, $company, $dateDB, $time);

echo $id;

?>