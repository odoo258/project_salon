<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');

require_once("../OdooConnection.class.php");
$odooConnection = new OdooConnection();

$attr  = @$_POST['atributo'];
$ProdutosIni = @$_POST['ProdutosIni'];
$fabricante = @$_POST['fabricante'];
$prod  = @$_POST['prod'];
$prod2 = @trim($_GET['prod2']);
$produtos = array();

$t = (int)$attr;

if(!isset($prod)){

    if(isset($ProdutosIni)){

        $ProdutosIni = json_decode($_POST['ProdutosIni']);

        $SearchAndReadProdAttRel = $odooConnection->search_attributes1($ProdutosIni);

        foreach ($SearchAndReadProdAttRel as $key => $value)
            if($t == $value['att_id'][0])
                $produtos[] = $value['prod_id'][0];
    } else {
        $SearchAndReadProdAttRel = $odooConnection->search_attributes2($t);

        foreach ($SearchAndReadProdAttRel as $key => $value)
            $produtos[] = $value['prod_id'][0];
    }

    print_r(json_encode($produtos));
} else if(isset($prod) && $prod == '') {
    $pp = json_decode($_POST['pp']);

    $SearchAndReadProdAttRel = $odooConnection->search_attributes3($pp);

    foreach ($SearchAndReadProdAttRel as $key => $value)
        $produtos[] = $value['prod_id'][0];

    print_r(json_encode($produtos));
} else if(isset($prod) && $prod != '') {
    $prod_array = json_decode($prod);

    foreach ($prod_array as $value) {         

        $SearchAndReadProdAttFab = $odooConnection->search_attributes4($value);

        foreach ($SearchAndReadProdAttFab as $key => $value) {

            if((int)$fabricante == (int)$value['att_id'][0])
                echo '1';
            else
                echo "0";
        }
    }
} else if(isset($prodUNUSE) && $prod == '') {
    $pp = array_map('intval',explode(',', $_POST['pp']));

    $SearchAndReadProdAttRel = $odooConnection->search_attributes5($pp);

    foreach ($SearchAndReadProdAttRel as $key => $value) {

        if((int)$fabricante == (int)$value['att_id'][0])
            echo '1';
        else
            echo "0";
    }
}
?>
