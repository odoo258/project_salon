<?php 
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');
header('content-type: application/json');

$response = array(
	'ERROR' => '',
);

require_once("../OdooConnection.class.php");
$odooConnection = new OdooConnection();

$invoiceId = $_POST['invoiceId'];
$invoice = $odooConnection->confirmInvoice($invoiceId);

echo json_encode($response);
?>