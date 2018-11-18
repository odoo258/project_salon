odoo.define('vehicle_service.plan', function (require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function () {

        $('#select_categ_ids').trigger('change');

        $('#select_categ_ids').change(function() {
            var vals = { categ: $(this).val() };
            ajax.jsonRpc("/shop/manufacturer", 'call', vals)
                .then(function(data) {
                    var selected = $('#input_manufacturer_id').val();
                    $('#select_manufacturer_ids').find('option').remove().end();
                    $('#select_manufacturer_ids').append('<option value="">Marca...</option>');
                    $.each(data, function(i, item) {
                        $('#select_manufacturer_ids').append($('<option>', {
                            value: item[0],
                            text: item[1],
                            selected: item[0]==selected?true:false,
                        }));
                    });
                    $('#select_manufacturer_ids').trigger('change');
                });
        });

        $('#select_manufacturer_ids').change(function() {
            var vals = { manufac: $(this).val(),
                         categ: $('#select_categ_ids').val()};
            ajax.jsonRpc("/shop/model", 'call', vals)
                .then(function(data) {
                    var selected = $('#input_model_id').val();
                    $('#select_model_ids').find('option').remove().end();
                    $('#select_model_ids').append('<option value="">Modelo...</option>');
                    $.each(data, function(i, item) {
                        $('#select_model_ids').append($('<option>', {
                            value: item[0],
                            text: item[1],
                            selected: item[0]==selected?true:false,
                        }));
                    });
                    $('#select_model_ids').trigger('change');
                });
        });

        $('#select_model_ids').change(function() {
            var vals = { modelo: $(this).val() };
            ajax.jsonRpc("/shop/year", 'call', vals)
                .then(function(data) {
                    var selected = $('#input_year_id').val();
                    $('#select_year_ids').find('option').remove().end();
                    $('#select_year_ids').append('<option value="">Ano...</option>');
                    $.each(data, function(i, item) {
                        $('#select_year_ids').append($('<option>', {
                            value: item[0],
                            text: item[1],
                            selected: item[0]==selected?true:false,
                        }));
                    });
                    $('#select_year_ids').trigger('change');
                });
        });
//
//        $('#btn_search_plan').on('click', function(e){
//            var model = $('#select_model_ids').val();
//            var year = $('#select_year_ids').val();
//                $.ajax({
//            url: '/shop/search_plan',
//            type: 'post',
//            data: {
//                'model': model,
//                'year': year
//            },
////            success: function (data) {
////                if(data=="ano_indisponivel"){
////                    bootbox.alert("Infelizmente não realizamos instalação para este modelo de carro do ano informado.");
////                }
////                if(data=="erro_plano"){
////                    bootbox.alert("O seu modelo carro não possui plano ou instalação disponíveis.");
////                }
////                else if(data=="ok"){
////                    location.href = "/shop";
////                }
////            },
////            error: function(data){
////                bootbox.alert("Algum erro ocorreu. Tente novamente mais tarde. Caso persista, entre em contato com o administrador");
////            }
//            });
//        });
//            var vals = {category: $('t[name="category_final"]'.val(),
//                        manufacturer: $('t[name="manufactorer_final"]'.val(),
//                        modelo: $('t[name="modelo_final"]'.val(), year: $('t[name="year_final"]').val()};
//            ajax.jsonRpc("/shop/search_plan", 'call', vals)
//                .then(function(data) {
//                    if(data.sucesso){
//                        $('input[name="district"]').val(data.district);
//                        $('input[name="street"]').val(data.street);
//                        $('select[name="country_id"]').val(data.country_id);
//                        $('select[name="country_id"]').change();
//                        $('select[name="state_id"]').val(data.state_id);
//                        $('#input_state_id').val(data.state_id);
//                        $('#input_city_id').val(data.city_id);
//                    }else{
//                        alert('Nenhum cep encontrado');
//                    }
//                }
//                );
    });
});
