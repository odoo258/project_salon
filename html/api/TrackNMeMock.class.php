<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');

class TrackNMeMock {

	function catchPayment($buyerName, $cpfCnpj, $value, $creditCardHolderName, $creditCardBrand, $creditCardNumber, $creditCardSecurityCode, $creditCardExpYear, $creditCardExpMonth) {

		$data = '{"buyerName":"'.$buyerName.'","buyerDocumentType":"CPF","buyerDocumentNumber":"'.$cpfCnpj.'","buyerType":"Person","transactionOperation":"AuthOnly","transactionPrice":'.$value.',"transactionKey":"94cbad5d-162d-46c1-b1eb-c0b397856ed1","orderKey":"cf31590a-b3ec-40b2-8ddb-adf7359726a3","instantBuyKey":"657d5193-b932-458e-ab54-44ac85d0a5f8","creditCardHolderName":"","creditCardBrand":"'.$creditCardHolderName.'","creditCardNumber":"","creditCardMaskedNumber":"492941****2693","creditCardSecurityCode":"","creditCardExpYear":0,"creditCardExpMonth":0}';

		return $this->execOperation("/credit-card/approve/", $data);
	}

	function catchRecurrencyPayment($value, $recurrencyKey) {

		$data = '{"buyerName":"'.$recurrencyKey.'","buyerDocumentType":"CPF","buyerDocumentNumber":"'.$recurrencyKey.'","buyerType":"Person","transactionOperation":"AuthOnly","transactionPrice":'.$value.',"transactionKey":"94cbad5d-162d-46c1-b1eb-c0b397856ed1","orderKey":"cf31590a-b3ec-40b2-8ddb-adf7359726a3","instantBuyKey":"657d5193-b932-458e-ab54-44ac85d0a5f8","creditCardHolderName":"","creditCardBrand":"'.$recurrencyKey.'","creditCardNumber":"","creditCardMaskedNumber":"492941****2693","creditCardSecurityCode":"","creditCardExpYear":0,"creditCardExpMonth":0}';

		return $this->execOperation("/credit-card/approve/", $data);
	}

	function signin($name, $email, $password, $confirmPassword, $cpfCnpj, $gender, $birthDate) {

		$data = '{"user":{"id":750,"login":"'.$email.'","name":"'.$name.'","email":"'.$email.'","cpfCnpj":"'.$cpfCnpj.'","gender":"'.$gender.'","birthDate":"'.$birthDate.'","status":"ACTIVE","profile":"USER"},"addresses":[],"contacts":[]}';

		return $this->execOperation("/signin/", $data);
	}

	function storeCreditCard($user, $creditCardHolderName, $creditCardBrand, $creditCardNumber, $creditCardSecurityCode, $creditCardExpYear, $creditCardExpMonth) {

		$data = '{"id":123,"type":"CREDIT_CARD","creditCardBrand":"'.$creditCardBrand.'","creditCardNumber":"492941****2693","creditCardRecurrencyKey":"31d77007-3eba-416a-ba2d-b4d027e2c24d","user":'.$user.'}';

		return $this->execOperation("/payments/", $data);
	}

	function enableDevice($user, $offer, $deviceName, $deviceEntity, $deviceNumber, $deviceImei, $deviceSimCard, $deviceModel, $deviceOperator) {

		$data = '{}';

		return $this->execOperation("/plans/sell/", $data);
	}

	function getDeviceInfo($deviceId) {

		$data = '{  "content": [    {      "id": "898503a7-4fbc-49ee-907b-983c4e9530c8",      "device": 149,      "dateTime": "2016-10-19T16:26:35",      "gprsDateTime": "2016-10-19T16:26:35",      "latitude": -23.60516,      "longitude": -46.692462,      "speed": 0,      "valid": true,      "imei": 1602000033,      "movement": "MOVING",      "sensors": [        {          "type": "TEMPERATURE",          "value": "OFF"        },        {          "type": "THREE_INPUT_ERROR_PASSWORD",          "value": "OFF"        },        {          "type": "GPRS_BACKED_UP",          "value": "OFF"        },        {          "type": "OIL_CUT_OFF",          "value": "OFF"        },        {          "type": "BATTERY_DEMOLITION",          "value": "OFF"        },        {          "type": "HIGH_LEVEL_SENSOR_1",          "value": "OFF"        },        {          "type": "HIGH_LEVEL_SENSOR_2",          "value": "OFF"        },        {          "type": "LOW_LEVEL_SENSOR_1",          "value": "OFF"        },        {          "type": "GPS_RECEIVER_FAULT_ALARM",          "value": "OFF"        },        {          "type": "TERMINAL_BY_BACKUP_BATTERY_POWER_SUPPLY",          "value": "OFF"        },        {          "type": "BATTERY_REMOVED",          "value": "OFF"        },        {          "type": "GPS_ANTENNA_DISCONNECT",          "value": "OFF"        },        {          "type": "GPS_ANTENNA_SHORT_CIRCUIT",          "value": "OFF"        },        {          "type": "LOW_LEVEL_SENSOR_2",          "value": "OFF"        },        {          "type": "DOOR_OPEN",          "value": "OFF"        },        {          "type": "VEHICLE_FORTIFICATION",          "value": "ON"        },        {          "type": "ACC_OFF",          "value": "OFF"        },        {          "type": "ENGINE",          "value": "OFF"        },        {          "type": "CUSTOM_ALARM",          "value": "OFF"        },        {          "type": "OVERSPEED",          "value": "OFF"        },        {          "type": "THEFT_ALARM",          "value": "OFF"        },        {          "type": "ROBBERY_ALARM",          "value": "OFF"        },        {          "type": "OVERSPEED_SPEED",          "value": "OFF"        },        {          "type": "ILLEGAL_IGNITION_ALARM",          "value": "OFF"        },        {          "type": "ENTERING_ALARM",          "value": "OFF"        },        {          "type": "GPS_ANTENNA_DISCONNECT_ALARM",          "value": "OFF"        },        {          "type": "GPS_ANTENNA_SHORT_CIRCUIT_ALARM",          "value": "OFF"        },        {          "type": "OUT_ALARM",          "value": "OFF"        }      ],      "formattedAddress": "R. Furnas, 261 - Brooklin Paulista, São Paulo - SP, 04562-050, Brazil"    }  ],  "last": false,  "totalPages": 37,  "totalElements": 37,  "sort": [    {      "direction": "DESC",      "property": "gprsDateTime",      "ignoreCase": false,      "nullHandling": "NATIVE",      "ascending": false    }  ],  "numberOfElements": 1,  "first": true,  "size": 1,  "number": 0}';

		return $this->execOperation("/tracking/", $data);
	}

	function getDeviceByImei($imei) {
		
		$data = '{"content":[{"id":196,"number":19976025066,"imei":1602000033,"simCard":"89551805000003239079","model":"Y2","status":"ACTIVE","activity":"SLEEPING","odometer":55676,"lastTracking":"2016-10-21T17:59:11","gprsInterval":60,"plan":138,"battery":53,"velocity":33,"interval":15,"car":13,"areas":[],"sentAlerts":["DRIVER_LICENSE_EXPIRED"]}],"last":true,"totalPages":1,"totalElements":1,"first":true,"sort":null,"numberOfElements":1,"size":10,"number":0}';

		return $this->execOperation("/devices", $data);
	}

	function getLastCreditCardOperation($userId) {

		$data = '{"content":[{"id":123,"type":"CREDIT_CARD","creditCardBrand":"Visa","creditCardNumber":"492941****2693","creditCardRecurrencyKey":"31d77007-3eba-416a-ba2d-b4d027e2c24d","user":750}],"last":true,"totalElements":1,"totalPages":1,"sort":null,"numberOfElements":1,"first":true,"size":1,"number":0}';

		return $this->execOperation("/payments", $data);
	}

	function execOperation($operation, $data) {

		$response = json_decode($data);

		return $response;
	}
}

?>
