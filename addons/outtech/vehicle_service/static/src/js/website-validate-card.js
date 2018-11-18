odoo.define('vehicle_service.year', function (require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function () {
        $('#credit_card_display_number').change(function() {
            var vals = {  card_number: $('input[name="credit_card_display_number"]').val() };
            ajax.jsonRpc("/number/validate", 'call', vals)
                .then(function(data) {
                    if(data == "letras"){
                        alert('Digite um número de cartão apenas com números');
                        $('input[name="credit_card_display_number"]').val('').focus();
                    }

                    if(data == "menor"){
                        alert('Digite um número de cartão com 16 dígitos');
                        $('input[name="credit_card_display_number"]').val('').focus();
                    }

                    if (data.sucesso){
                        $('input[name="credit_card_display_number"]').val(data.card_number);
                    }
                }
            );
        });
    });

    $(document).ready(function () {
        $('#credit_card_month_expiration').change(function() {
            var vals = {  month: $('input[name="credit_card_month_expiration"]').val() };
                ajax.jsonRpc("/month/validate", 'call', vals)
                    .then(function(data) {
                        if(data == "menor"){
                            alert('Insira um mês com 2 caracteres');
                            $('input[name="credit_card_month_expiration"]').val('').focus();
                        }

                        if(data == "range"){
                            alert('Insira um mês maior que 0 e menor que 12');
                            $('input[name="credit_card_month_expiration"]').val('').focus();
                        }

                        if(data == "letras"){
                            alert('Insira um mês com apenas números');
                            $('input[name="credit_card_month_expiration"]').val('').focus();
                        }

                        if (data.sucesso){
                            $('input[name="credit_card_month_expiration"]').val(data.month);
                        }
                    }
                );
        });
    });

    $(document).ready(function () {
        $('#credit_card_year_expiration').change(function() {
            var vals = {  year: $('input[name="credit_card_year_expiration"]').val() };
            ajax.jsonRpc("/year/validate", 'call', vals)
                .then(function(data) {
                    if(data == "vencido"){
                        alert('Cartão de crédito com ano já vencido.');
                        $('input[name="credit_card_year_expiration"]').val('').focus();
                    }

                    if(data == "menor"){
                        alert('Insira um ano com 4 caracteres');
                        $('input[name="credit_card_year_expiration"]').val('').focus();
                    }

                    if(data == "letras"){
                        alert('Insira um ano com apenas números');
                        $('input[name="credit_card_year_expiration"]').val('').focus();
                    }

                    if (data.sucesso){
                        $('input[name="credit_card_year_expiration"]').val(data.year);
                    }
                }
            );
        });

    });
});
