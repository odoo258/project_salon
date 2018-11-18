<?php
header('Access-Control-Allow-Origin: *');
//header('Content-Type: charset=utf-8');
require_once("../OdooConnection.class.php");
$odooConnection = new OdooConnection();

$order              = (int)$_POST['order_id'];
@$customer           = (int)$_POST['partner_id'];
@$contract_name      = $_POST['product_contract_name'];
@$product_cart_id    = (int)$_POST['product_cart_id'];
@$product_contract_id    = (int)$_POST['product_contract_id'];
@$product_contract_price    = (int)$_POST['product_contract_price'];

if(!isset($_POST['contract_id']) && (!isset($_POST['cart_update']))) { 

    $id = $odooConnection->createContract($order, $contract_name, $customer);

    print_r($id);
}

//contract product add - TODO: object
else if(isset($_POST['contract_id']) && $_POST['contract_id'] != '') {

    $contractId = (int)$_POST['contract_id'];
    $productId = (int)$_POST['product_contract_id'];

    $id = $odooConnection->createInvoiceLine($contractId, $productId, $product_contract_price, 'ecommerce');

    print_r($id);
}

//cart update - create
else if(isset($_POST['cart_update']) && $_POST['cart_update'] != '' && $_POST['cart_update'] == 'create' ) {

    $productId = (int)$_POST['product_cart_id'];
    
    $id = $odooConnection->createOrderLine($order, $productId);

    print_r($id);
}

//cart update - remove
else if(isset($_POST['cart_update']) && isset($_POST['product_contract_id'])) {
    sleep(4);

    $orderId = (int)$_POST['order_id'];
    $productId = (int)$_POST['product_contract_id'];

    $orderLineId = $odooConnection->removeOrderLine($orderId, $productId);

    print_r($orderLineId);
}
?>