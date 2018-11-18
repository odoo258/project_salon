<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');

require_once("../Config.class.php");
$apiURL = Config::$apiURL;
?>
<!DOCTYPE html>
<html lang="pt-br">
<meta charset="UTF-8">
<head>
  <title>Track'n Me API de Pagamentos</title>  
</head>
<body>

<div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
     <h4 class="modal-title">Track'n Me API de Pagamentos <span class="fa fa-lock"></span></h4>
</div>
<div class="modal-body">
  <div id="wrapwrap">
      <div class="te">
        <div class="row">
          <div class="form-group col-lg-4">
              <label class="control-label" for="creditCardBrand">Bandeira</label>
          </div>
          <div class="form-group col-lg-8">
            <select name="creditCardBrand" id="creditCardBrand" class="form-control" style="font-family: 'FontAwesome', Helvetica;">
              <option>- selecione -</option>
              <option value="AmericamExpress">&#xf1f3; Americam Express</option>
              <option value="MasterCard">&#xf1f1; MasterCard</option>
              <option value="Visa">&#xf1f0; Visa</option>
            </select>
          </div>
        </div>
        <div class="row">
          <div class="form-group col-lg-4">
              <label class="control-label" for="creditCardNumber">Número do Cartão de Crédito</label>
          </div>
          <div class="form-group col-lg-8">
              <input type="text" name="creditCardNumber" class="form-control" id="creditCardNumber" placeholder="1111 2222 3333 4444">
          </div>
        </div>
        <div class="row">
          <div class="form-group col-lg-4">
              <label class="control-label" for="creditCardHolderName">Nome no Cartão de Crédito</label>
          </div>
          <div class="form-group col-lg-8">
              <input type="text" name="creditCardHolderName" class="form-control" id="creditCardHolderName" placeholder="José D. Silva">
          </div>
        </div>
        <div class="row">
          <div class="form-group col-lg-4">
              <label class="control-label" for="creditCardExpMonth">Validade</label>
          </div>
          <div class="form-group col-lg-4">
              <input type="text" name="creditCardExpMonth" class="form-control" id="creditCardExpMonth" placeholder="Mês" maxlength="2">
          </div>
          <div class="form-group col-lg-4">
              <input type="text" name="creditCardExpYear" class="form-control" id="creditCardExpYear" placeholder="Ano" maxlength="4">
          </div>
        </div>
        <div class="row">
          <div class="form-group col-lg-4">
              <label class="control-label" for="creditCardSecurityCode">Código de Segurança PIN</label>
          </div>
          <div class="form-group col-lg-8">
              <input type="text" name="creditCardSecurityCode" class="form-control" id="creditCardSecurityCode" placeholder="123">
          </div>
        </div>
      </div>
  </div>  
</div>
<div class="modal-footer">
    <button type="button" class="btn btn-default" data-dismiss="modal">Fechar</button>
    <button type="button" id="enviar-dados" class="btn btn-primary">Enviar dados ></button>
</div>

</body>

<script src="http://code.jquery.com/jquery-2.2.4.min.js" integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44=" crossorigin="anonymous"></script>
<script type="text/javascript">

  jQuery(document).ready(function($) {
    $('#enviar-dados').click(function() {
      chamaPlataforma();
    });
  });

  function chamaPlataforma() {
    $.ajax({
      type: 'POST',
      url: '<?=$apiURL?>/cc-payment/php-rest.php',
      data: {
        partnerId: $('#partner_id').val(), 
        orderId: $('#order_id').val(), 
        creditCardHolderName: $('#creditCardHolderName').val(), 
        creditCardBrand: $('#creditCardBrand').val(), 
        creditCardNumber: $('#creditCardNumber').val(), 
        creditCardSecurityCode: $('#creditCardSecurityCode').val(), 
        creditCardExpMonth: $('#creditCardExpMonth').val(), 
        creditCardExpYear: $('#creditCardExpYear').val()
      },
      success: function(data) { 
        if (data.startsWith('OK')) {
          window.location = '/shop/confirmation'
        } else {
          alert('deu ruim' + data);
        }
      }
    });
  }
</script>
</html>