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

	$response = array('ERROR' => $ex->getMessage());
	echo json_encode($response);
}

restore_error_handler();

function execute() {

	$response = array(
		'ERROR' 		=> '',
		'GPS' 			=> '',
		'ACC_OFF' 		=> '',
		'GPS_VALID' 	=> ''
		);

	require_once("../TrackNMeBuilder.class.php");
	$trackNMe = TrackNMeBuilder::getInstance();

	$deviceId = @$_POST['deviceId'];

	$resultGetDeviceInfo = $trackNMe->getDeviceInfo($deviceId);

	$infos = $resultGetDeviceInfo->{"content"};

	if (isset($infos) && count($infos) == 0) {
		throw new Exception('Busca não retornou informações.');
	}

	$tracking = $infos[0];

	$latitude = $tracking->{"latitude"};
	$longitude = $tracking->{"longitude"};

	if (!is_null($latitude) && is_float($latitude) && !is_null($longitude) && is_float($longitude))
		$response["GPS"] = 'OK';
	
	$response["GPS_VALID"] = $tracking->{"valid"};
	$sensors = $tracking->{"sensors"};

	if (count($sensors) != 0) {
		foreach ($sensors as $i => $value) {
			$sensor = $sensors[$i];
			if ($sensor->{"type"} == 'ACC_OFF')
				$response['ACC_OFF'] = $sensor->{"value"};
		}
	}

	echo json_encode($response);
}
?>