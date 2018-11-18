<?php
header('Access-Control-Allow-Origin: *');

class TrackNMe {

	function catchPayment($buyerName, $cpfCnpj, $value, $creditCardHolderName, $creditCardBrand, $creditCardNumber, $creditCardSecurityCode, $creditCardExpYear, $creditCardExpMonth) {

		$data = array(
		            'user'=> 0,
		            'buyerName'=> $buyerName, 
		            'buyerDocumentType'=> 'CPF', 
		            'buyerDocumentNumber'=> $cpfCnpj, 
		            'buyerType'=> 'Person', 
		            'transactionOperation'=> 'AuthOnly',  //AuthOnly //AuthAndCapture //mudar para AuthAndCapture
		            'transactionPrice'=> $value, 
		            'creditCardHolderName'=> $creditCardHolderName, 
		            'creditCardBrand'=> $creditCardBrand, 
		            'creditCardNumber'=> $creditCardNumber, 
		            'creditCardSecurityCode'=> $creditCardSecurityCode, 
		            'creditCardExpYear'=> $creditCardExpYear, 
		            'creditCardExpMonth'=> $creditCardExpMonth
		        );

		return $this->execOperationPost("/credit-card/approve/", $data);
	}

	function catchRecurrencyPayment($value, $recurrencyKey) {

		$data = array(
		            'transactionOperation'=> 'AuthOnly',  //AuthOnly //AuthAndCapture //mudar para AuthAndCapture
		            'transactionPrice'=> $value, 
		            'instantBuyKey'=> $recurrencyKey
				);

		return $this->execOperationPost("/credit-card/approve/", $data);
	}

	function signin($name, $email, $password, $confirmPassword, $cpfCnpj, $gender, $birthDate) {

		$data = array(
			'user' => array(
				'login' => $email, //deve ser o mesmo do email
				'name' => $name, 
				'password' => $password, //A senha deve conter entre 8 e 32 caracteres.
				'confirmPassword' => $confirmPassword, //A senha deve conter entre 8 e 32 caracteres.
				'cpfCnpj' => $cpfCnpj, //O CPF/CNPJ informado não corresponde a um CPF/CNPJ válido. Informe apenas os números sem barras, pontos ou hífens
				'email' => $email, 
				'gender' => $gender, //'MALE',
				'birthDate' => $birthDate//'1979-08-29T00:00:00'
			)
		);

		return $this->execOperationPost("/signin/", $data);
	}

	function storeCreditCard($user, $creditCardHolderName, $creditCardBrand, $creditCardNumber, $creditCardSecurityCode, $creditCardExpYear, $creditCardExpMonth) {

		$data = array(
		            'user' => $user, 
		            'type' => 'CREDIT_CARD', 
		            'creditCardHolderName' => $creditCardHolderName, 
		            'creditCardBrand' => $creditCardBrand, 
		            'creditCardNumber' => $creditCardNumber, 
		            'creditCardSecurityCode' => $creditCardSecurityCode, 
		            'creditCardExpYear' => $creditCardExpYear, 
		            'creditCardExpMonth' => $creditCardExpMonth
		        );

		return $this->execOperationPost("/payments/", $data);
	}

	function enableDevice($user, $offer, $deviceName, $deviceEntity, $deviceNumber, $deviceImei, $deviceSimCard, $deviceModel, $deviceOperator) {

		$data = array(
		            'user' => $user, 
		            'offer' => $offer, 
			        'accessionPrice' => 100, //esse não precisa
		            'device' => array( 
			            'name' => $deviceName, 
			            'entity' => $deviceEntity, 
			            'number' => $deviceNumber, 
			            'imei' => $deviceImei, 
			            'simCard' => $deviceSimCard, 
			            'model' => $deviceModel, 
			            'operator' => $deviceOperator
		            )
		        );

		return $this->execOperationPost("/plans/sell/", $data);
	}

	function getDeviceInfo($deviceId) {

		$data = "?by=device&device=$deviceId&limit=1";

		return $this->execOperationGet("/trackings", $data);
	}

	function getDeviceByImei($imei) {

		$data = "?by=imei&imei=$imei";

		return $this->execOperationGet("/devices", $data);
	}

	function getLastCreditCardOperation($userId) {

		$data = "?by=user&user=$userId&limit=1";

		return $this->execOperationGet("/payments", $data);
	}

	function execOperationGet($operation, $params) {
		
		return $this->execOperation('GET', $operation, '', $params);
	}

	function execOperationPost($operation, $data) {
		
		$content = json_encode($data);
		
		return $this->execOperation('POST', $operation, $content, '');
	}

	function execOperation($method, $operation, $content, $params) {
		
		$url = 'https://www.telefonicarastreamento.com.br/api';

		$options = array(
		  'http' => array(
		    'method'  => $method, 
		    'content' => $content, 
		    'header'  =>  "Content-Type: application/json\r\n" . 
		                  "Accept: application/json\r\n"
		    )
		);

		$context = stream_context_create($options);
		$result = file_get_contents($url . $operation . $params, false, $context);
		$response = json_decode($result);

		return $response;
	}

}
?>