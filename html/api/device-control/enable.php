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
		'DEVICE_ID' => ''
	);

	require_once("../TrackNMeBuilder.class.php");
	require_once("../OdooConnection.class.php");
	$odooConnection = new OdooConnection();
	$trackNMe = TrackNMeBuilder::getInstance();

	//$deviceId = $_POST['deviceId'];
	//$device = $odooConnection->getDevice($deviceId);
	//$product = $odooConnection->getProduct($device['product_id'][0]);

	//$taskId = $_POST['taskId'];
	//$task = $odooConnection->getTask($taskId);

	//$partner = $odooConnection->getPartner($task['partner_id'][0]);

	$offer = 3;//TODO é isso mesmo? propriedades
	$user = $_POST['user_plataforma'];//$partner['user_plataforma'];
	$deviceName = $_POST['name_product'];//$product['name_template'];
	$deviceEntity = "CAR";//TODO propriedades
	$deviceNumber = $_POST['sim_msisdn'];//$device['sim_msisdn'];
	$deviceImei = $_POST['imei'];//$device['imei'];
	$deviceSimCard = $_POST['sim_iccid'];//$device['sim_iccid'];
	$deviceModel = $_POST['model'];//$device['model'];
	$deviceOperator = $_POST['sim_operator'];//$device['sim_operator'];

	$resultEnableDevice = $trackNMe->enableDevice($user, $offer, $deviceName, $deviceEntity, $deviceNumber, $deviceImei, $deviceSimCard, $deviceModel, $deviceOperator); 

	$resultDeviceIMEI = $trackNMe->getDeviceByImei($deviceImei);

	if ($resultDeviceIMEI == null || $resultDeviceIMEI == '') {
		$response['ERROR'] = "Erro ao habilitar dispositivo!";
	} else {
		$response['DEVICE_ID'] = $resultDeviceIMEI->content[0]->id;
	}

	echo json_encode($response);
}
?>
