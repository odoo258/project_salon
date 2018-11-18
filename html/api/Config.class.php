<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');

class Config {
	
	public static $url 		= "http://localhost:8010";
	public static $username = "admin";//"odoo@tracknme.com.br";
	public static $password = "tmehom@17";//"admin";//"acidpill";
	public static $db 		= "Tracknme-Homolog-11-01-17";//"Teste10";//"telefonica";

	public static $apiURL 	= 'http://35.160.234.137/api/';

	public static $isMockPlataforma = true;

	public static $paymentParams = array(
					'account_id' => 660,
					'journal_id' => 7,
					'fiscal_position' => 5,
					'fiscal_document_id' => 1,
	);
}
