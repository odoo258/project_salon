odoo.define('web_studio.many2many_tags_email', function (require) {
"use strict";

var core = require('web.core');
var form_common = require('web.form_common');
var field_registry = require('web.field_registry');
var relational_fields = require('web.relational_fields');

var _t = core._t;

var FieldMany2ManyTags = relational_fields.FieldMany2ManyTags;

var FieldMany2ManyTagsEmail = FieldMany2ManyTags.extend({
    init: function() {
        this.values_checking = [];
        this._super.apply(this, arguments);
    },

    add_id: function (id) {
        var self = this;
        var _super = this._super.bind(this);
        // check partner has email
        this.trigger_up('perform_model_rpc', {
            model: 'res.partner',
            method: 'search',
            args: [[
                ["id", "=", id],
                ["email", "=", false],
                ["notify_email", "=", 'always']
            ]],
            on_success: function(partner_id) {
                if (partner_id.length) {
                    // invalid partner
                    var pop = new form_common.FormViewDialog(self, {
                        res_model: 'res.partner',
                        res_id: partner_id[0],
                        title: _t("Please complete partner's informations and Email"),
                    }).open();
                    pop.on('write_completed', self, function () {
                        // self.values_checking = _.without(self.values_checking, id);
                        _super.apply(self, [id]);
                    });
                } else {
                    // valid partner
                    _super.apply(self, [id]);
                }
            }
        });
    },
});

field_registry.add('many2many_tags_email', FieldMany2ManyTagsEmail);

});
