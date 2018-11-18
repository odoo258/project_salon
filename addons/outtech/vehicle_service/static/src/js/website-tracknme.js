odoo.define('vehicle_service.year', function (require) {
    "use strict";

    var ajax = require('web.ajax');

    var nowTemp = new Date();
    var now = new Date(nowTemp.getFullYear(), nowTemp.getMonth(), nowTemp.getDate(), 0, 0, 0, 0);
        $(function(){
        $('#datetimepicker4').datetimepicker({
        minDate: nowTemp,
        pickTime: false,
        format: 'DD/MM/YYYY',
        startDate: '+0d',
        autoclose: true,
        onRender: function(date) {
                            return date.valueOf() &lt; now.valueOf() ? 'disabled' : '';}
        });
    });

    $(document).ready(function () {
        $('#datetimepicker4').change(function() {
            var vals = {  reseller_ids: $('select[name="reseller_ids"]').val(),
                            date_schedule: $('input[name="date_schedule"]').val()};
            ajax.jsonRpc("/reseller/validate", 'call', vals)
                .then(function(data) {
                    if(data.desabilitar.morning){
                        $('input[value="dia"]').attr('disabled', true);
                    }
                    else{
                        $('input[value="dia"]').removeAttr("disabled");
                    }


                    if(data.desabilitar.afternoon){
                        $('input[value="tarde"]').attr('disabled', true);
                    }
                    else{
                        $('input[value="tarde"]').removeAttr("disabled");
                    }

                    if(data.desabilitar.night){
                        $('input[value="noite"]').attr('disabled', true);
                    }
                    else{
                        $('input[value="noite"]').removeAttr("disabled");
                    }

                }
            );
        });
    });
});
