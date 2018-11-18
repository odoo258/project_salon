odoo.define('vehicle_service.car', function (require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function () {
        $('#placa').change(function() {
            var vals = {  placa: $('input[name="placa"]').val() };
            ajax.jsonRpc("/placa/validate", 'call', vals)
                .then(function(data) {
                    if(data == "erro"){
                        alert('Placa já cadastrada');
                        $('input[name="placa"]').val('');
                    }

                    if (data == "tamanho"){
                        alert('Insira uma placa válida.');
                        $('input[name="placa"]').val('');
                    }

                    if (data == "letras"){
                        alert('Número cadastrado nas 3 letras iniciais da placa');
                        $('input[name="placa"]').val('');
                    }

                    if (data == "num"){
                        alert('Letra cadastrada nas 4 letras finais da placa');
                        $('input[name="placa"]').val('');
                    }

                    if (data.sucesso){
                    $('input[name="placa"]').val(data.placa);
                    }
                }
            );
        });
    });

});
