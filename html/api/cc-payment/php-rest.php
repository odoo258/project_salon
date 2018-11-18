<?php 
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');

set_error_handler(
    create_function(
        '$severity, $message, $file, $line',
        'throw new ErrorException($message, $severity, $severity, $file, $line);'
    )
);

try {
    execute();
} catch (Exception $ex) {
	error_log("Caught $ex");

	echo "ERROR: " . $ex->getSeverity() . " - " . $ex->getMessage() . ". ON " . $ex->getFile() . ":" . $ex->getLine();
}

restore_error_handler();

function execute() {

	require_once("../TrackNMeBuilder.class.php");
	require_once("../OdooConnection.class.php");
	$odooConnection = new OdooConnection();
	$trackNMe = TrackNMeBuilder::getInstance();

	//$partnerId = $_POST['partnerId'];
	//$partner = $odooConnection->getPartner($partnerId);

	//$orderId = $_POST['orderId'];
	//$order = $odooConnection->getOrder($orderId);

	$orderId = $_POST['orderId'];
	$partnerId 	= $_POST['partnerId'];
	$name 		= $_POST['name'];
	$email 		= $_POST['email'];
	$cpfCnpj 	= $_POST['cpfCnpj'];
	$value 		= $_POST['value'];

	$creditCardHolderName 		= $_POST['creditCardHolderName'];
	$creditCardBrand 			= $_POST['creditCardBrand'];
	$creditCardNumber 			= $_POST['creditCardNumber'];
	$creditCardSecurityCode 	= $_POST['creditCardSecurityCode'];
	$creditCardExpYear 			= $_POST['creditCardExpYear'];
	$creditCardExpMonth 		= $_POST['creditCardExpMonth'];

	$resultCatchPayment = $trackNMe->catchPayment($name, $cpfCnpj, $value, $creditCardHolderName, $creditCardBrand, $creditCardNumber, $creditCardSecurityCode, $creditCardExpYear, $creditCardExpMonth);

	$password 			= $_POST['password'];			//TODO pedir a senha para o cliente
	$confirmPassword 	= $_POST['confirmPassword'];				//TODO pedir a senha para o cliente
	$gender 			= $_POST['gender'];					//TODO criar campo no cliente
	$birthDate 			= $_POST['birthDate'];	//TODO criar campo no cliente

	$resultSignin = $trackNMe->signin($name, $email, $password, $confirmPassword, $cpfCnpj, $gender, $birthDate);


	$user = $resultSignin->user->id;

	//$resultSetUserPlataforma = $odooConnection->setUserPlataforma($partnerId, $user);

	//$resultUpdateContract = $odooConnection->setContractParter($orderId, $partnerId);


	$resultStoreCreditCard = $trackNMe->storeCreditCard($user, $creditCardHolderName, $creditCardBrand, $creditCardNumber, $creditCardSecurityCode, $creditCardExpYear, $creditCardExpMonth);


	//$amount 			= $value;
	//$currencyId 		= $order['currency_id'][0];
	//$reference 			= $order['name'];
	//$acquirerId 		= 2;
	//$acquirerReference 	= $resultCatchPayment->transactionKey;
	//$orderId 			= $order['id'];

	//$resultCreateTransaction = $odooConnection->createTransaction($amount, $currencyId, $reference, $acquirerId, $acquirerReference, $partnerId, $orderId);


	//$transactionId 	= $resultCreateTransaction;
	//$state 			= 'manual';

	//$resultUpdateOrder = $odooConnection->updateOrder($orderId, $transactionId, $acquirerId, $state);

	$response = array(
		//'testeConexao' => $acquirerReference, 
		'testeConexao1' => $cpfCnpj, 
		'partnerId' => $_POST['partnerId'], 
		'partner' => $partnerId, 
		'orderId' => $_POST['orderId'], 
		'order' => $orderId, 
		'catchPayment' => $resultCatchPayment, 
		'signin' => $resultSignin,
		'user_plataform'=> $user,
		'storeCreditCard' => $resultStoreCreditCard, 
		//'createTransaction' => $resultCreateTransaction, 
		//'updateOrder' => $resultUpdateOrder, 
		//'updateContract' => $resultUpdateContract
	);

	if (json_last_error() === JSON_ERROR_NONE) {
		//echo "OK";
		//var_dump($response);
		echo json_encode($response);
	} else
	    echo "Deu ruim: " . json_last_error();
}
?>
