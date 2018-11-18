<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');
header('content-type: application/json');

$response = array(
    'PARTNER_ID' => '',
    'USER_ID' => '',
    'ERROR' => ''
);

require_once("../OdooConnection.class.php");
$odooConnection = new OdooConnection();

$cliente_nome =         $_POST['cliente_nome'];
$cliente_email =        $_POST['cliente_email'];
$cliente_endereco =     $_POST['cliente_endereco'];
$cliente_estado =       $_POST['cliente_estado'];
$cliente_cidade =       $_POST['cliente_cidade'];
$cliente_cep =          $_POST['cliente_cep'];
$cliente_cpf_cnpj =     $_POST['cliente_cpf_cnpj'];
$cliente_telefone =     $_POST['cliente_telefone'];
$company_id =           (int)$_POST['company_id'];
$veiculo_placa =        $_POST['veiculo_placa'];
$password =             $_POST['password'];

$partnerId = $odooConnection->createPartner($cliente_nome, $company_id, $cliente_email, $cliente_endereco, $cliente_estado, $cliente_cidade, $cliente_cep, $cliente_telefone, $veiculo_placa, $cliente_cpf_cnpj);

if ($partnerId && is_numeric($partnerId)) {
    $response['PARTNER_ID'] = $partnerId;

    $userId = $odooConnection->createUser($partnerId, $cliente_email, $password);

    if ($userId && is_numeric($userId)) {
        $response['USER_ID'] = $userId;
    } else {
        $response['ERROR'] = "Erro na criação do usuário. " . print_r($userId, true);
    }
    
} else {
    $response['ERROR'] = "Erro ao cadastrar cliente. " . print_r($partnerId, true);
}

echo json_encode($response);
?>
