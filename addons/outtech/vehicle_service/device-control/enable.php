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

	$deviceId = $_POST['deviceId'];
	$device = $odooConnection->getDevice($deviceId);
	$product = $odooConnection->getProduct($device['product_id'][0]);

	$taskId = $_POST['taskId'];
	$task = $odooConnection->getTask($taskId);

	$partner = $odooConnection->getPartner($task['partner_id'][0]);

	$offer = 3;//TODO é isso mesmo? propriedades
	$user = $partner['x_user_plataforma'];
	$deviceName = $product['name_template'];
	$deviceEntity = "CAR";//TODO propriedades
	$deviceNumber = $device['x_sim_msisdn'];
	$deviceImei = $device['x_imei'];
	$deviceSimCard = $device['x_sim_iccid'];
	$deviceModel = $device['x_modelo'];
	$deviceOperator = $device['x_sim_operadora'];


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