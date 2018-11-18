<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');

require_once("../OdooConnection.class.php");
$odooConnection = new OdooConnection();

require_once("../Config.class.php");
$apiURL     = Config::$apiURL;

$order      = @$_GET['order_id'];
$customer   = @$_GET['partner_id'];

$SearchAndReadPartner = $odooConnection->searchCompanies();

?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <title>Odoo API</title>  
</head>
<body>

<div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
     <h4 class="modal-title">Agendar Instalação&#160;&#160;&#160;<i class="fa fa-calendar"/></h4>
</div>
<div class="modal-body">
    <div class="te">
<div class="row"> 
    <div class="col-md-6">
    Escolha o melhor local para instalação: 
    </div>
    <div class="col-md-12">
    <select required="required" name="localInstalacao" id="localInstalacao" style="padding: 5px;max-width: 570px;">
        <option>- selecione -</option>
        <?php 
        foreach ($SearchAndReadPartner as $key => $value) {
            echo '<option value="'.$value['company_id'][0].'">'.xmlrpc_encode($value['name'])
            .' - '.xmlrpc_encode($value['street'])
            .xmlrpc_encode($value['street2'])
            .' - nº'.xmlrpc_encode($value['number'])
            .' - '.xmlrpc_encode($value['district'])
            .' - '.xmlrpc_encode($value['l10n_br_city_id'][1])
            .' - '.xmlrpc_encode($value['state_id'][1])
            .' - '.$value['zip'].
            '</option>';
        }
        ?>
    </select>
    </div>
    <br>
    <br>
    <br>
    <br>

    <div class="col-md-6" style="padding: 5px; margin-left: 10px;">
    Escolha a melhor data para instalação:
    </div>
    <div id="sandbox-container" class="col-md-4">
    <input required="required" style="background: #FFFFFF;" type="text" class="form-control" name="dataInstalacao" id="dataInstalacao">
    </div>
<br>
<br>
    <div class="col-md-6" style="padding: 5px; margin-left: 10px;">
    Escolha o melhor horário para instalação:
    </div>
    <div class="col-md-4">
    <select required="required" class="form-control" name="horaInstalacao" id="horaInstalacao">
        <option>- selecione -</option>
        <option value="08:00">08:00</option>
        <option value="08:30">08:30</option>
        <option value="09:00">09:00</option>
        <option value="09:30">09:30</option>
        <option value="10:00">10:00</option>
        <option value="10:30">10:30</option>
        <option value="11:00">11:00</option>
        <option value="11:30">11:30</option>
        <option value="13:00">13:00</option>
        <option value="13:30">13:30</option>
        <option value="14:00">14:00</option>
        <option value="14:30">14:30</option>
        <option value="15:00">15:00</option>
        <option value="15:30">15:30</option>
        <option value="16:00">16:00</option>
        <option value="16:30">16:30</option>
        <option value="17:00">17:00</option>
        <option value="17:30">17:30</option>
    </select>
    </div>

</div>

    </div>
</div>
<div class="modal-footer">
    <button type="button" id="fechar" class="btn btn-default" data-dismiss="modal">Fechar</button>
    <button type="button" id="salvar"  class="btn btn-primary">Salvar ></button>
</div>

</body>
<script type="text/javascript">
    
$('#salvar').click(function(event) {
   $.post(
        "<?=$apiURL?>schedule-installation/schedule.php", 
        { 
            order_id: "<?=$order?>", 
            partner_id: "<?=$customer?>", 
            dataInstalacao: $('#dataInstalacao').val(), 
            localInstalacao: $('#localInstalacao').val(), 
            horaInstalacao: $('#horaInstalacao').val()
        }
    ).done(function(data) {
        alert( "Protocolo de Instalação: " + data );

        $("#fechar").click();
        $("#schedule-btn").prop('disabled',true);
        $("#schedule-btn").attr("href", "#");
        $("#schedule-btn").html('<i class="fa fa-calendar"></i> Protoloco da Instalação: <b>'+data+'</b>');

        setTimeout('window.location="/shop"', 2000);
  });
});

$(document).ready(function() {
    
    console.log( "ready!" );

    setTimeout(
        function() {
            
            console.log( "setTimeout!" );
            $(function() {
                $('#dataInstalacao').datepicker({
                    dateFormat: 'dd/mm/yy',
                    beforeShowDay: $.datepicker.noWeekends,
                    minDate: new Date
                });
            });
        }, 5000
    );
});

/* Brazilian initialisation for the jQuery UI date picker plugin. */
/* Written by Leonildo Costa Silva (leocsilva@gmail.com). */
( function( factory ) {
    if ( typeof define === "function" && define.amd ) {
        // AMD. Register as an anonymous module.
        define( [ "/widgets/datepicker" ], factory );
    } else {
        // Browser globals
        factory( jQuery.datepicker );
    }
}( function( datepicker ) {

    datepicker.regional[ "pt-BR" ] = {
        closeText: "Fechar",
        prevText: "&#x3C;Anterior",
        nextText: "Próximo&#x3E;",
        currentText: "Hoje",
        monthNames: [ "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
        "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro" ],
        monthNamesShort: [ "Jan","Fev","Mar","Abr","Mai","Jun",
        "Jul","Ago","Set","Out","Nov","Dez" ],
        dayNames: [
            "Domingo",
            "Segunda-feira",
            "Terça-feira",
            "Quarta-feira",
            "Quinta-feira",
            "Sexta-feira",
            "Sábado"
        ],
        dayNamesShort: [ "Dom","Seg","Ter","Qua","Qui","Sex","Sáb" ],
        dayNamesMin: [ "Dom","Seg","Ter","Qua","Qui","Sex","Sáb" ],
        weekHeader: "Sm",
        dateFormat: "dd/mm/yy",
        firstDay: 0,
        isRTL: false,
        showMonthAfterYear: false,
        yearSuffix: "" };
    datepicker.setDefaults( datepicker.regional[ "pt-BR" ] );

    return datepicker.regional[ "pt-BR" ];
} ) );
</script>
</html>