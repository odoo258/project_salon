<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: charset=utf-8');

require_once("../Config.class.php");
$apiURL     = Config::$apiURL;

require_once("../OdooConnection.class.php");
$odooConnection = new OdooConnection();

$order      = @$_GET['order_id'];
$customer   = @$_GET['partner_id'];

$SearchAndReadStates = $odooConnection->searchStates(32);

$tipoVeiculo = $odooConnection->searchTipoVeiculo();
$SearchAndReadProdAttVal = $odooConnection->searchTiposVeiculo($tipoVeiculo);

$fabricanteVeiculo = $odooConnection->searchFabricanteVeiculo($tipoVeiculo);
$SearchAndReadFabricantes = $odooConnection->searchFabricantesVeiculo($fabricanteVeiculo);

$modeloVeiculo = $odooConnection->searchModeloVeiculo($fabricanteVeiculo);
$SearchAndReadModelos = $odooConnection->searchModelosVeiculo($modeloVeiculo);

$anoVeiculo = $odooConnection->searchAnoVeiculo($modeloVeiculo);
$SearchAndReadAnos = $odooConnection->searchAnosVeiculo($anoVeiculo);
?>

<script type="text/javascript" src="/tracknme/static/src/js/jquery.steps.min.js"></script>
<link rel="stylesheet" href="/tracknme/static/src/css/jquery.steps.css">

<div class="te">
    <div class="panel"> 
        <div id="alert-info" class="alert alert-info col-md-12" style="display: none">
            <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>
            <label for="">Informação: </label> <span class="alert-info-msg">msg</span>
        </div>

        <div id="alert-danger" class="alert alert-danger col-md-12" style="display: none">
            <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>
            <label for="">Erro: </label> <span class="alert-danger-msg">msg</span>
        </div>

        <div class="hidden">
            <input type="text" value="" id="user_id" title="user_id">
            <!-- TODO: pegar o company_id do cadastro do user_id, testar com usuario de outra empresa antes de mudar -->
            <input type="text" id="company_id" title="company_id" value="1">
            <input type="text" id="partner_id" title="partner_id"  value="0">
            <input type="text" id="product_id" title="product_id"  value="0">
            <input type="text" id="product_contract_name" title="product_contract_name"  value="">
            <input type="text" id="sale_order_id" title="sale_order_id"  value="0">
            <input type="text" id="url" title="url"  value="<?=$url?>">
        </div>
    </div>

    <div class="steps" id="steps">

        <h3><i class="fa fa-car"></i>&nbsp; Veículo</h3>
        <div class="panel panel-info">
            <div class="panel-heading">
                Dados do Veículo <i class="fa fa-car pull-right"></i>
            </div>

            <div class="panel-body">
                <div class="col-md-12">
                    <label for="">Tipo de Veículo</label>
                    <div>
                        <?php 
                        foreach ($SearchAndReadProdAttVal as $key => $value) {
                            echo '<input type="radio" name="tipo_veiculo" onclick="Radio(this.value)" id="tipo_veiculo" value="'.$value['id'].'" style="display:inline">'.utf8_encode($value['name']).
                            '</input>';
                        }
                        ?>
                    </div>
                </div>
                <div class="col-md-12">
                    <label for="fabricante_veiculo" class="control-label">Fabricante</label>
                    <select onchange="Select(this.value)" class="form-control js_variant_change" id="fabricante_veiculo" name="fabricante_veiculo">
                        <option value="0"> - selecione - </option>
                        <?php 
                        foreach ($SearchAndReadFabricantes as $key => $value) {
                            echo '<option value="'.$value['id'].'">'.utf8_encode($value['name']).'</option>';
                        }
                        ?>
                    </select>
                </div>
                <div class="col-md-12">
                    <label for="modelo_veiculo">Modelo</label>
                    <select onchange="Select2(this.value)" class="form-control js_variant_change" id="modelo_veiculo" name="modelo_veiculo">
                        <option value="0"> - selecione - </option>
                        <?php 
                        foreach ($SearchAndReadModelos as $key => $value) {
                            echo '<option value="'.$value['id'].'">'.utf8_encode($value['name']).'</option>';
                        }
                        ?>
                    </select>
                </div>
                <div class="col-md-12">
                    <label for="ano_veiculo">Ano</label>
                    <select onchange="Select3(this.value)" class="form-control js_variant_change" id="ano_veiculo" name="ano_veiculo">
                        <option value="0"> - selecione - </option>
                        <?php 
                        foreach ($SearchAndReadAnos as $key => $value) {
                            echo '<option value="'.$value['id'].'">'.utf8_encode($value['name']).'</option>';
                        }
                        ?>
                    </select>
                </div>
                <div class="form-group col-md-12">
                    <label for="veiculo_placa">Placa</label>
                    <input type="text" width="100" class="form-control" name="veiculo_placa" id="veiculo_placa" value="">
                </div>
            </div>
        </div>
    
        <h3><i class="glyphicon glyphicon-user"></i> &nbsp;Cliente</h3>
        <div class="panel panel-info">
            <div class="panel-heading">
                Dados do Cliente <i class="glyphicon glyphicon-user pull-right"></i>
            </div>

            <div class="panel-body">
                <div class="col-md-12">
                    <label for="cliente_nome">Nome</label>
                    <input type="text" name="cliente_nome" id="cliente_nome" class="form-control" >
                </div>

                <div class="col-md-6">
                    <label for="cliente_email">Email</label>
                    <input type="text" name="cliente_email" id="cliente_email" class="form-control" >
                </div>
                <div class="col-md-6">
                    <label for="cliente_telefone">Telefone</label>
                    <input type="text" name="cliente_telefone" id="cliente_telefone" class="form-control" >
                </div>

                <div class="col-md-8">
                    <label for="cliente_endereco">Endereço</label>
                    <input type="text" name="cliente_endereco" id="cliente_endereco" class="form-control" >
                </div>
                <div class="col-md-4">
                    <label for="cliente_estado">Estado</label>
                    <select required="required" name="cliente_estado" id="cliente_estado" class="form-control" >
                        <option>- selecione -</option>
                        <?php 
                        foreach ($SearchAndReadStates as $key => $value) {
                            echo '<option value="'.$value['id'].'">'.utf8_encode($value['code']).' - '.utf8_encode($value['name']).'</option>';
                        }
                        ?>
                    </select>
                </div>

                <div class="col-md-8">
                    <label for="cliente_cidade">Cidade</label>
                    <input type="text" name="cliente_cidade" id="cliente_cidade" class="form-control" >
                </div>
                <div class="col-md-4">
                    <label for="cliente_cep">CEP</label>
                    <input type="text" name="cliente_cep" id="cliente_cep" class="form-control" >
                </div>

                <div class="col-md-6">
                    <label for="cliente_cpf_cnpj">CPF/CNPJ</label>
                    <input type="text" name="cliente_cpf_cnpj" id="cliente_cpf_cnpj" class="form-control" >
                </div>
                <div class="col-md-6">
                    <label for="cliente_data_nascimento">Data Nascimento</label>
                    <input type="text" name="cliente_data_nascimento" id="cliente_data_nascimento" class="form-control" >
                </div>
            </div>
        </div>
    
        <h3><i class="glyphicon glyphicon-lock"></i> &nbsp;Usuário</h3>
        <div class="panel panel-info">
            <div class="panel-heading">
                Dados do Usuário <i class="glyphicon glyphicon-lock pull-right"></i>
            </div>

            <div class="panel-body">

            <div class="row">
                <div class="col-md-6" >
                    <label for="login">Login</label>
                    <input type="text" readonly="readonly" name="login" id="login" class="form-control">
                </div>
             <div class="col-md-6" >&nbsp;</div>
            </div>

            <div class="col-md-12" >&nbsp;</div>
            
          <div class="row">
            <div class="col-md-6" >
                <label for="senha">Senha</label>
                <input type="password" name="senha" id="senha" class="form-control">
            </div>
            <div class="col-md-6" >
                <label for="confirmacaoSenha">Confirmação de Senha</label>
                <input type="password" name="confirmacaoSenha" id="confirmacaoSenha" class="form-control">
            </div>
              </div>

            </div>
        </div>
    
        <h3><i class="fa fa-credit-card"></i> Pagamento</h3>
        <div class="panel panel-info">
            <div class="panel-heading">
                Dados de Cobrança <i class="fa fa-credit-card pull-right"></i>
            </div>

            <div class="panel-body">
                <div class="col-md-5">
                    <label class="control-label" for="creditCardBrand">Bandeira</label>
                </div>
                <div class="form-group col-md-7">
                    <select name="creditCardBrand" id="creditCardBrand" class="form-control" style="font-family: 'FontAwesome', Helvetica;">
                        <option>- selecione -</option>
                        <option value="AmericamExpress">&#xf1f3; Americam Express</option>
                        <option value="MasterCard">&#xf1f1; MasterCard</option>
                        <option value="Visa">&#xf1f0; Visa</option>
                    </select>
                </div>

                <div class="col-md-5">
                    <label class="control-label" for="creditCardNumber">Número do Cartão de Crédito</label>
                </div>
                <div class="form-group col-md-7">
                    <input type="text" name="creditCardNumber" class="form-control" id="creditCardNumber" placeholder="1111 2222 3333 4444">
                </div>

                <div class="col-md-5">
                    <label class="control-label" for="creditCardHolderName">Nome no Cartão de Crédito</label>
                </div>
                <div class="form-group col-md-7">
                    <input type="text" name="creditCardHolderName" class="form-control" id="creditCardHolderName" placeholder="José D. Silva">
                </div>

                <div class="col-md-5">
                    <label class="control-label" for="creditCardExpMonth">Validade</label>
                </div>
                <div class="form-group col-md-3">
                    <input type="text" name="creditCardExpMonth" class="form-control" id="creditCardExpMonth" placeholder="Mês" maxlength="2">
                </div>
                <div class="form-group col-md-4">
                    <input type="text" name="creditCardExpYear" class="form-control" id="creditCardExpYear" placeholder="Ano" maxlength="4">
                </div>

                <div class="col-md-5">
                    <label class="control-label" for="creditCardSecurityCode">Código de Segurança PIN</label>
                </div>
                <div class="form-group col-md-7">
                    <input type="text" name="creditCardSecurityCode" class="form-control" id="creditCardSecurityCode" placeholder="123">
                </div>
            </div>
        </div>
    
        <h3><i class="fa fa-calendar"></i> &nbsp; Instalação</h3>
        <div class="panel panel-info">
            <div class="panel-heading">
                Agendamento da Instalação <i class="fa fa-calendar pull-right"></i>
            </div>

            <div class="panel-body">
                <div class="col-md-6" >
                    <label for="dataInstalacao">Data</label>
                    <input required="required" style="background: #FFF;" type="text" class="form-control" name="dataInstalacao" id="dataInstalacao">
                </div>

                <div class="col-md-6">
                    <label for="horaInstalacao">Horário</label><br>
                    <select required="required" class="form-control" name="horaInstalacao" id="horaInstalacao">
                        <option value="0">- selecione -</option>
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
</div>
<script type="text/javascript">
    var ProdutosIni;
    function Radio(val) {
        console.log(val);
         $.post( "<?=$apiURL?>admin-sell/search_attribute.php", {
                atributo:val,
                tipo:'tipoVeiculo',
                 })
        .done(function( data ) {
            ProdutosIni = data;
            $('#product_id').val(data);

            $("#fabricante_veiculo > option").each(function() {
     
                var toRemove = this.value;
                if(this.value > 0) {
                    $.post( "<?=$apiURL?>admin-sell/search_attribute.php", {
                            atributo:val,
                            prod:ProdutosIni,
                            fabricante: this.value,
                            pp:ProdutosIni
                    })
                    .done(function( data ) {
                        if(data.trim() == 0) {
                            $("#fabricante_veiculo option[value='"+toRemove+"']").hide();
                            console.log(data + ' - ' +toRemove);
                        } else {
                            $("#fabricante_veiculo option[value='"+toRemove+"']").show();
                            console.log(data + ' - ' +toRemove);
                        } 

                        $('#fabricante_veiculo').attr('disabled',false);
                    });
                }
            });
        });
    }

    function Select(val) {
        console.log(val);
        $('#modelo_veiculo').attr('disabled',true);

        if($('#product_id').val() === '' || $('#product_id').val()  ==='[]') {
            alerta('Recomece a seleção do Veículo');

            $('input[name=tipo_veiculo]').attr('checked',false);
        }

        $.post( "<?=$apiURL?>admin-sell/search_attribute.php", {
            atributo:val,
            ProdutosIni:ProdutosIni,
            tipo:'tipoVeiculo',
            pp:ProdutosIni
        })
        .done(function( data ) {
            $('#product_id').val(data);
            ProdutosIni = data;
            $("#modelo_veiculo > option").each(function() {
      
                var toRemove = this.value;

                if(this.value > 0){
                    $.post( "<?=$apiURL?>admin-sell/search_attribute.php", {
                            atributo:val,
                            pp:ProdutosIni,
                            prod:ProdutosIni,
                            fabricante: this.value
                    })
                    .done(function( data ) { 
                        if(data.trim() == 0) {
                            $("#modelo_veiculo option[value='"+toRemove+"']").hide();
                            console.log(data + ' - ' +toRemove);
                        } else {
                            $("#modelo_veiculo option[value='"+toRemove+"']").show();
                            console.log(data + ' - ' +toRemove);
                        }

                        $('#modelo_veiculo').attr('disabled',false);
                    });
                };
            });
        });
    }

    function Select2(val) {
        $('#ano_veiculo').attr('disabled',true);
        console.log(val);
        if($('#product_id').val() === '' || $('#product_id').val()  ==='[]')
        {
            alerta('Recomece a seleção do Veículo');
            $('input[name=tipo_veiculo]').attr('checked',false);
        }
         $.post( "<?=$apiURL?>admin-sell/search_attribute.php", {
                atributo:val,
                ProdutosIni:ProdutosIni,
                tipo:'tipoVeiculo',
                pp:ProdutosIni
                 })
        .done(function( data ) {
        $('#product_id').val(data);
        ProdutosIni = data;
        $("#ano_veiculo > option").each(function() {
     
        var toRemove = this.value;
        if(this.value > 0){
        $.post( "<?=$apiURL?>admin-sell/search_attribute.php", {
                atributo:val,
                pp:ProdutosIni,
                prod:ProdutosIni,
                fabricante: this.value
                 })
        .done(function( data ) { 
            if(data.trim() == 0) {
            $("#ano_veiculo option[value='"+toRemove+"']").hide();
            console.log(data);
                                }else{
            $("#ano_veiculo option[value='"+toRemove+"']").show();
            console.log(data);
                                } 
            $('#ano_veiculo').attr('disabled',false);

        });             
        };
        });
    });
    }

    function Select3(val) {
        if($('#product_id').val() === '' || $('#product_id').val() ==='[]') {
            alerta('Recomece a seleção do Veículo');
            $('input[name=tipo_veiculo]').attr('checked', false);
        }

        console.log(val);
        
        $.post(
            "<?=$apiURL?>admin-sell/search_attribute.php", 
            {
                atributo:val,
                ProdutosIni:ProdutosIni,
                tipo:'tipoVeiculo',
                pp:ProdutosIni
            }
        )
        .done(function( data ) {
            $('#product_id').val(data);
            ProdutosIni = data;
        })
    };

</script>
<script type="text/javascript">
$(':radio').prop('checked', false);

var UserID = $('.oe_topbar_avatar').attr('src').split('&')[2].replace('id=', '');
$("#user_id").val(UserID);
    
$('#salvar').click(function(event) {

    $('.alert-info').fadeOut();
    $('.alert-danger').fadeOut();

    if (!validaCamposVeiculo())
        return;

    if (!validaCamposCliente())
        return;

    if (!validaCamposAgendamento())
        return;

   if (!validaCamposUsuario())
        return;

    salvarCliente();
});

function validaCamposVeiculo() {

    if( $('#fabricante_veiculo').val()  != '0' &&
        $('#modelo_veiculo').val()      != '0' &&
        $('#veiculo_placa').val()       != ''  &&
        $('#ano_veiculo').val()         != '0' ) {

        return true;
    }

    alerta('Todos os Dados do Veículo são obrigatórios.');
    return false;
}

function validaCamposCliente() {

    if( 
        $('#cliente_email').val()               != '' &&
        $('#cliente_endereco').val()            != '' &&
        $('#cliente_estado').val()              != '' &&
        $('#cliente_cidade').val()              != '' &&
        $('#cliente_cep').val()                 != '' &&
        $('#cliente_senha').val()               != '' &&
        $('#cliente_cpf_cnpj').val()            != '' &&
        $('#cliente_data_nascimento').val()     != '' &&
        $('#cliente_telefone').val()            != '' ) {

        return true;
    }

    alerta('Todos os Dados do Cliente são obrigatórios.');
    return false;
}

function validaCamposAgendamento() {

    if($('#dataInstalacao').val() != '' && $('#horaInstalacao').val() != '0') {
        return true;
    }

    alerta('Todos os Dados da Instalação são obrigatórios.');
    return false;
}

function validaCamposUsuario() {

    if($('#senha').val() != '' && $('#confirmacaoSenha').val() != '0') {
        return true;
    }

    alerta('Todos os Dados do Usuário são obrigatórios.');
    return false;
}

function validaCamposPagamento() {

    if( 
        $('#creditCardBrand').val()         != '' &&
        $('#creditCardNumber').val()        != '' &&
        $('#creditCardHolderName').val()    != '' &&
        $('#creditCardExpYear').val()       != '' &&
        $('#creditCardExpMonth').val()      != '' &&
        $('#creditCardSecurityCode').val()  != '' &&
        $('#cliente_telefone').val()        != '' ) {

        return true;
    }

    alerta('Todos os Dados de Cobrança são obrigatórios.');
    return false;
}

function informa(msg) {

    $('.alert-info-msg').html(msg);
    $('.alert-info').fadeIn('slow');
}

function alerta(msg) {

    $('.alert-danger-msg').html(msg);
    $('.alert-danger').fadeIn('slow');
}

function salvarCliente() {
    
    $.ajax({
        url: "<?=$apiURL?>admin-sell/res_partner.php", 
        type: 'POST',
        data: {
            cliente_nome:       $('#cliente_nome').val(), 
            cliente_email:      $('#cliente_email').val(), 
            cliente_endereco:   $('#cliente_endereco').val(), 
            cliente_estado:     $('#cliente_estado').val(), 
            cliente_cidade:     $('#cliente_cidade').val(), 
            cliente_cep:        $('#cliente_cep').val(), 
            cliente_telefone:   $('#cliente_telefone').val(), 
            cliente_cpf_cnpj:   $('#cliente_cpf_cnpj').val(), 
            company_id:         $('#company_id').val(),  
            veiculo_placa:      $('#veiculo_placa').val(),
            password:           $('#senha').val()
        },
        dataType: "json",
        success: function(data) {
            
            if(data.ERROR != null && data.ERROR != '') {
                alerta("Erro ao adicionar cliente: " + data.ERROR);
            } else {
                informa('Cliente adicionado, processando as informações da venda, aguarde...');

                $('#partner_id').val(data.PARTNER_ID);
                var produto = $('#product_id').val().replace('[','').replace(']','');

                salvarVenda(produto);
            }
        }
    });
}

function salvarVenda(produto) {
    $.ajax({
        url: '<?=$apiURL?>admin-sell/sale_order.php', 
        type: 'POST',
        data: {
            partner_id:           parseInt($('#partner_id').val()),
            company_id:           $('#company_id').val(),
            user_id:              $('#user_id').val(),
            product_id:           produto
        },
        dataType: "json",
        success: function(data) {
            
            if(data.ERROR != null && data.ERROR != '') {
                alerta("Erro ao criar venda: " + data.ERROR);
            } else {
                $('#sale_order_id').val(data.ORDER_ID);
                informa('Venda adicionada, processando as informações do contrato, aguarde...');         
                GeraContrato(produto);
            }
        }
    });
}

function GeraContrato(produto) {
    $.ajax({
        url: '<?=$apiURL?>contract/create.php', 
        type: 'POST',
        data: {
            order_id: $('#sale_order_id').val(),
            partner_id: $('#partner_id').val(),
            product_contract_price: $('#product_contract_price').val(),
            product_contract_id: produto
        },
        dataType: "json",
        success: function(data) {
            
            if(data.ERROR != null && data.ERROR != '') {
                alerta("Erro ao criar contrato: " + data.ERROR);
            } else {
                informa('Contrato adicionado, chamando Plataforma, aguarde...');
                chamaPlataforma();
            }
        }
    });
}

function chamaPlataforma(){
    $.ajax({
      type: 'POST',
      url: '<?=$apiURL?>cc-payment/php-rest.php',
      data: {
        partnerId: $('#partner_id').val(), 
        orderId: $('#sale_order_id').val(), 
        creditCardHolderName: $('#creditCardHolderName').val(), 
        creditCardBrand: $('#creditCardBrand').val(), 
        creditCardNumber: $('#creditCardNumber').val(), 
        creditCardSecurityCode: $('#creditCardSecurityCode').val(), 
        creditCardExpMonth: $('#creditCardExpMonth').val(), 
        creditCardExpYear: $('#creditCardExpYear').val()
      },
      success: function(data) { 
        if (data.startsWith('OK')) {
            informa('Plataforma chamada com sucesso, processando as informações do agendamento, aguarde...');
            agendaInstalacao();
        } else {
            alerta("Erro ao chamar Plataforma: " + data);
        }
      }
    });
}

function agendaInstalacao() {

    $.post( "<?=$apiURL?>schedule-installation/schedule.php", { 
        partner_id:           $('#partner_id').val(),
        user_id:              $('#user_id').val(),
        order_id:             $('#sale_order_id').val(),
        localInstalacao:      $('#company_id').val(),
        dataInstalacao:       $('#dataInstalacao').val(),
        horaInstalacao:       $('#horaInstalacao').val()
    })
    .done(function( data ) {

        if (data.match(/[a-zA-Z]/i)) { // alphabet letters found, any error returned by the Odoo API
            alerta('Houve um problema ao processar as informações, está é a mensagem de retorno do servidor:<br>' + data);
        } else {
            informa("Todas as requisições foram executadas com sucesso.")
        }
    });
}
</script>
<script type="text/javascript">
    $(document).ready(function() {	
        
		$("#steps").steps({
                    headerTag: "h3", 
                    transitionEffect: "slideLeft",
                    enableCancelButton: true,
                    labels: {
                        cancel: "Cancelar",
                        current: "passo atual:",
                        pagination: "Paginação",
                        finish: "Finalizar",
                        next: "Próximo",
                        previous: "Anterior",
                        loading: "Carregando ..."
                    },
                    onStepChanging: function (event, currentIndex, newIndex) { 

                        $('.alert-info').fadeOut();
                        $('.alert-danger').fadeOut();

                        if (currentIndex > newIndex)
                            return true;

                        switch(currentIndex) {
                            case 0:
                                return validaCamposVeiculo();
                            case 1:
                                return validaCamposCliente();
                            case 2:
                                return validaCamposUsuario();
                            case 3:
                                return validaCamposPagamento();
                            default:
                                return true;
                        }
                    },
                    onFinishing: function (event, currentIndex) { 

                        $('.alert-info').fadeOut();
                        $('.alert-danger').fadeOut();

                        return validaCamposAgendamento();; 
                    },
                    onFinished: function (event, currentIndex) { 

                        return salvarCliente();
                    },
                    onCanceled: function (event, currentIndex) { 

                        $('.close').click();
                    },
                });

		        $('.js_variant_change').attr('disabled',true);

		        $('#cliente_email').change(function(event) {
		            $('#login').val($(this).val());
		        });

		        $(function() {
                    $('#dataInstalacao').datepicker({
                        dateFormat: 'dd/mm/yy',
                        beforeShowDay: $.datepicker.noWeekends,
                        minDate: new Date
                    })
                    
		            $('#cliente_data_nascimento').datepicker();
		        });
    });

/* Brazilian initialisation for the jQuery UI date picker plugin. */
/* Written by Leonildo Costa Silva (leocsilva@gmail.com). */
( function( factory ) {
    if ( typeof define === "function" && define.amd ) {
        // AMD. Register as an anonymous module.
        define( [ "../widgets/datepicker" ], factory );
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
