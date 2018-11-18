<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');

class OdooConnection {
	
	var $url;
	var $username;
	var $password;
	var $db;

	var $common;
	var $uid;
	var $models;

	function __construct() {

		$this->initConfig();
		$this->initConnection();
	}

	private function initConfig() {

		require_once("../Config.class.php");

		$this->url 			= Config::$url;
		$this->username 	= Config::$username;
		$this->password 	= Config::$password;
		$this->db 			= Config::$db;
	}

	private function initConnection() {
		
		require_once('../../ripcord/ripcord.php');

		$this->common = ripcord::client("$this->url/xmlrpc/2/common");

		$this->uid = $this->common->authenticate($this->db, $this->username, $this->password, array());

		$this->models = ripcord::client("$this->url/xmlrpc/2/object");
	}

	function getPartner($id) {

		return $this->getEntityById($id, 'res.partner');
	}

	function getDevice($id) {

		return $this->getEntityById($id, 'stock.production.lot');
	}

	function getProduct($id) {

		return $this->getEntityById($id, 'product.product');
	}

	function getTask($id) {

		return $this->getEntityById($id, 'installation.schedule');
	}

	function getOrder($id) {

		return $this->getEntityById($id, 'sale.order', array('amount_total', 'name', 'currency_id', 'payment_tx_id', 'payment_acquirer_id', 'state'));
	}

	function getContract($id) {

		return $this->getEntityById($id, 'account.analytic.account');
	}

	function getInvoice($id) {

		return $this->getEntityById($id, 'account.invoice');
	}

	function getEntityById($id, $entityPath, $returnedFields = array()) {

		$filters = array(array('id', '=', (int)$id));

		$entities = $this->filterEntities($entityPath, $filters, $returnedFields);

		if (count($entities) == 0)  {
			throw new Exception("Não foi possível encontrar o objeto ($entityPath) com o id ($id) informado.");
		}

		return $entities[0];
	}

	function filterEntities($entityPath, $filters, $returnedFields = array(), $limit = 1, $orderBy = '') {

		$entities = $this->models->execute_kw($this->db, $this->uid, $this->password,
	    	$entityPath, 'search_read',
	    	array(
	    		$filters
	    	),
	    	array(
	    		'fields' 	=> $returnedFields, 
	    		'limit' 	=> $limit,
	    		'order' 	=> $orderBy
	    	)
	    );

		return $entities;
	}

	function searchEntities($entityPath, $filters, $returnedFields = array(), $limit = '', $orderBy = '') {

		$ids = $this->models->execute_kw($this->db, $this->uid, $this->password,
	    	$entityPath, 'search',
	    	array(
	    		$filters
	    	),
	    	array(
	    		'fields' 	=> $returnedFields, 
	    		'limit' 	=> $limit,
	    		'order' 	=> $orderBy
	    	)
	    );

		return $ids;
	}

	function createContract($order, $contractName, $customer) {

	    $id = $this->models->execute_kw($this->db, $this->uid, $this->password,
		    'account.analytic.account', 'create',
		    array(
		    	array(
	                "code"=> $order, 
	                "name"=> utf8_encode($contractName), 
	                "partner_id"=> $customer, 
	                "company_id"=> '1', 
	                "parent_id"=> '', 
	                "pricelist_id"=> '1', 
	                "to_invoice"=> '3', 
	                "state"=> 'open', 
	                "type"=> 'contract',  
	                "is_overdue_quantity"=> true, 
	                "fix_price_invoices"=> false, 
	                "recurring_invoices"=> false,
	                "recurring_interval"=> '1', 
	                "recurring_rule_type"=> 'monthly', 
	                "invoice_on_timesheets"=> false, 
	                "use_timesheets"=> false, 
	                "use_tasks"=> false
	             )
		    )
	    );

	    return $id;
	}

	function createTask($orderId, $partnerId, $companyId, $dateDB, $time) {

	    $id = $this->models->execute_kw($this->db, $this->uid, $this->password,
    		'project.task', 'create',
    		array(
    			array(
	                'name'=>"Instalação venda Nº ".$orderId." às ".$time,
	                'project_id'=>1,
	                'date_deadline'=>$dateDB,
	                'company_id'=>$companyId,
	                'partner_id'=>$partnerId,
	                'user_id'=>'',
	                'x_order_id'=>$orderId
                )
            )
        );

	    return $id;
	}

	function createInvoiceLine($contractId, $productId, $productPrice, $from) {

	    $id = $this->models->execute_kw($this->db, $this->uid, $this->password,
    		'account.analytic.invoice.line', 'create',
    		array(
    			array(
                "analytic_account_id"=> $contractId,
                "product_id"=> $productId,
                "name"=> 'Contratado via ' . $from,
                "price_unit"=> $productPrice,
                "uom_id"=> 1
                )
            )
        );

	    return $id;
	}

	function createOrderLine($orderId, $productId) {

	    $id = $this->models->execute_kw($this->db, $this->uid, $this->password,
    		'sale.order.line', 'create',
    		array(
    			array(
                "order_id"=> $orderId,
                "product_id"=> $productId
                )
            )
        );

	    return $id;
	}	

	function searchDevice($serial_number) {

	    $stock_location = $this->models->execute_kw($this->db, $this->uid, $this->password,
    		'stock.location', 'search',
    		array(
    			array(
                	array('usage', '=', 'internal'),
                )
            )
        );

	    $stock_quant = $this->models->execute_kw($this->db, $this->uid, $this->password,
    		'stock.quant', 'search_read',
    		array(
    			array(
                	array('qty', '>', 0),
            		array('location_id', 'in', $stock_location),
                )
            ),
            array(
	    		'fields' => array('id', 'lot_id')
	    	)
        );

	    foreach ($stock_quant as $key => $value) {
	    	$stock = $stock_quant[$key];
	    	if ($stock['lot_id'][1]==$serial_number) {
	    		return $stock['lot_id'][0];
	    	}
	    }

	    return null;
	}

	function searchStates($countryId) {
		
		$filters = array(array('country_id', '=' , $countryId));

		return $this->filterEntities('res.country.state', $filters, array(), '', 'code');
	}

	function searchCompanies() {
		
		$companies = $this->models->execute_kw($this->db, $this->uid, $this->password,
			'res.company', 'search_read',
			array(
				array(
					array('partner_id', '!=', ''),
					array('currency_id', '!=', ''),
	            //     array('parent_id', '=', 35)
					)),
			array(
				'fields' => array('partner_id'), 
				'order' => 'id'
				)
			);

		$pp = array();
		foreach ($companies as $val) {
			$pp[] = $val['partner_id'][0];
		}

		$partnerCompanies = $this->models->execute_kw($this->db, $this->uid, $this->password,
			'res.partner', 'search_read',
			array(
				array(
					array('is_company', '=', true),
					array('customer', '=', false),
					array('id', 'in', $pp)
					)
				),
			array(
				'fields' => array('id', 'company_id', 'name', 'country_id', 'comment', 'street', 'street2', 'city', 'state_id', 'zip', 'district', 'l10n_br_city_id', 'number'), 
				'order' => 'name'
				)
			);

		return $partnerCompanies;
	}

	function searchTipoVeiculo() {
		$tiposVeiculo = $this->models->execute_kw($this->db, $this->uid, $this->password,
		    'product.attribute', 'search',
		    array(
		        array(
		            array('name','=', 'Tipo de Veículo')
	            )
	        )
	    );

	    return $tiposVeiculo[0];
	}

	function searchTiposVeiculo($tipoVeiculo) {

		$tiposVeiculo = $this->models->execute_kw($this->db, $this->uid, $this->password,
		    'product.attribute.value', 'search_read',
		    array(
		    	array(
		    		array('attribute_id', '=', $tipoVeiculo)
		    	)
		    ),
		    array(
		    	'fields' => array('id', 'name')
		    )
	    );

	    return $tiposVeiculo;
	}

	function searchFabricanteVeiculo($tipoVeiculo) {

		$fabricantesVeiculo = $this->models->execute_kw($this->db, $this->uid, $this->password,
		    'product.attribute', 'search',
		    array(
		        array(
		            array('related_attribute_id', '=', $tipoVeiculo)
	            )
	        )
	    );

	    return $fabricantesVeiculo[0];
	}

	function searchFabricantesVeiculo($fabricanteVeiculo) {

		$fabricantesVeiculo = $this->models->execute_kw($this->db, $this->uid, $this->password,
		    'product.attribute.value', 'search_read',
		    array(
		        array(
		        	array('attribute_id', '=', $fabricanteVeiculo)
		        )
		    ),
		    array(
		    	'fields' => array('id', 'name')
		    )
	    );

	    return $fabricantesVeiculo;
	}

	function searchModeloVeiculo($modeloVeiculo) {

		$modelosVeiculo = $this->models->execute_kw($this->db, $this->uid, $this->password,
		    'product.attribute', 'search',
		    array(
		        array(
		            array('related_attribute_id', '=', $modeloVeiculo)
	            )
	        )
	    );

	    return $modelosVeiculo[0];
	}

	function searchModelosVeiculo($anoVeiculo) {

		$modelosVeiculo = $this->models->execute_kw($this->db, $this->uid, $this->password,
		    'product.attribute.value', 'search_read',
		    array(
		        array(
		        	array('attribute_id', '=', $anoVeiculo)
		        )
		    ),
		    array(
		    	'fields' => array('id', 'name')
		    )
	    );

	    return $modelosVeiculo;
	}

	function searchAnoVeiculo($modeloVeiculo) {

		$anosVeiculo = $this->models->execute_kw($this->db, $this->uid, $this->password,
		    'product.attribute', 'search',
		    array(
		        array(
		            array('related_attribute_id', '=', $modeloVeiculo)
	            )
	        )
	    );

	    return $anosVeiculo[0];
	}

	function searchAnosVeiculo($anoVeiculo) {

		$modelosVeiculo = $this->models->execute_kw($this->db, $this->uid, $this->password,
		    'product.attribute.value', 'search_read',
		    array(
		        array(
		        	array('attribute_id', '=', $anoVeiculo)
		        )
		    ),
		    array(
		    	'fields' => array('id', 'name')
		    )
	    );

	    return $modelosVeiculo;
	}

	function search_attributes1($ProdutosIni) {

		$SearchAndReadProdAttRel = $this->models->execute_kw($this->db, $this->uid, $this->password,
            'product.attribute.value.product.product.rel', 'search_read',
            array(
                array(
                    array('id', '>', '0'),
                    array('prod_id', 'in', $ProdutosIni),
                )
            ),
            array(
            	'fields' => array('att_id', 'prod_id')
            )
        );

        return $SearchAndReadProdAttRel;
	}

	function search_attributes2($t) {

        $SearchAndReadProdAttRel = $this->models->execute_kw($this->db, $this->uid, $this->password,
            'product.attribute.value.product.product.rel', 'search_read',
            array(
                array(
                    array('id','>', '0'),
                    array('att_id','=', [$t]),
                )
            ),
            array(
            	'fields'=>array('att_id', 'prod_id')
            	)
        );

        return $SearchAndReadProdAttRel;
	}

	function search_attributes3($pp) {

	    $SearchAndReadProdAttRel = $this->models->execute_kw($this->db, $this->uid, $this->password,
	        'product.attribute.value.product.product.rel', 'search_read',
	        array(
	            array(
	                array('id', '>', '0'),
	                array('prod_id', 'in', $pp),
	            )
	        ),
	        array(
	        	'fields' => array('att_id', 'prod_id')
	        	)
	    );

        return $SearchAndReadProdAttRel;
	}

	function search_attributes4($value) {

		$SearchAndReadProdAttFab = $this->models->execute_kw($this->db, $this->uid, $this->password,
            'product.attribute.value.product.product.rel', 'search_read',
            array(array(
                array('id','>', '0'),
                array('prod_id','=', (int)$value),
                )
            ),
            array(
            	'fields' => array('att_id', 'prod_id')
            )
        );

        return $SearchAndReadProdAttFab;
	}

	function search_attributes5($pp) {

		$SearchAndReadProdAttRel = $this->models->execute_kw($this->db, $this->uid, $this->password,
	        'product.attribute.value.product.product.rel', 'search_read',
	        array(
	            array(
	                array('prod_id', 'in', $pp),
	            )
	        ),
	        array(
	        	'fields' => array('att_id', 'prod_id')
	        )
        );

        return $SearchAndReadProdAttRel;
	}

	function removeOrderLine($orderId, $productId) {

	    // check if the deletable record is in the database
	    $var = $this->models->execute_kw($this->db, $this->uid, $this->password,
	        'sale.order.line', 'search',
	        array(array(
	                    array('order_id', '=', $orderId),
	                    array('product_id', '=', $productId)
	            )
	        )
	    );

	    $orderLineId = (int)$var[0];

	    $this->models->execute_kw($this->db, $this->uid, $this->password,
	        'sale.order.line', 'unlink',
	        array(
	        	array($orderLineId)
	        )
	    );

	    return $orderLineId;
	}

	function createTransaction($amount, $currencyId, $reference, $acquirerId, $acquirerReference, $partnerId, $orderId) {

		$fields = array(
			'amount' => $amount, 
			'currency_id' => $currencyId, 
			'acquirer_id' => $acquirerId, 
			'acquirer_reference' => $acquirerReference, 
			'partner_id' => $partnerId, 
			'sale_order_id' => $orderId, 
			'reference' => $reference,
			'state' => 'done',
			'date_validate' => date('Y-m-d H:i:s')
		);

		$id = $this->createEntity('payment.transaction', $fields);

		return $id;
	}

	function createOrder($partnerId, $companyId, $userId) {

		$fields = array(
			'partner_id'		=>$partnerId,
			'company_id'  		=>$companyId,
			'user_id' 			=>$userId,
			'state'				=>'manual',
			'procurement_group_id' =>'1',
		);

		$id = $this->createEntity('sale.order', $fields);

		return $id;
	}

	function createPartner($nome, $company_id, $email, $endereco, $estado, $cidade, $cep, $telefone, $veiculoPlaca, $cpfCnpj) {

        $fields = array(
            'name'=>$nome,
            'display_name'=>$nome,
            'company_id'=>$company_id,
            'email' =>$email,
            'street2'=>$endereco,
            'state_id'=>$estado,
            'city'=>$cidade,
            'zip'=>$cep,
            'phone'=>$telefone,
            'veiculo_placa'=>$veiculoPlaca,
            'cnpj_cpf'=>$cpfCnpj
        );

		$id = $this->createEntity('res.partner', $fields);

		return $id;
	}

	function createUser($partnerId, $login, $password) {

		$fields = array(
			'partner_id' => $partnerId, 
			'login' => $login,
			'password'=>$password
		);

		$id = $this->createEntity('res.users', $fields);

		return $id;
	}

	function createEntity($entityPath, $fields) {
	    $id = $this->models->execute_kw($this->db, $this->uid, $this->password, 
	    	$entityPath, 'create',
	    	array(
	    		$fields
	    	)
	    );

		return $id;
	}

	function updateOrder($id, $transactionId, $acquirerId, $state) {

		$fields = array(
			'payment_tx_id' => $transactionId, 
			'payment_acquirer_id' => $acquirerId, 
			'state' => $state,
			'invoiced' => true
		);

		$result = $this->updateEntity($id, 'sale.order', $fields);

		if ($result)
			return $this->getOrder($id);
		else
			return $result;
	}

	function confirmInvoice($id) {

		$fields = array(
			'fiscal_position' 		=> Config::$paymentParams['fiscal_position'],
			'fiscal_document_id' 	=> Config::$paymentParams['fiscal_document_id'],
		);

		$result = $this->updateEntity($id, 'account.invoice', $fields);

		if ($result) {
		    $result = $this->models->exec_workflow($this->db, $this->uid, $this->password, 
		    	'account.invoice', 'invoice_validate',
	    		(int)$id
		    );
		}

		return $result;
	}

	function payInvoice($id, $reference) {

		$invoice 	= $this->getInvoice($id);

		$amount 	= $invoice['amount_total'];
		$periodId 	= $invoice['period_id'][0];
		$accountId 	= Config::$paymentParams['account_id'];
		$journalId 	= Config::$paymentParams['journal_id'];

	    $result = $this->models->execute_kw($this->db, $this->uid, $this->password, 
	    	'account.invoice', 'pay_and_reconcile',
    		array((int)$id),
    		array(
    			'pay_amount' => $amount, 
    			'pay_account_id' => $accountId, 
    			'period_id' => $periodId, 
    			'pay_journal_id' => $journalId, 
    			'writeoff_acc_id' => false, 
    			'writeoff_period_id' => false, 
    			'writeoff_journal_id' => false, 
    			'context' => '', 
    			'name' => $reference
    		)
	    );

		return $result;
	}

	function setContractParter($orderId, $partnerId) {

		$contract = $this->getContractByOrder($orderId);

		$fields = array('partner_id' => $partnerId);

		$result = $this->updateEntity($contract['id'], 'account.analytic.account', $fields);

		return $result;
	}

	function setUserPlataforma($partnerId, $user) {

		$fields = array('user_plataforma' => $user);

		$result = $this->updateEntity($partnerId, 'res.partner', $fields);

		return $result;
	}

	function activeContract($orderId) {

		$contract = $this->getContractByOrder($orderId);

		$firstRecur = date('Y-m-d', strtotime("+1 month"));

		$fields = array(
			'recurring_invoices' => true,
			'recurring_next_date' => $firstRecur,
		 );

		$result = $this->updateEntity($contract['id'], 'account.analytic.account', $fields);

		return $result;
	}

	function getContractByOrder($orderId) {

		$filters = array(array('code', '=', $orderId));

		$contracts = $this->filterEntities('account.analytic.account', $filters);

		return $contracts[0];
	}

	function updateEntity($id, $entityPath, $fields) {
	    $result = $this->models->execute_kw($this->db, $this->uid, $this->password, 
	    	$entityPath, 'write',
	    	array(
	    		array((int)$id), $fields
	    	)
	    );

		return $result;
	}

	/* ########## SUPPORT FUNCTIONS ########## */
	function getFields($entityPath) {

		$info = $this->models->execute_kw($this->db, $this->uid, $this->password,
    		$entityPath, 'fields_get',
    		array(), 
    		array('attributes' => array('string'/*, 'help', 'type'*/))
    	);

		return $info;
	}

	function count($id, $entityPath) {
  	
		$count = $this->models->execute_kw($this->db, $this->uid, $this->password,
    		$entityPath, 'search_count',
		    array(array(array('id', '=', $id)))
    	);

		return $count;
	}

	function create($name) {
	    $id = $this->models->execute_kw($this->db, $this->uid, $this->password, 
	    	'res.partner', 'create',
	    	array(
	    		array('name'=>$name)
	    	)
	    );

		$result = $this->getEntityById($id, 'res.partner');

		return $result;
	}

	function update($id) {
	    $this->models->execute_kw($this->db, $this->uid, $this->password, 
	    	'res.partner', 'write',
	    	array(
	    		array($id), array('name' => "Newer partner")
	    	)
	    );

		$this->models->execute_kw($this->db, $this->uid, $this->password,
		    'res.partner', 'name_get', 
		    array(array($id))
		);
	}
}

?>
