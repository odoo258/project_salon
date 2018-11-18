<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');
header('content-type: application/json');

$response = array(
    'ORDER_ID' => '',
    'ORDER_LINE_ID' => '',
    'ERROR' => ''
);

require_once("../OdooConnection.class.php");
$odooConnection = new OdooConnection();

$partnerId     = (int)$_POST['partner_id'];
$companyId     = (int)$_POST['company_id'];
$userId        = (int)$_POST['user_id'];
$productId     = (int)$_POST['product_id'];

$product = $odooConnection->getProduct($productId);

$orderId = $odooConnection->createOrder($partnerId, $companyId, $userId);

if ($orderId && is_numeric($orderId)) {
    $response['ORDER_ID'] = $orderId;

    foreach ($product['accessory_product_ids'] as $key => $accessoryId) {
        $orderLineId = $odooConnection->createOrderLine($orderId, $accessoryId);

        if ($orderLineId && is_numeric($orderLineId)) {
            $response['ORDER_LINE_ID'.$key] = $orderLineId;
        } else {
            $response['ERROR'] = "Erro na criação da linha do produto. " . print_r($orderLineId, true);
        }
    }

} else {
    $response['ERROR'] = "Erro ao criar venda. " . print_r($orderId, true);
}

echo json_encode($response);

?>