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

	require_once("../OdooConnection.class.php");
	$odooConnection = new OdooConnection();

	$response = array(
		'CONTRACT_ID' => '',
		'ERROR' => ''
	);

	//$taskId = $_POST['taskId'];
	//$task = $odooConnection->getTask($taskId);
	//$contract = $odooConnection->activeContract($task['contract_id'][0]);

	if ($_POST['contract_id'] != '') {
        if ($_POST['msg'] == '') {
            $response['CONTRACT_ID'] = $_POST['contract_id'];
            }
        else {
            $response['ERROR'] = $_POST['msg'];
        }

	} else {
		$response['ERROR'] = $_POST['msg'];
	}

	echo json_encode($response);
}
?>
