<?php 
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');
header('content-type: application/json');

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

	$response = array('ERROR' => $ex->getSeverity() . " - " . $ex->getMessage() . ". ON " . $ex->getFile() . ":" . $ex->getLine());
	echo json_encode($response);
}

restore_error_handler();

function execute() {

	$response = array(
		'ERROR' => '',
	);

	require_once("../TrackNMeBuilder.class.php");
	require_once("../OdooConnection.class.php");
	$odooConnection = new OdooConnection();
	$trackNMe = TrackNMeBuilder::getInstance();

	$invoiceId = $_POST['invoiceId'];
	//$invoice = $odooConnection->getInvoice($invoiceId);

	//$partner = $odooConnection->getPartner($invoice['partner_id'][0]);

	$payments = $trackNMe->getLastCreditCardOperation($_POST['user_plataforma']);

	if ($payments == null || count($payments->content) == 0) {
		$response['ERROR'] = "Erro ao buscar informações de pagamento!";
	} else {
		$payment = $payments->content[0];
		$recurrencyKey = $payment->creditCardRecurrencyKey;
		$value = $_POST['amount_total'];

		$recurrencyPayment = $trackNMe->catchRecurrencyPayment($value, $recurrencyKey);

		if ($recurrencyPayment == null) {
			$response['ERROR'] = "Erro ao realizar o pagamento!";
			//TODO salvar erro no para consulta poterior
		} else {
		    	$response['INFO'] = "ok";
		}
	}

	echo json_encode($response);
}
?>
