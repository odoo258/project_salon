//var options_cities = {
//    types: ['(regions)'],
//    componentRestrictions: {country: "br"}
//};
//
//var city_input;
//var street_input;
//
//function initialize() {
//    var city_input = document.getElementById('location');
//
//    var autocomplete_city = new google.maps.places.Autocomplete(city_input, options_cities);
//    geocoder = new google.maps.Geocoder();
//}
//google.maps.event.addDomListener(window, 'load', initialize);

odoo.define('vehicle_service.resellers', function (require) {
    "use strict";
    var ajax = require('web.ajax');

    $('#location').change(function() {
            var vals = {address: $('#location').val()};
            ajax.jsonRpc("/page/search_reseller", 'call', vals)
                .then(function(data) {
                    var selected = $('#input_model_id').val();
                    $('#reseller_ids').find('option').remove().end();
                    $('#reseller_ids').append('<option value="">Revendedor...</option>');
                    $.each(data, function(i, item) {
                        $('#reseller_ids').append($('<option>', {
                            value: item[0],
                            text: item[1],
                            selected: item[0]==selected?true:false,
                        }));
                    });
                    $('#reseller_ids').trigger('change');
                });
        });

});