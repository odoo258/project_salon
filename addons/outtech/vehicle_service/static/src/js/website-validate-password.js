odoo.define('vehicle_service.year', function (require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function () {
        $('#password').change(function() {
            var vals = {  password: $('input[name="password"]').val() };
            ajax.jsonRpc("/password/validate", 'call', vals)
                .then(function(data) {
                    if(data == "menor"){
                        alert('Senha deve ter no mínimo 8 caracteres');
                        $('input[name="password"]').val('').focus();
                    }

                    if(data == "maior"){
                        alert('Senha deve ter no máximo 32 caracteres');
                        $('input[name="password"]').val('').focus();
                    }

                    if (data.sucesso){
                        $('input[name="password"]').val(data.password);
                    }
                }
            );
        });
    });

    $(document).ready(function () {
        $('#confirm_password').change(function() {
            var vals = {  password: $('input[name="password"]').val(),
                          confirm_password: $('input[name="confirm_password"]').val()};
            ajax.jsonRpc("/confirm-password/validate", 'call', vals)
                .then(function(data) {
                    if(data == "menor"){
                        alert('Senha deve ter no mínimo 8 caracteres');
                        $('input[name="confirm_password"]').val('').focus();
                    }

                    if(data == "maior"){
                        alert('Senha deve ter no máximo 32 caracteres');
                        $('input[name="confirm_password"]').val('').focus();
                    }

                    if(data == "diferente"){
                        alert('As duas senhas devem ser identicas.');
                        $('input[name="confirm_password"]').val('').focus();
                    }

                }
            );
        });
    });
});
