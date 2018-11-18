odoo.define('vehicle_service.device-control', function (require) {
    var UserID = $('.oe_topbar_avatar').attr('src').split( '&' )[2].replace('id=','');
    $("#user_id").val(UserID);

    var TaskID = window.location.hash.split( '&' )[0].replace('id=','').replace('#','');
    $("#task_id").val(TaskID);

    $('#pesquisar').click(function() { Pesquisar(); });
    $('#salvar').click(function() { Salvar(); });

    var ledsTimeout;

    var ajax = require('web.ajax');

    function Pesquisar() {

        $('#device_buttons').fadeOut();
        clearTimeout(ledsTimeout);
        
        ajax.jsonRpc("/tracknme/device-control/search", 'call',
            {
            serial_number: $('#serial_number').val(),
            taskId: $('#task_id').val()
             }
        ).then(function (data) {

            if(data.DEVICE == '' || data.DEVICE == null ){
                alerta("Dispositivo não encontrado: " + data.ERROR);
            } else {
                informa("Dispositivo encontrado, iniciando habilitação...");

                Enable(data.DEVICE);
            }
        });
    }

    function Enable(id) {
        
        ajax.jsonRpc("/tracknme/device-control/enable", 'call',
            { 
                deviceId: id, 
                taskId: $('#task_id').val() 
            }
        ).then(function (data) {

            if(data.DEVICE_ID == '' || data.DEVICE_ID == null ){
                alerta("Dispositivo não habilitado: " + data.ERROR);
            } else {
                informa("Dispositivo habilitado, iniciando testes...");
                $('#device_buttons').fadeIn();
                ajax.jsonRpc("/tracknme/device-control/save_id", 'call',
                    {
                        equip: id,
                        deviceId: data.DEVICE_ID

                    }).then(function (result) {
                    if (result == true){
                        Testar_Device(data.DEVICE_ID);
                    }
                    else{
                        alerta("Dispositivo não Encontrado");
                        }
                    });

            }
        });
    }

    function Testar_Device(id) {
        
        ajax.jsonRpc("/tracknme/device-control/info", 'call',
            { 
                deviceId: id, 
            }
        ).then(function (data) {

            $('#device_buttons').fadeOut('fast');

            if(data.ERROR != null && data.ERROR != '' )
                ledsOff(data.ERROR);
            else
                ledsOn(data);

            if ($('#device_buttons').size() == 0)
                clearTimeout(ledsTimeout);
            else
                ledsTimeout = setTimeout(function() { Testar_Device(id) }, 3000);
        });
    }

    function ledsOn(data) {

        $('.alert-danger').fadeOut();

        if(data.ACC_OFF == 'ON'){
            $('#car-test').addClass('btn-success').removeClass('btn-danger btn-default');
            $('#car-test .status').html('Ligada');
        } else {
            $('#car-test').addClass('btn-danger').removeClass('btn-success btn-default');
            $('#car-test .status').html('Desligada');
        }

        if(data.GPS == 'OK') {
            $('#gps-test').addClass('btn-success').removeClass('btn-danger btn-default');
            $('#gps-test .status').html('Ligada');
        } else {
            $('#gps-test').addClass('btn-danger').removeClass('btn-success btn-default');
            $('#gps-test .status').html('Desligada');
        }

        if(data.GPS_VALID == false) {
            $('#gps-valid').addClass('btn-danger').removeClass('btn-success btn-default');
            $('#gps-valid .status').html('Invalida');
        } else {
            $('#gps-valid').addClass('btn-success').removeClass('btn-danger btn-default');
            $('#gps-valid .status').html('Válida');
        }

        $('#device_buttons').fadeIn('fast');
    }

    function ledsOff(error) {

        alerta("Testes insuficientes: " + error);

        $('#car-test').addClass('btn-default').removeClass('btn-danger btn-success');
        $('#car-test .status').html('');
        $('#gps-valid').addClass('btn-default').removeClass('btn-danger btn-success');
        $('#gps-valid .status').html('');
        $('#gps-test').addClass('btn-default').removeClass('btn-danger btn-success');
        $('#gps-test .status').html('');

        $('#device_buttons').fadeIn('fast');
    }

    function Salvar() {

        ajax.jsonRpc("/tracknme/contract/active", 'call',
            { 
                taskId: $('#task_id').val(),
                serial_number: $('#serial_number').val()
            }
        ).then(function (data) {

            if(data.CONTRACT_ID == '' || data.CONTRACT_ID == null ){
                alerta("Contrato não ativado: " + data.ERROR);
            } else {
                informa("Contrato ativado com sucesso. A tarefa já pode ser finalizada.");
                $('#salvar').attr('disabled', 'true');
            }
        });
    }

    function alerta(msg) {

        $('.alert-info').fadeOut();

        $('.alert-danger').fadeIn();
        $('.alert-danger-msg').html(msg);
    }

    function informa(msg) {

        $('.alert-danger').fadeOut();
        
        $('.alert-info').fadeIn();
        $('.alert-info-msg').html(msg);
    }

});