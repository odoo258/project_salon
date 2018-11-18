<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');

class TrackNMeBuilder {
	
	public static function getInstance() {

		require_once("../Config.class.php");

		if (Config::$isMockPlataforma) {
			require_once("../TrackNMeMock.class.php");
			return new TrackNMeMock();
		} else {
			require_once("../TrackNMe.class.php");
			return new TrackNMe();
		}
	}
}