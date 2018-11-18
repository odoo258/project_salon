<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');


require_once("../OdooConnection.class.php");
$odooConnection = new OdooConnection();

$response = array(
    'CONTRACT_ID' => '',
    'INVOICE_LINE_ID' => '',
    'ERROR' => ''
);

$order              = (int)$_POST['order_id'];
$customer           = (int)$_POST['partner_id'];
@$contractName      = $_POST['product_contractName'];
@$productId         = (int)$_POST['product_contract_id'];
@$productPrice      = (int)$_POST['product_contract_price'];

if (!isset($contractName)) {
    $product = $odooConnection->getProduct($productId);
    $contractName = $product['display_name'];
    $productPrice = $product['lst_price'];
}

$contractId = $odooConnection->createContract($order, $contractName, $customer);

if ($contractId) {
    $response['CONTRACT_ID'] = $contractId;

	$invoiceId = $odooConnection->createInvoiceLine($contractId, $productId, $productPrice, 'administrativo');
	if ($invoiceId) {
    	$response['INVOICE_LINE_ID'] = $invoiceId;
	} else {
    	$response['ERROR'] = "Erro ao criar contrato. Erro no invoice.";
	}
	
} else {
    $response['ERROR'] = "Erro ao criar contrato.";
}

echo json_encode($response);
?>