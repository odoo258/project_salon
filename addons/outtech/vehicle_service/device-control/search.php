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
		'ERROR' => 0,
		'DEVICE' => ''
	);

	require_once("../OdooConnection.class.php");
	$odooConnection = new OdooConnection();

	$serial_number = @$_POST['serial_number'];

	$idDevice = $odooConnection->searchDevice($serial_number);

	if ($idDevice == null || $idDevice == '') {
		$response['ERROR'] = "Número de Série ($serial_number) não localizado!";
	} else {
		$response['DEVICE'] = $idDevice;
	}

	echo json_encode($response);
}
?>