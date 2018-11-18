odoo.define('pos_ext.pos_ext', function (require) {
'use strict';

var gui = require('point_of_sale.gui');
var option = false;
var option_cpf = false;
var autorization_buttons = false;
var no_user = false;
var cpf = "";
var PosDB = require('point_of_sale.DB');
var cnpj = "";
var authorizer_user = null;
var authorizer_user_id = "";
var finalize = false;
var core = require('web.core');
var models = require('point_of_sale.models');
var _t = core._t;
var Model = require('web.DataModel');
var screens = require('point_of_sale.screens');
var chrome = require('point_of_sale.chrome');
var option_validate = {'value':false};
var option_pay = {'value':false, 'g':true};
var self = this;
var UserModel = new Model('res.users');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var popups = require('point_of_sale.popups');
var QWeb = core.qweb;
var Backbone = window.Backbone;
var DiscountT = DiscountFunc;
var host = "ws://localhost:2500";
var exports = {};


models.load_fields("account.journal", "payment_wallet");
models.load_fields("account.journal", "is_tef");
models.load_fields("account.journal", "operation_code");
models.load_fields("account.journal", "is_contingency");
models.load_fields("account.journal", "installments");
models.load_fields("account.journal", "pay_installments");
models.load_fields("res.partner", "wallet_partner");
models.load_fields("res.partner", "trust");
models.load_fields('pos.order','cpf_nfse');
models.load_fields('res.partner','cnpj_cpf');
models.load_fields('res.users','percent');
models.load_fields('res.users','value');
models.load_fields('res.users','user_allowed');
models.load_fields('res.users','user_password');
models.load_fields('res.users','discount_permission_id');
models.load_fields('res.users','date_validate');
models.load_fields('res.users','pos_salesperson');

var _super_NumpadWidget = screens.NumpadWidget.prototype;

PosDB.include({
    _partner_search_string: function(partner){
        var str =  partner.name;
        if(partner.barcode){
            str += '|' + partner.barcode;
        }
        if(partner.address){
            str += '|' + partner.address;
        }
        if(partner.phone){
            str += '|' + partner.phone.split(' ').join('');
        }
        if(partner.mobile){
            str += '|' + partner.mobile.split(' ').join('');
        }
        if(partner.email){
            str += '|' + partner.email;
        }
        if(partner.cnpj_cpf){
            str += '|' + partner.cnpj_cpf.split(".").join("").split("-").join("");
        }
        str = '' + partner.id + ':' + str.replace(':','') + '\n';
        return str;
    },
});

var OrderlineSuper = models.Orderline;
models.Orderline = models.Orderline.extend({
    get_display_price: function(){
        var qtd = 0;

        if(this.discount_fixed == 0) {
            qtd = this.get_quantity();
        }
        else{
            qtd = 1;
        }

        if (this.pos.config.iface_tax_included) {
            return (this.get_price_with_tax() * qtd);
        } else {
            return (this.get_base_price() * qtd);
        }
    }
});


var _paylineproto = models.Paymentline.prototype;
models.Paymentline = models.Paymentline.extend({

    init_from_JSON: function (json) {
        _paylineproto.init_from_JSON.apply(this, arguments);

        this.number_card = json.number_card;
        this.card_banner = json.card_banner;
        this.authorization_number = json.authorization_number;
        this.number_installment = json.number_installment;
        this.return_tef_reduced = json.return_tef_reduced;
        this.return_tef_client = json.return_tef_client;
        this.return_tef_cancel = json.return_tef_cancel;
        this.return_tef_establishment = json.return_tef_establishment;
    },

    export_as_JSON: function(){
        return _.extend(_paylineproto.export_as_JSON.apply(this, arguments), {number_card: this.number_card,
                                                                              card_banner: this.card_banner,
                                                                              authorization_number: this.authorization_number,
                                                                              number_installment: this.number_installment,
                                                                              return_tef_reduced: this.return_tef_reduced,
                                                                              return_tef_client: this.return_tef_client,
                                                                              return_tef_cancel: this.return_tef_cancel,
                                                                              return_tef_establishment: this.return_tef_establishment});
    },
});

var DiscountFunc = screens.NumpadWidget.include({
        init: function(parent) {
            this._super(parent);
            this.numpadparent=parent;
        },
        clickChangeMode: function(event) {
            var config = this.pos.config;
            var self = this;
            var ret = $.Deferred();
            var price_pwd = (config.is_password_price) ? config.password_price : config.is_password_price;
            var discount_pwd = (config.is_password_discount) ? config.password_discount : config.is_password_discount;

            console.log("current Target ===> " + event.currentTarget.attributes['data-mode'].value)
            var newMode = event.currentTarget.attributes['data-mode'].value;
            console.log("New Mode ===> " + newMode)

            //=========== Calling Super ((Parent)) ================
            var tmp = this._super.apply(this, arguments);
            //=====================================================
            option_pay['value'] = false
            var date_today = new Date();
            var ret = new $.Deferred();
            var salesperson = this.pos.cashier || this.pos.user;
            if (newMode == "discount" || newMode == "discount_total" || newMode == "discount_percent"  || newMode == "discount_fixed" && discount_pwd) {
                self.gui.show_popup('textinput',{
                        title: _t('Desconto'),
                        'value': "",
                        confirm:function(value) {
//                            if (line_selected.discount){
//                                var desc = self.state.attributes.buffer + event.currentTarget.innerText;
//                            }
//                            else{
//                                var desc = event.currentTarget.innerText;
//                            }
                            if (isNaN(parseFloat(value))){
                                self.gui.show_popup('error',_t("You must insert only numbers."));
                                return false;
                            }
                            value = value.replace(",", ".")
                            date_today.setHours(0);
                            date_today.setMinutes(0);
                            date_today.setSeconds(0);
                            date_today.setMilliseconds(0);

                            var desc_percent = value;

                            if (salesperson && date_today <= moment(salesperson.date_validate).toDate()){
                                if (salesperson && parseFloat(value) > parseFloat(salesperson.percent)){
                                    var authorize_teste = self.autorizePasswordSelect();
                                    self.gui.show_popup('selection',{
                                        'title': _t('Select Authorizer'),
                                        'list': authorize_teste,
                                        'confirm': function(user_selected){
                                            authorizer_user = user_selected;
                                            authorizer_user_id = authorizer_user.id;
                                            var discount_pwd = authorizer_user.user_password;
                                            option_pay.gui.ask_password(discount_pwd).then(function() {
                                                return self.state.appendNewChar(desc_percent);
                                            });
                                            },
                                        'cancel':  function(){ ret.reject(); },
                                    });
                                }
                                else{
                                    //var newChar = event.currentTarget.innerText || event.currentTarget.textContent;
                                    self.state.appendNewChar(desc_percent);
                                }
                            }else{
                                var authorize_teste = self.autorizePasswordSelect();
                                    self.gui.show_popup('selection',{
                                        'title': _t('Select Authorizer'),
                                        'list': authorize_teste,
                                        'confirm': function(user_selected){
                                            authorizer_user = user_selected;
                                            authorizer_user_id = authorizer_user.id;
                                            var discount_pwd = authorizer_user.user_password;
                                            option_pay.gui.ask_password(discount_pwd).then(function() {
                                                return self.state.appendNewChar(desc_percent);
                                            });
                                            },
                                        'cancel':  function(){ ret.reject(); },
                                    });
                            }
                            },

                        });
                //var newMode = event.currentTarget.attributes['data-mode'].value;
                return self.state.changeMode(newMode);
                console.log("DISCOUNT!!!")
            }

            else if (newMode == "price" && price_pwd) {
                var newMode = event.currentTarget.attributes['data-mode'].value;
                return self.state.changeMode(newMode);
                console.log("PRICE!!!")
            }
            else
                var newMode = event.currentTarget.attributes['data-mode'].value;
                return self.state.changeMode(newMode);
                console.log("QUANTITY!!!")
        },
        autorizePasswordSelect: function(){
            var def  = new $.Deferred();
            var self = this;
            var authorized_list = [];

            var select_list = [];
            for (var i = 0; i < this.pos.users.length; i++) {
                var user1 = this.pos.users[i];
                if (user1.user_password != false) {
                    option_pay['gui'] = this.gui;
                    authorized_list.push({
                        'label': user1.name,
                        'item':  user1,
                    });
                }
            }

            return authorized_list;

        },
        clickSwitchSign: function() {
            var self = this;
            var $el = $(this);
            autorization_buttons = true;
            var ret = new $.Deferred();
            var state = this.state.deleteLastChar;
            var authorize_teste = self.autorizePasswordSelect();
            self.gui.show_popup('selection',{
                'title': _t('Select Authorizer'),
                'list': authorize_teste,
                'confirm': function(user_selected){
                    authorizer_user = user_selected;
                    authorizer_user_id = authorizer_user.id;
                    var discount_pwd = authorizer_user.user_password;
                    self.gui.ask_password(discount_pwd).then(function() {
                        autorization_buttons = false;
                        option_pay['value'] = false;
                        return $(self).find('.numpad-minus').prevObject[0].state.switchSign();
                    });
                },
                'cancel':  function(){ ret.reject(); },
            });
        },
        clickDeleteLastChar: function(){
            var self = this;
            var $el = $(this);
            var ret = new $.Deferred();
            var state = this.state.deleteLastChar;
            var authorize_teste = self.autorizePasswordSelect();
            var currentTarget = this.state.attributes['mode'];
            if (currentTarget == 'price'){
                self.gui.show_popup('selection',{
                    'title': _t('Select Authorizer'),
                    'list': authorize_teste,
                    'confirm': function(user_selected){
                        authorizer_user = user_selected;
                        authorizer_user_id = authorizer_user.id;
                        var discount_pwd = authorizer_user.user_password;
                        option_pay.gui.ask_password(discount_pwd).then(function() {
                            return $(self).find('.numpad-backspace').prevObject[0].state.deleteLastChar();
                        });
                    },
                    'cancel':  function(){ ret.reject(); },
                });
            }
            else{
                return $(self).find('.numpad-backspace').prevObject[0].state.deleteLastChar();
            }

        },
        clickAppendNewChar: function(event) {
            var newChar;
            var self = this;
            var g = this.gui;
            var type = this.state.get('mode');
            var config = this.pos.config;
            var user = this.pos.user;
            var price_pwd = (config.is_password_price) ? config.password_price : config.is_password_price;
            var salesperson = this.pos.cashier || this.pos.user;
            var order = this.pos.get_order();
            var lines = order.get_orderlines();
            var product = order.selected_orderline.product;
            var line_selected = order.selected_orderline;
            var desc = "0";
            var date_today = new Date();
            var ret = new $.Deferred();
            option_pay['type'] = 'discount';
            if (event != undefined){
                option_pay['event'] = event;
            }
            option_pay['obj'] = this._super;

            var date_formated = date_today.toJSON().substr(0, 10);
            var discountPermissionLineModel = new Model('discount.permission.line');
            var domain = [['date_validate', '>=', date_formated], ['user_id', '=', salesperson.id]];
               if (option_pay['value'] !== true && (!isNaN(event.currentTarget.innerText))){
                if (type === 'discount'){
                        return $('.selected-mode').click();
//                        self.gui.show_popup('textinput',{
//                        title: _t('Insira o desconto desejado'),
//                        'value': "",
//                        confirm:function(value) {
////                            if (line_selected.discount){
////                                var desc = self.state.attributes.buffer + event.currentTarget.innerText;
////                            }
////                            else{
////                                var desc = event.currentTarget.innerText;
////                            }
//                            var desc_percent = value;
//                            date_today.setHours(0);
//                            date_today.setMinutes(0);
//                            date_today.setSeconds(0);
//                            date_today.setMilliseconds(0);
//
//                            if (salesperson && date_today <= moment(salesperson.date_validate).toDate()){
//                                if (salesperson && parseFloat(value) > parseFloat(salesperson.percent)){
//                                    var authorize_teste = self.autorizePasswordSelect();
//                                    self.gui.show_popup('selection',{
//                                        'title': _t('Select Authorizer'),
//                                        'list': authorize_teste,
//                                        'confirm': function(user_selected){
//                                            authorizer_user = user_selected;
//                                            authorizer_user_id = authorizer_user.id;
//                                            var discount_pwd = authorizer_user.user_password;
//                                            option_pay.gui.ask_password(discount_pwd).then(function() {
//                                                return self.state.appendNewChar(desc_percent);
//                                            });
//                                            },
//                                        'cancel':  function(){ ret.reject(); },
//                                    });
//                                }
//                                else{
//                                    //var newChar = event.currentTarget.innerText || event.currentTarget.textContent;
//                                    self.state.appendNewChar(desc_percent);
//                                }
//                            }else{
//                                var authorize_teste = self.autorizePasswordSelect();
//                                    self.gui.show_popup('selection',{
//                                        'title': _t('Select Authorizer'),
//                                        'list': authorize_teste,
//                                        'confirm': function(user_selected){
//                                            authorizer_user = user_selected;
//                                            authorizer_user_id = authorizer_user.id;
//                                            var discount_pwd = authorizer_user.user_password;
//                                            option_pay.gui.ask_password_ext(discount_pwd).then(function() {
//                                                return ret.resolve();
//                                            });
//                                            },
//                                        'cancel':  function(){ ret.reject(); },
//                                    });
//                            }
//                            },
//
//                        });
                        }
                        if (type === 'discount_total'){
                            if (line_selected.discount_total){
                                var desc = line_selected.discount_total + event.currentTarget.innerText;
                            }
                            else{
                                var desc = event.currentTarget.innerText;
                            }

                            date_today.setHours(0);
                            date_today.setMinutes(0);
                            date_today.setSeconds(0);
                            date_today.setMilliseconds(0);

                            if (salesperson && date_today <= moment(salesperson.date_validate).toDate()){
                                if (salesperson && parseFloat(desc) > parseFloat(salesperson.value)){
                                    var authorize_teste = self.autorizePasswordSelect();
                                    self.gui.show_popup('selection',{
                                        'title': _t('Select Authorizer'),
                                        'list': authorize_teste,
                                        'confirm': function(user_selected){
                                            authorizer_user = user_selected;
                                            authorizer_user_id = authorizer_user.id;
                                            var discount_pwd = authorizer_user.user_password;
                                            option_pay.gui.ask_password_ext(discount_pwd).then(function() {
                                                return ret.resolve();
                                            });
                                            },
                                        'cancel':  function(){ ret.reject(); },
                                    });
                                }
                                else{
                                    var newChar = event.currentTarget.innerText || event.currentTarget.textContent;
                                    self.state.appendNewChar(newChar);
                                }
                            }else{
                                var authorize_teste = self.autorizePasswordSelect();
                                    self.gui.show_popup('selection',{
                                        'title': _t('Select Authorizer'),
                                        'list': authorize_teste,
                                        'confirm': function(user_selected){
                                            authorizer_user = user_selected;
                                            authorizer_user_id = authorizer_user.id;
                                            var discount_pwd = authorizer_user.user_password;
                                            option_pay.gui.ask_password_ext(discount_pwd).then(function() {
                                                return ret.resolve();
                                            });
                                            },
                                        'cancel':  function(){ ret.reject(); },
                                    });
                            }
                        }
                        if (type === 'discount_fixed'){
                            if (line_selected.discount_fixed){
                                var desc = line_selected.discount_fixed + event.currentTarget.innerText;
                            }
                            else{
                                var desc = event.currentTarget.innerText;
                            }

                            date_today.setHours(0);
                            date_today.setMinutes(0);
                            date_today.setSeconds(0);
                            date_today.setMilliseconds(0);

                            if (salesperson && date_today <= moment(salesperson.date_validate).toDate()){
                                if (salesperson && parseFloat(desc) > parseFloat(salesperson.percent)){
                                    var authorize_teste = self.autorizePasswordSelect();
                                    self.gui.show_popup('selection',{
                                        'title': _t('Select Authorizer'),
                                        'list': authorize_teste,
                                        'confirm': function(user_selected){
                                            authorizer_user = user_selected;
                                            authorizer_user_id = authorizer_user.id;
                                            var discount_pwd = authorizer_user.user_password;
                                            option_pay.gui.ask_password_ext(discount_pwd).then(function() {
                                                return ret.resolve();
                                            });
                                            },
                                        'cancel':  function(){ ret.reject(); },
                                    });
                                }
                                else{
                                    var newChar = event.currentTarget.innerText || event.currentTarget.textContent;
                                    self.state.appendNewChar(newChar);
                                }
                            }else{
                                var authorize_teste = self.autorizePasswordSelect();
                                    self.gui.show_popup('selection',{
                                        'title': _t('Select Authorizer'),
                                        'list': authorize_teste,
                                        'confirm': function(user_selected){
                                            authorizer_user = user_selected;
                                            authorizer_user_id = authorizer_user.id;
                                            var discount_pwd = authorizer_user.user_password;
                                            option_pay.gui.ask_password_ext(discount_pwd).then(function() {
                                                return ret.resolve();
                                            });
                                            },
                                        'cancel':  function(){ ret.reject(); },
                                    });
                            }
                        }
                        if (type === 'discount_percent'){
                            if (line_selected.discount_percent){
                                var desc = line_selected.discount_percent + event.currentTarget.innerText;
                            }
                            else{
                                var desc = event.currentTarget.innerText;
                            }

                            date_today.setHours(0);
                            date_today.setMinutes(0);
                            date_today.setSeconds(0);
                            date_today.setMilliseconds(0);

                            if (salesperson && date_today <= moment(salesperson.date_validate).toDate()){
                                if (salesperson && parseFloat(desc) > parseFloat(salesperson.percent)){
                                    var authorize_teste = self.autorizePasswordSelect();
                                    self.gui.show_popup('selection',{
                                        'title': _t('Select Authorizer'),
                                        'list': authorize_teste,
                                        'confirm': function(user_selected){
                                            authorizer_user = user_selected;
                                            authorizer_user_id = authorizer_user.id;
                                            var discount_pwd = authorizer_user.user_password;
                                            option_pay.gui.ask_password_ext(discount_pwd).then(function() {
                                                return ret.resolve();
                                            });
                                            },
                                        'cancel':  function(){ ret.reject(); },
                                    });
                                }
                                else{
                                    var newChar = event.currentTarget.innerText || event.currentTarget.textContent;
                                    self.state.appendNewChar(newChar);
                                }
                            }else{
                                var authorize_teste = self.autorizePasswordSelect();
                                    self.gui.show_popup('selection',{
                                        'title': _t('Select Authorizer'),
                                        'list': authorize_teste,
                                        'confirm': function(user_selected){
                                            authorizer_user = user_selected;
                                            authorizer_user_id = authorizer_user.id;
                                            var discount_pwd = authorizer_user.user_password;
                                            option_pay.gui.ask_password_ext(discount_pwd).then(function() {
                                                return ret.resolve();
                                            });
                                            },
                                        'cancel':  function(){ ret.reject(); },
                                    });
                            }
                        }
                        else if (type == 'quantity'){
                            option_pay['value'] = false;
                            var oldBuffer = self.state.attributes.buffer;
                            var newChar = event.currentTarget.innerText || event.currentTarget.textContent;
                            if (line_selected.quantity){
                                var qty = line_selected.quantity + event.currentTarget.innerText;
                            }
                            else{
                                var qty = event.currentTarget.innerText;
                            }
                            if (parseFloat(qty) == 0 || (oldBuffer == 0 && newChar == 0)){
                                self.gui.show_popup('error',_t("Quantity can't be equal to 0."));
                                return false;
                            }
                            self.state.appendNewChar(newChar);
                        }
                        else if (type == 'price'){
                            var authorize_teste = self.autorizePasswordSelect();
                                self.gui.show_popup('selection',{
                                    'title': _t('Select Authorizer'),
                                    'list': authorize_teste,
                                    'confirm': function(user_selected){
                                        authorizer_user = user_selected;
                                        authorizer_user_id = authorizer_user.id;
                                        var discount_pwd = authorizer_user.user_password;
                                        option_pay.gui.ask_password_ext(discount_pwd).then(function() {
                                            return ret.resolve();
                                        });
                                        },
                                    'cancel':  function(){ ret.reject(); },
                                });
                        }
                }
                else{
                    if (autorization_buttons == false){
                        option_pay['value'] = false;
                        var newChar = event.currentTarget.innerText || event.currentTarget.textContent;
                        self.state.appendNewChar(newChar);
                    }
                }
            },
});

var SalespersonButton = screens.ActionButtonWidget.extend({
    template: 'SalespersonButton',
    exist: function(verify){
        if(verify || option == true){
            option = true;
            return 'ok';
        }
        else{
            return 'no';
        }
    },
    get_cashier: function(){
        return this.user || this.pos.user;
    },
    finalize: function(finalize){
        if (finalize == true){
            this.cashier_name();
            return true;
        }
        else{
            return false;
        }
    },
    renderElement: function(){
        var self = this;
        this._super();

        if (finalize == true){
            option = false;
            no_user = true;
            self.finalize(finalize);
            finalize = false;
        }

        this.$('.control-button').click(function(){
            self.button_click();
        });
    },
    select_cashier: function(options){
        options = options || {};
        var self = this;
        var def  = new $.Deferred();
        var no_salesperson = [{
            label: _t("None"),
        }];

        var list = [];
        for (var i = 0; i < this.pos.users.length; i++) {
            var user = this.pos.users[i];
            //if (!options.only_managers || user.role === 'manager') {
            if (user.pos_salesperson != false) {
                list.push({
                    'label': user.name,
                    'item':  user,
                });
            }
        }

        var selection_list = no_salesperson.concat(list);

        this.gui.show_popup('selection',{
            'title': options.title || _t('Select User'),
            list: selection_list,
            confirm: function(user){ def.resolve(user); },
            cancel:  function(){ def.reject(); },
        });

        return def.then(function(user){
            return user;
        });
    },
    button_click: function(){
        var self = this;
        self.select_cashier({
            'current_user': "",
            'title':      _t('Escolher Vendedor'),
        }).then(function(user){
            if (!user){
                no_user = true;
                user = self.pos.user || self.pos.cashier;
                self.pos.set_cashier(user);
            }
            else{
                no_user = false;
                self.pos.set_cashier(user);
            }
            self.exist(user);
            self.renderElement();

        });
    },
    cashier_name: function(){
        if (this.pos != undefined){
            var user = this.pos.get_cashier();
        }
        else{
            no_user = true;
        }
        if(user && no_user != true){
            return user.name;
        }
        else if (no_user == true){
            return "None";
        }
        else{
            return "";
        }
    },
});

gui.Gui.extend({

    numpad_input: function(buffer, input, options) {
            var newbuf  = buffer.slice(0);
            options = options || {};
            var newbuf_float  = formats.parse_value(newbuf, {type: "float"}, 0);
            var decimal_point = _t.database.parameters.decimal_point;

            if (input === decimal_point) {
                if (options.firstinput) {
                    newbuf = "0.";
                }else if (!newbuf.length || newbuf === '-') {
                    newbuf += "0.";
                } else if (newbuf.indexOf(decimal_point) < 0){
                    newbuf = newbuf + decimal_point;
                }
            } else if (input === 'CLEAR') {
                newbuf = "";
            } else if (input === 'BACKSPACE') {
                newbuf = newbuf.substring(0,newbuf.length - 1);
            } else if (input === '+') {
                if ( newbuf[0] === '-' ) {
                    newbuf = newbuf.substring(1,newbuf.length);
                }
            } else if (input === '-') {
                if ( newbuf[0] === '-' ) {
                    newbuf = newbuf.substring(1,newbuf.length);
                } else {
                    newbuf = '-' + newbuf;
                }
            } else if (input[0] === '+' && !isNaN(parseFloat(input))) {
                newbuf = this.chrome.format_currency_no_symbol(newbuf_float + parseFloat(input));
            } else if (!isNaN(parseInt(input))) {
                if (options.firstinput) {
                    newbuf = '' + input;
                } else {
                    newbuf += input;
                }
            }

            // End of input buffer at 12 characters.
            if (newbuf.length > buffer.length && newbuf.length > 12) {
                this.play_sound('bell');
                return buffer.slice(0);
            }

            return newbuf;
        },

});


gui.Gui.include({
    select_user: function(options){
        options = options || {};
        var self = this;
        var def  = new $.Deferred();

        var list = [];
        for (var i = 0; i < this.pos.users.length; i++) {
            var user = this.pos.users[i];
            if (!options.only_managers || user.role === 'manager') {
                list.push({
                    'label': user.name,
                    'item':  user,
                });
            }
        }

        return def.then(function(user){
            if (options.security && user !== options.current_user && user.pos_security_pin) {
                return self.ask_password(user.pos_security_pin).then(function(){
                    return user;
                });
            } else {
                return user;
            }
        });
    },

    select_installments: function(installment){
        var self = this;
        var def  = new $.Deferred();

        var list = [];
        for (var i = 1; i <= installment[1]; i++) {
            if ( i == 1){
                list.push({
                    'label': 'Parcela única',
                    'item': i,
                });
            }
            else{
                list.push({
                    'label': 'Parcelar em ' + i + 'x',
                    'item': i,
                });
            }
        }

        return list;
    },
});


var CpfButton = screens.ActionButtonWidget.extend({
    template: 'CpfButton',
    valida_cpf: function(c){
        if (c == ""){
            return true;
        }

        c = c.replace(/[^\d]+/g,'');   
        var i;
        var s = c;
        var c = s.substr(0,9);
        var dv = s.substr(9,2);
        var d1 = 0;

        for (i = 0; i < 9; i++){
            d1 += c.charAt(i)*(10-i);
        }
        if (d1 == 0){
            return false;
        }
        d1 = 11 - (d1 % 11);
        if (d1 > 9) d1 = 0;
        if (dv.charAt(0) != d1){
            return false;
        }

        d1 *= 2;
        for (i = 0; i < 9; i++){
            d1 += c.charAt(i)*(11-i);
        }
        d1 = 11 - (d1 % 11);
        if (d1 > 9) d1 = 0;
        if (dv.charAt(1) != d1){
            return false;
        }
    },
    get_cnpj: function(){
        return cnpj;
    },
    set_cnpj: function(cpf_nfse){
        cnpj = cpf_nfse;
    },
    get_cpf: function(){
        return cpf;
    },
    set_cpf: function(cpf_nfse){
        cpf = cpf_nfse;
    },
    renderElement: function(){
        var self = this;
        this._super();
        cpf = "";

        this.$el.click(function(){
            option_cpf = false;
            self.button_click();
        })
    },
    partner_cpf: function(){
        var self = this;
        var partner_id = this.pos.get_order().get_client();
        if (partner_id && option_cpf == false){
            var v = partner_id.cnpj_cpf;
            if (!v){
                self.set_cpf("");
                self.set_cnpj("");
                return false;
            }
            v = v.replace(/[^\d]+/g,'');
            if (v.length == 11){
                self.set_cpf(v);
                return v;
            }
            else if(v.length == 14){
                self.set_cnpj(v);
                return v;
            }
        }
        else{
            return false;
        }
    },
    button_click: function(){
        var self = this;
        var partner_id = self.partner_cpf();
        if (partner_id != false){
            var v = self.get_cpf();
            v = v.replace(/(\d{3})(\d)/,"$1.$2");

            //Coloca um ponto entre o terceiro e o quarto dígitos
            //de novo (para o segundo bloco de números)
            v = v.replace(/(\d{3})(\d)/,"$1.$2");

            //Coloca um hífen entre o terceiro e o quarto dígitos
            v = v.replace(/(\d{3})(\d{1,2})$/,"$1-$2");
            this.gui.show_popup('textinput',{
                    title: _t('CPF na Nota Paulista'),
                    'value': v,
                    confirm: function(value) {
                    var valida = self.valida_cpf(value);
                    if (valida == false){
                        self.gui.show_popup('error',_t('CPF inválido!'));
                        self.button_click();
                    }
                    else{
                        option_cpf = true;
                        value = value.replace(/[^\d]+/g,'');
                        self.set_cpf(value);
                    }
                },
            });
        }
        else if (self.get_cpf() != false){
            var v = cpf;
            v = v.replace(/(\d{3})(\d)/,"$1.$2");

            //Coloca um ponto entre o terceiro e o quarto dígitos
            //de novo (para o segundo bloco de números)
            v = v.replace(/(\d{3})(\d)/,"$1.$2");

            //Coloca um hífen entre o terceiro e o quarto dígitos
            v = v.replace(/(\d{3})(\d{1,2})$/,"$1-$2");
            this.gui.show_popup('textinput',{
                title: _t('CPF na Nota Paulista'),
                'value': v,
                confirm: function(value) {
                    var valida = self.valida_cpf(value);
                    if (valida == false){
                        self.gui.show_popup('error',_t('CPF inválido!'));
                        self.button_click();
                    }
                    else{
                        option_cpf = true;
                        value = value.replace(/[^\d]+/g,'');
                        self.set_cpf(value);
                    }
                },
            });
        }else{
            this.gui.show_popup('textinput',{
                title: _t('CPF na Nota Paulista'),
                'value': "",
                confirm: function(value) {
                    var valida = self.valida_cpf(value);
                    if (valida == false){
                        self.gui.show_popup('error',_t('CPF inválido!'));
                        self.button_click();
                    }
                    else{
                        option_cpf = true;
                        value = value.replace(/[^\d]+/g,'');
                        self.set_cpf(value);
                    }
                },
            });
        }
    },
});

var CancelTefButton = screens.ActionButtonWidget.extend({
    template: 'CancelTefButton',

    confirmacao_cancel: function(value) {

              var numTrans = value;

              var ws = new WebSocket(host);
                ws.onopen = function() {
                    var transacao = this;

                    if (numTrans.value != "")  {
                      transacao.numeroTransacao = numTrans.value;
                    }

                    transacao.operacao = 6;
                    ws.send(JSON.stringify(transacao));
                };

              ws.onmessage = function(evt) {
                var msg = evt.data;
                var obj = JSON.parse(msg);

                if (obj.retorno == 0 || obj.retorno == 13) {
//                    alert("Transacao confirmada!");
                      return 'ok'
                } else {
                    alert("Nao foi possivel confirmar a transacao. retorno: "
                          + obj.retorno + ", erro: " + obj.codigoErro);
                }

                //resetCupom();

              };
          },


    cancel_tef: function(value) {
          var self = this;
          var opt = {};
          var numTrans = value;
          var posOrderModel = new Model('pos.order');
          var order = this.pos.get_order();
          var cupomEstab = {};
          var cupomCliente = {};
          var ws = new WebSocket('ws://localhost:2500');
            ws.onopen = function() {
                var transacao = this;
                transacao.operacao = 128;
                ws.send(JSON.stringify(transacao));
            };

          ws.onmessage = function(evt) {
            var msg = evt.data;
            var obj = JSON.parse(msg);

            if (obj.retorno == 0 || obj.retorno == 13) {
                if (obj.cupomEstabelecimento != null) {
                  var linhas = "";
                  for (var i=0; i < obj.cupomEstabelecimento.length; i++){
                   linhas += obj.cupomEstabelecimento[i].linha + "</br>";
                  }
                    //alert(linhas);
                    cupomEstab.innerHTML = linhas;
                }

                if (obj.cupomCliente != null) {
                  var linhas = "";
                  for (var i=0; i < obj.cupomCliente.length; i++){
                   linhas += obj.cupomCliente[i].linha + "</br>";
                  }
                    //alert(linhas);
                    cupomCliente.innerHTML = linhas;
                }
                posOrderModel.call('print_receipt_tef',[cupomCliente.innerHTML,cupomEstab.innerHTML,order.pos.config]).then(function(valida){
                                                if (valida['result'] == false){
                                                    self.gui.show_popup('error',_t('No printer connection!'));
                                                }
                            })
                self.confirmacao_cancel(obj.nsuCTF);
                opt['return_tef_cancel'] = cupomEstab.innerHTML;
                alert("Transacao Cancelada!");
            } else {
                alert("Nao foi possivel cancelar a transacao. retorno: "
                      + obj.retorno + ", erro: " + obj.codigoErro);
            }



            //resetCupom();

          };

      },

    button_click: function(){
        var self = this;
        this.gui.show_popup('textinput',{
                title: _t('Numero da Transação'),
                'value': '',
                confirm: function(value) {
                var valida = self.cancel_tef(value);

            },
        });
    }
});

screens.define_action_button({
    'name': 'cancel_tef',
    'widget': CancelTefButton,
});

var CancelCupomButton = screens.ActionButtonWidget.extend({
    template: 'CancelCupomButton',

    cancel_cupom: function(value){
    var posOrderModel = new Model('pos.order');
    var session_id = this.pos.pos_session.id
    var self = this;
    posOrderModel.call('cancel_cupom_sat',[value,session_id]).then(function(valida){
    if (valida['result'] == false){
            self.gui.show_popup('error',_t('Chave inválido!'));
        }
    else{
            self.gui.show_popup('error',_t('Cupom Cancelado com sucesso!'));
            option_cpf = true;
        }

    })
    },

    button_click: function(){
        var self = this;
        this.gui.show_popup('textinput',{
                title: _t('Chave de Cupom'),
                'value': '',
                confirm: function(value) {
                var valida = self.cancel_cupom(value);

            },
        });
    }
});

screens.define_action_button({
    'name': 'cancel_cupom',
    'widget': CancelCupomButton,
});

var ReprintCupomButton = screens.ActionButtonWidget.extend({
    template: 'ReprintCupomButton',

    reprint_cupom: function(value){
        var posOrderModel = new Model('pos.order');
        var session_id = this.pos.pos_session.id
        var self = this;
    posOrderModel.call('reprint_cupom_sat',[value,session_id]).then(function(valida){
    if (valida == false){
            self.gui.show_popup('error',_t('Chave inválido!'));
        }
    else{
            self.gui.show_popup('error',_t('Cupom Reimpressão com sucesso!'));
            option_cpf = true;
        }

    })
    },

    button_click: function(){
        var self = this;
        this.gui.show_popup('textinput',{
                title: _t('Chave de Cupom'),
                'value': '',
                confirm: function(value) {
                var valida = self.reprint_cupom(value);
            },
        });
    }
});

screens.define_action_button({
    'name': 'reprint_cupom',
    'widget': ReprintCupomButton,
});

screens.ActionpadWidget.include({
    valida_cpf: function(c){
        if (c == ""){
            return true;
        }

        c = c.replace(/[^\d]+/g,'');   
        var i;
        var s = c;
        var c = s.substr(0,9);
        var dv = s.substr(9,2);
        var d1 = 0;

        for (i = 0; i < 9; i++){
            d1 += c.charAt(i)*(10-i);
        }
        if (d1 == 0){
            return false;
        }
        d1 = 11 - (d1 % 11);
        if (d1 > 9) d1 = 0;
        if (dv.charAt(0) != d1){
            return false;
        }

        d1 *= 2;
        for (i = 0; i < 9; i++){
            d1 += c.charAt(i)*(11-i);
        }
        d1 = 11 - (d1 % 11);
        if (d1 > 9) d1 = 0;
        if (dv.charAt(1) != d1){
            return false;
        }
    },
    valida_cnpj: function(cnpj){
        cnpj = cnpj.replace(/[^\d]+/g,'');

        if (cnpj.length != 14 && cnpj != ""){
            return false;
        }

            // Valida DVs
        var i;
        var tamanho = cnpj.length - 2
        var numeros = cnpj.substring(0,tamanho);
        var digitos = cnpj.substring(tamanho);
        var soma = 0;
        var pos = tamanho - 7;
        for (i = tamanho; i >= 1; i--) {
          soma += numeros.charAt(tamanho - i) * pos--;
          if (pos < 2){
                pos = 9;
          }
        }
        var resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
        if (resultado != digitos.charAt(0)){
            return false;
        }

        tamanho = tamanho + 1;
        numeros = cnpj.substring(0,tamanho);
        soma = 0;
        pos = tamanho - 7;
        for (i = tamanho; i >= 1; i--) {
          soma += numeros.charAt(tamanho - i) * pos--;
          if (pos < 2){
                pos = 9;
          }
        }
        resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
        if (resultado != digitos.charAt(1)){
              return false;
        }

        return true;
    },
    get_cpf: function(){
        return cpf;
    },
    set_cpf: function(cpf_nfse){
        cpf = cpf_nfse;
    },
    get_cnpj: function(){
        return cnpj;
    },
    set_cnpj: function(cpf_nfse){
        cnpj = cpf_nfse;
    },
    partner_cpf: function(){
        var self = this;
        var partner_id = this.pos.get_order().get_client();
        if (partner_id && option_cpf == false){
            var v = partner_id.cnpj_cpf;
            if (!v){
                self.set_cpf("");
                self.set_cnpj("");
                return false;
            }
            v = v.replace(/[^\d]+/g,'');
            if (v.length == 11){
                self.set_cpf(v);
                return v;
            }
            else if(v.length == 14){
                self.set_cnpj(v);
                return v;
            }
        }
        else{
            return false;
        }
    },
    renderElement: function() {
        var self = this;
        this._super();
        option_cpf = false;
        this.$('.pay2').click(function(){
            var partner_id = self.partner_cpf();
            var order = self.pos.get_order();
            var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                return line.has_valid_product_lot();
            });
            for (var i=0; i < order.orderlines.models.length; i++){
                   if (order.orderlines.models[i].quantity == 0 || (order.orderlines.models[i].quantity >= 1 && order.orderlines.models[i].price == 0) || order.orderlines.models[i].discount == 100 || order.get_total_with_tax() == 0){
                        self.gui.show_popup('error',_t("Products with quantity or price equal to 0 can't be sold."));
                        return false;
                   }
            }
            if (option_cpf == false){
                if (partner_id || cpf || cnpj){
                    if (cpf != "" && cpf != undefined){
                        var v = self.get_cpf() || "";
                        v = v.replace(/(\d{3})(\d)/,"$1.$2");
                        v = v.replace(/(\d{3})(\d)/,"$1.$2");
                        v = v.replace(/(\d{3})(\d{1,2})$/,"$1-$2");

                        self.gui.show_popup('textinput',{
                            title: _t('CPF na Nota Paulista'),
                            'value': v,
                            confirm: function(value) {
                                var valida = self.valida_cpf(value);
                                if (valida == false){
                                    self.gui.show_popup('error',_t('CPF inválido!'));
                                    self.renderElement();
                                }
                                else{
                                    option_cpf = true;
                                    value = value.replace(/[^\d]+/g,'');
                                    self.set_cpf(value);
                                    self.renderElement();
                                    self.gui.show_screen('payment');
                                }
                            },
                        });
                    }
                    else if (cnpj != "" && cnpj != undefined){
                        var v = self.get_cnpj() || "";
                        v = v.replace(/^(\d{2})(\d)/,"$1.$2");             //Coloca ponto entre o segundo e o terceiro dígitos
                        v = v.replace(/^(\d{2})\.(\d{3})(\d)/,"$1.$2.$3"); //Coloca ponto entre o quinto e o sexto dígitos
                        v = v.replace(/\.(\d{3})(\d)/,".$1/$2");           //Coloca uma barra entre o oitavo e o nono dígitos
                        v = v.replace(/(\d{4})(\d)/,"$1-$2");      //Coloca um hífen depois do bloco de quatro dígitos
                        self.gui.show_popup('textinput',{
                            title: _t('CNPJ do cliente'),
                            'value': v,
                            confirm: function(value) {
                                var valida = self.valida_cnpj(value);
                                if (valida == false){
                                    self.gui.show_popup('error',_t('CNPJ inválido!'));
                                    self.renderElement();
                                }
                                else{
                                    option_cpf = true;
                                    value = value.replace(/[^\d]+/g,'');
                                    self.set_cnpj(value);
                                    self.renderElement();
                                    self.gui.show_screen('payment');
                                }
                            },
                        });
                    }

                }else{
                    self.gui.show_popup('textinput',{
                        title: _t('CPF/CNPJ na Nota Paulista'),
                        'value': "",
                        confirm: function(value) {
                            if (isNaN(value) == true){
                                var valida = false;
                            }
                            else{
                                value = value.replace(/[^\d]+/g,'');
                            }

                            if (value.length == 11 && valida != false){
                                var valida = self.valida_cpf(value);
                            }
                            else if(value.length == 14 && valida != false){
                                var valida = self.valida_cnpj(value);
                            }
                            else{
                                valida = false;
                            }

                            if (valida == false && value != ""){
                                self.gui.show_popup('error',_t('CPF/CNPJ inválido!'));
                                self.renderElement();
                            }
                            else{
                                option_cpf = true;
                                value = value.replace(/[^\d]+/g,'');
                                if (value.length == 14){
                                    self.set_cnpj(value);
                                }
                                else{
                                    self.set_cpf(value);
                                }
                                self.renderElement();
                                self.gui.show_screen('payment');
                            }
                        },
                    });
                }
            }
            if (option_cpf === true){
                if(!has_valid_product_lot){
                    self.gui.show_popup('confirm',{
                        'title': _t('Empty Serial/Lot Number'),
                        'body':  _t('One or more product(s) required serial/lot number.'),
                        confirm: function(){
                            self.gui.show_screen('payment');
                        },
                    });
                }else{
                    self.gui.show_screen('payment');
                }
            }
        });
        this.$('.set-customer').click(function(){
            self.gui.show_screen('clientlist');
        });
    }
});

var _super = models.Order;
models.Order = models.Order.extend({
    get_cpf: function(){
        return cpf;
    },
    set_cpf: function(cpf_nfse){
        this.cpf = cpf;
    },
    get_cnpj: function(){
        return cnpj;
    },
    set_cnpj: function(cpf_nfse){
        this.cnpj = cnpj;
    },

    export_for_printing: function(){
        var self = this;
        var json = _super.prototype.export_for_printing.apply(this,arguments);

        if (cpf != "" && cpf != undefined){
            var v = cpf;
            if (v != undefined || v != false){
                v = v.replace(/(\d{3})(\d)/,"$1.$2");
                v = v.replace(/(\d{3})(\d)/,"$1.$2");
                v = v.replace(/(\d{3})(\d{1,2})$/,"$1-$2");
            }
            else{
                v = "";
            }
        }
        else if (cnpj != "" && cnpj != undefined){
            var v = cnpj;
            if (v != undefined || v != false){
                v = v.replace(/^(\d{2})(\d)/,"$1.$2");             //Coloca ponto entre o segundo e o terceiro dígitos
                v = v.replace(/^(\d{2})\.(\d{3})(\d)/,"$1.$2.$3"); //Coloca ponto entre o quinto e o sexto dígitos
                v = v.replace(/\.(\d{3})(\d)/,".$1/$2");           //Coloca uma barra entre o oitavo e o nono dígitos
                v = v.replace(/(\d{4})(\d)/,"$1-$2");      //Coloca um hífen depois do bloco de quatro dígitos

            }
            else{
                v = "";
            }
        }

        json.pos_ext = {
                cpf_nfse: v,
                //subtotal: this.get_subtotal() + this.discount_total,
        };

        cpf = "";
        cnpj = "";

        return json;
    },

    export_as_JSON: function(){
        var self = this;
        var json = _super.prototype.export_as_JSON.apply(this,arguments);
        var order = self.pos.get_order();
        var paymentlines = []
        if (order != undefined || order != null){
        order.paymentlines.each(_.bind( function(item) {
            return paymentlines.push([0, 0, order.paymentlines.models]);
        }, this));
        }
        if (order != undefined || order != null){
            json.card_banner = order.card_banner;
            json.paymentlines = paymentlines;
            json.number_card = order.number_card;
            json.number_installment = order.number_installment;
            json.return_tef = order.return_tef;
            json.return_tef_client = order.return_tef_client;
            json.return_tef_cancel = order.return_tef_cancel;
            json.return_tef_estab = order.return_tef_estab;
            json.authorization_number = order.authorization_number;
        }
        json.authorizer_user_id = authorizer_user_id;
        json.cpf_nfse = cpf;
        if (this.quotation == true){
            json.quotation = true;
        }
        return json;
    },

    init_from_JSON: function(json){
        var self = this;
        _super.prototype.init_from_JSON.apply(this,arguments);
        cpf = json.cpf_nfse;
    },
    finalize: function(){
        var self = this;

        var user = this.pos.user || this.pos.cashier;
        self.pos.set_cashier(user);

        var sales = new SalespersonButton();
        option = false;
        finalize = true;
        sales.renderElement();

        var el = document.getElementById("salesperson-button");
        el.innerHTML = '<i class="fa fa-check"></i> Vendedor';



        cpf = "";

        _super.prototype.finalize.apply(this,arguments);
    },
});

//screens.define_action_button({
//    'name': 'pos_ext',
//    'widget': CpfButton,
//});

screens.define_action_button({
    'name': 'pos_ext',
    'widget': SalespersonButton,
});

screens.PaymentScreenWidget.include({
    set_installment: function(installment){
        this.installment = installment;
        if (this.installment_ok != "ok"){
            this.installment_verify = installment
        }
    },

    confirmacao: function(value) {

          var numTrans = value;

          var ws = new WebSocket(host);
            ws.onopen = function() {
                var transacao = this;

                if (numTrans.value != "")  {
                  transacao.numeroTransacao = numTrans.value;
                }

                transacao.operacao = 6;
                ws.send(JSON.stringify(transacao));
            };

          ws.onmessage = function(evt) {
            var msg = evt.data;
            var obj = JSON.parse(msg);

            if (obj.retorno == 0 || obj.retorno == 13) {
                alert("Transacao confirmada!");
            } else {
                alert("Nao foi possivel confirmar a transacao. retorno: "
                      + obj.retorno + ", erro: " + obj.codigoErro);
            }

            //resetCupom();

          };
      },

    solicitacao: function(amount, operation_code, index){
        var self = this;
        var numTrans = "";
        var operacao = operation_code;
        var valor = amount.toFixed(2).replace('.','');
        var parcelas = this.get_installment().replace('x','');
        var dataTransacao = "";
        var nsuCTF = "";

        var cupomReduzido = {};
        var cupomEstab = {};
        var cupomCliente = {};

        var order = this.pos.get_order();

        var opt = {};

        this.operacao = operacao
        this.valor = valor
        this.numTrans = numTrans
        this.parcelas = parcelas
        this.dataTransacao = dataTransacao
        this.nsuCTF = nsuCTF
        this.cupomReduzido = cupomReduzido
        this.cupomEstab = cupomEstab
        this.cupomCliente = cupomCliente

        var ws = new WebSocket('ws://localhost:2500');
            ws.a = this;

            ws.onopen = function() {
                var transacao = {};

                transacao.operacao = this.a.operacao;
                transacao.valorTransacao = this.a.valor;

                if (this.numTrans != "")  {
                   transacao.numeroTransacao = this.numTrans;
                }

                if (this.parcelas != "") {
                    transacao.numeroParcelas = this.parcelas;
                }

                if (this.dataTransacao != "") {
                    transacao.dataTransacao = this.dataTransacao;
                }

                if (this.nsuCTF != "") {
                    transacao.nsuCTF = this.nsuCTF;
                }

                ws.send(JSON.stringify(transacao));

            };

            ws.onmessage = function (evt) {
                var posOrderModel = new Model('pos.order');
                var received_msg = evt.data;
                var obj = JSON.parse(received_msg);
                var msg = "";

                //alert(received_msg);

                var card_banner = obj.bandeira
                var number_card = obj.cartao


                if (obj.display != null) {
                  var display = "";
                  for (var i=0; i < obj.display.length; i++){
                   display += obj.display[i].mensagem;
                  }

                  msg += display;
                }



                if (obj.retorno == 0) {
                    if (obj.codigoAprovacao != "") {
                      msg += "\n Codigo Aprovacao: " +  obj.codigoAprovacao;
                    }

                    if (obj.nsuCTF != "") {
                      msg += "\n Nsu CTF: " + obj.nsuCTF;
                    }

                    if (obj.bandeira != "") {
                      msg += "\n Bandeira: " + obj.bandeira;
                    }

                    if (obj.cartao != "") {
                      msg += "\n Cartao: " + obj.cartao;
                    }

                    if (obj.redeAdquirente != "") {
                      msg += "\n Adquirente: " + obj.redeAdquirente;
                    }
                    operacao = "";
                    valor = "";


                    if (obj.cupomReduzido != null) {
                      var linhas = "";
                      for (var i=0; i < obj.cupomReduzido.length; i++){
                       linhas += obj.cupomReduzido[i].linha + "</br>";
                      }
                        //alert(linhas);
                        cupomReduzido.innerHTML = linhas;
                    }


                    if (obj.cupomEstabelecimento != null) {
                      var linhas = "";
                      for (var i=0; i < obj.cupomEstabelecimento.length; i++){
                       linhas += obj.cupomEstabelecimento[i].linha + "</br>";
                      }
                        //alert(linhas);
                        cupomEstab.innerHTML = linhas;
                    }

                    if (obj.cupomCliente != null) {
                      var linhas = "";
                      for (var i=0; i < obj.cupomCliente.length; i++){
                       linhas += obj.cupomCliente[i].linha + "</br>";
                      }
                        //alert(linhas);
                        cupomCliente.innerHTML = linhas;
                    }

                    // Print Receipt Cupom
                    //self.validate_order_ext_cupon();

                    // Print Receipt TEF
                    posOrderModel.call('print_receipt_tef',[cupomCliente.innerHTML,cupomEstab.innerHTML,order.pos.config]).then(function(valida){
                    if (valida['result'] == false){
                        self.gui.show_popup('error',_t('No printer connection!'));
                    }
                    //else{}

                    })

                    self.confirmacao(obj.codigoAprovacao);

                    order.paymentlines.models[index].paid = 'ok';
                    order.paymentlines.models[index].number_card = number_card;
                    order.paymentlines.models[index].card_banner = card_banner;
                    order.paymentlines.models[index].authorization_number = obj.codigoAprovacao;
                    order.paymentlines.models[index].number_installment = parcelas;
                    order.paymentlines.models[index].return_tef_reduced = cupomReduzido.innerHTML;
                    order.paymentlines.models[index].return_tef_client = cupomCliente.innerHTML;
                    order.paymentlines.models[index].return_tef_establishment = cupomEstab.innerHTML;
                    order.number_installment = parcelas;
                    order.card_banner = card_banner;
                    order.number_card = number_card;
                    order.return_tef = cupomReduzido.innerHTML;
                    order.return_tef_client = cupomCliente.innerHTML;
                    order.return_tef_estab = cupomEstab.innerHTML;
                    order.authorization_number = obj.codigoAprovacao;
                    opt['number_installment'] = parcelas;
                    opt['card_banner'] = card_banner;
                    opt['number_card'] = number_card;
                    opt['authorization_number'] = obj.codigoAprovacao;
                    opt['return_tef'] = cupomReduzido.innerHTML;
                    opt['return_tef_client'] = cupomCliente.innerHTML;
                    opt['return_tef_estab'] = cupomEstab.innerHTML;
                    opt['ok'] = true;
                    opt['msg'] = msg;
                    //self.pos.push_order(order, opt);

                    //alert(msg);
                    //this.a.gui.show_screen('receipt');

                } else {
                  msg += "\n Retorno: " + obj.retorno;
                  msg += "\n Codigo de Erro: " + obj.codigoErro;
                  opt['msg'] = msg;
                  opt['ok'] = false;
                  alert(msg);
                }


                 //alert(msg);
                 //ws.close();
                };

          ws.onclose = function() {
             //alert("Connection is closed...");
          };

          ws.onerror = function () {
              alert("Erro - CTF Client não encontrado.");
          }

          option_cpf = false;
          },

    get_installment: function(){
        var installment = this.installment;
        if (this.installment != undefined){
            for (var f = 0; f < this.pos.attributes.selectedOrder.paymentlines.models.length; f++ ) {
                if (this.pos.attributes.selectedOrder.paymentlines.models[f].selected === true && this.pos.attributes.selectedOrder.paymentlines.models[f].installment != undefined){
                    installment =  this.pos.attributes.selectedOrder.paymentlines.models[f].installment;
                }
            }
        }
        if (this.installment == undefined){
            installment = 1;
        }
        this.installment_ok = ""
        //if (this.installment === this.installment_verify){
        installment = installment + "x";
        //}
        //else{
         //   installment = this.installment_verify + "x"
        //}

        return installment;
    },
    renderElement: function() {
        var self = this;
        this._super();

        this.$('.back').click(function(){
            self.click_back();
            option_cpf = false;
        });
    },

    validate_order_ext: function(force_validation) {
        if (this.order_is_valid(force_validation)) {
            this.finalize_validation_ext();
        }
    },

    validate_order_ext_cupon: function(force_validation) {
            if (this.order_is_valid(force_validation)) {
                this.finalize_validation_ext_cupon();
            }
        },

    finalize_validation_ext_cupon: function() {
            var self = this;
            var order = this.pos.get_order();
            if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) {

                    this.pos.proxy.open_cashbox();
            }

            order.initialize_validation_date();

            if (order.is_to_invoice()) {
                var invoiced = this.pos.push_and_invoice_order(order);
                this.invoicing = true;

                invoiced.fail(function(error){
                    self.invoicing = false;
                    if (error.message === 'Missing Customer') {
                        self.gui.show_popup('confirm',{
                            'title': _t('Please select the Customer'),
                            'body': _t('You need to select the customer before you can invoice an order.'),
                            confirm: function(){
                                self.gui.show_screen('clientlist');
                            },
                        });
                    } else if (error.code < 0) {        // XmlHttpRequest Errors
                        self.gui.show_popup('error',{
                            'title': _t('The order could not be sent'),
                            'body': _t('Check your internet connection and try again.'),
                        });
                    } else if (error.code === 200) {    // OpenERP Server Errors
                        self.gui.show_popup('error-traceback',{
                            'title': error.data.message || _t("Server Error"),
                            'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
                        });
                    } else {                            // ???
                        self.gui.show_popup('error',{
                            'title': _t("Unknown Error"),
                            'body':  _t("The order could not be sent to the server due to an unknown error"),
                        });
                    }
                });

                invoiced.done(function(){
                    self.invoicing = false;
                    //self.gui.show_screen('receipt');
                });
            } else {
                this.pos.push_order(order);
    //            this.gui.show_screen('receipt');
                }

        },

    finalize_validation_ext: function() {
        var self = this;
        var order = this.pos.get_order();
        order.quotation = true;
        if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) {

                this.pos.proxy.open_cashbox();
        }

        order.initialize_validation_date();

        if (order.is_to_invoice()) {
            var invoiced = this.pos.push_and_invoice_order(order);
            this.invoicing = true;

            invoiced.fail(function(error){
                self.invoicing = false;
                if (error.message === 'Missing Customer') {
                    self.gui.show_popup('confirm',{
                        'title': _t('Please select the Customer'),
                        'body': _t('You need to select the customer before you can invoice an order.'),
                        confirm: function(){
                            self.gui.show_screen('clientlist');
                        },
                    });
                } else if (error.code < 0) {        // XmlHttpRequest Errors
                    self.gui.show_popup('error',{
                        'title': _t('The order could not be sent'),
                        'body': _t('Check your internet connection and try again.'),
                    });
                } else if (error.code === 200) {    // OpenERP Server Errors
                    self.gui.show_popup('error-traceback',{
                        'title': error.data.message || _t("Server Error"),
                        'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
                    });
                } else {                            // ???
                    self.gui.show_popup('error',{
                        'title': _t("Unknown Error"),
                        'body':  _t("The order could not be sent to the server due to an unknown error"),
                    });
                }
            });

            invoiced.done(function(){
                self.invoicing = false;
                //self.gui.show_screen('receipt');
            });
        } else {
            this.pos.push_order(order);
//            this.gui.show_screen('receipt');
            }

    },
    export_for_printing: function(){
        var self = this;
        var json = _super.prototype.export_for_printing.apply(this,arguments);

        if (cpf != "" && cpf != undefined){
            var v = cpf;
            if (v != undefined || v != false){
                v = v.replace(/(\d{3})(\d)/,"$1.$2");
                v = v.replace(/(\d{3})(\d)/,"$1.$2");
                v = v.replace(/(\d{3})(\d{1,2})$/,"$1-$2");
            }
            else{
                v = "";
            }
        }
        else if (cnpj != "" && cnpj != undefined){
            var v = cnpj;
            if (v != undefined || v != false){
                v = v.replace( /^(\d{2})(\d)/ , "$1.$2"); //Coloca ponto entre o segundo e o terceiro dígitos
                v = v.replace( /^(\d{2})\.(\d{3})(\d)/ , "$1.$2.$3"); //Coloca ponto entre o quinto e o sexto dígitos
                v = v.replace( /\.(\d{3})(\d)/ , ".$1/$2"); //Coloca uma barra entre o oitavo e o nono dígitos
                v = v.replace( /(\d{4})(\d)/ , "$1-$2");
            }
            else{
                v = "";
            }
        }

        json.pos_ext = {
                cpf_nfse: v,
        };

        cpf = "";
        cnpj = "";

        return json;
    },


});


var PaymentMethodButton = screens.PaymentScreenWidget.extend({
    template:      'PaymentScreenWidget',
    back_screen:   'product',
    init: function(parent, options){
    var self = this;
       this._super(parent, options);
        //Overide methods
       this.keyboard_keydown_handler = function(event){

           if (event.keyCode === 8 || event.keyCode === 46) { // Backspace and Delete
              // event.preventDefault();
              self.keyboard_handler(event);
           }
       };

       this.keyboard_handler = function(event){
           var key = '';

//          if (event.type === "keypress") {
//               if (event.keyCode === 13) { // Enter
//                   self.validate_order();
////                    continue;
//               } else
               if (event.keyCode === 46) { // Delete
                   key = 'CLEAR';
               } else if (event.keyCode === 8) { // Backspace
                   key = 'BACKSPACE';
               }
               if ( event.keyCode === 190 || // Dot
                           event.keyCode === 110 ||  // Decimal point (numpad)
                           event.keyCode === 44 ||  // Comma
                           event.keyCode === 46 ) {  // Numpad dot
                   key = self.decimal_point;
               } else if (event.keyCode >= 48 && event.keyCode <= 57) { // Numbers
                   key = '' + (event.keyCode - 48);
               } else if (event.keyCode === 45) { // Minus
                   key = '-';
               } else if (event.keyCode === 43) { // Plus
                   key = '+';
               }else{
                return ;
               }

           if (self.old_order.selected_paymentline.paid == 'ok'){
               self.pos.gui.show_popup('error',{
                        'title': _t("Aviso!"),
                        'body': _t("Linha não pode ser alterada, Pagamento já efetuado!"),
                    });
           }
           else{
            self.payment_input(key);
            }
           /*event.preventDefault();
           if (event.type === "keypress") {
             return ;
            }*/
       };

    },
    initialize: function(session, attributes) {
        this.installment = null;
    },
    renderElement: function() {
        var self = this;
        this._super();

        this.render_paymentlines();

        this.$('.back').click(function(){
            self.click_back();
        });

        this.$('.next_ext').click(function(){

            var order = self.pos.get_order();

            if (!order.selected_paymentline){
                order.pos.gui.show_popup('error',{
                        'title': _t("Aviso!"),
                        'body': _t("Por favor Escolha uma Forma de Pagamento!"),
                    });
            }
            else{
                if (order.selected_paymentline.amount > 0){
                    var paid_value = 0
                    var test_paid = 0
                    for ( var i = 0; i < order.paymentlines.models.length; i++ ) {
                        paid_value += order.paymentlines.models[i].amount
                        if (order.paymentlines.models[i].paid != 'ok'){
                            test_paid = 1
                        }
                        }
                    if (test_paid == 0){
                        self.validate_order_ext_cupon();
                        self.set_installment(1);
                        self.gui.show_screen('receipt');
                        return;
                    }
                    if (parseFloat(paid_value.toFixed(2)) >= (parseFloat(order.get_total_with_tax()).toFixed(2))){
                        option_pay['g'] = true;
                        //self.validate_order_ext_cupon();

                        for ( var i = 0; i < order.paymentlines.models.length; i++ ) {
                            if (order.paymentlines.models[i].selected){
                            var index = i

                            if (order.paymentlines.models[i].paid != 'ok'){
                                if (order.paymentlines.models[i].cashregister.journal.is_contingency == true){
                                    if (order.paymentlines.models[i].paid != 'ok'){
                                        self.gui.show_popup('textinput',{
                                        'title': _t('Authorization Number'),
                                        'confirm': function(value) {

                                            if (!value) {
                                                this.gui.show_popup('error',_t('Authorization Number not found!'));
                                            }
                                            else {
                                                var opt = [];
                                                var parcelas = self.get_installment();
                                                if (parcelas){
                                                    parcelas = parcelas.replace('x','');
                                                }
                                                order['number_installment'] = parcelas;
                                                order['authorization_number'] = value;
                                                //self.pos.push_order(order);
    //                                            self.validate_order_ext_cupon();
                                                self.set_installment(1);
                                                order.paymentlines.models[index]['paid'] = 'ok';
                                                order.paymentlines.models[index]['authorization_number'] = value;
                                                order.paymentlines.models[index]['number_installment'] = parcelas;
                                                this.gui.show_popup('confirm',_t('Pagamento Efetuado'));
    //                                            self.gui.show_screen('receipt');
                                        }

                                    },
                                    })};

                                    }
                                else if (order.paymentlines.models[i].cashregister.journal.is_tef == true){
                                        if (order.paymentlines.models[i].paid != 'ok'){
                                            if (order.paymentlines.models[i].cashregister.journal.operation_code){
                                                self.solicitacao(order.paymentlines.models[i].amount, order.paymentlines.models[i].cashregister.journal.operation_code, i);
                                                self.set_installment(1);
                                                //order.paymentlines.models[i].paid = 'ok'
                                                break
                                                }
                                                //self.validate_order_ext_cupon();
                                                //self.gui.show_screen('receipt');
                                            else{
                                                order.pos.gui.show_popup('error',{
                                                    'title': _t("Notice!"),
                                                    'body': _t("No operation code registered for this journal! Please configure a operation code."),
                                                });
                                            }
                                            }
                                        else{
                                            continue
                                        }
                                }
                                else{
                                    if (order.paymentlines.models[i].paid != 'ok'){
                                        order.paymentlines.models[i].paid = 'ok'

                                        order.pos.gui.show_popup('confirm',_t('Pagamento Efetuado'));
                                    }
                                    else{
                                        order.pos.gui.show_popup('error',{
                                            'title': _t("Notice!"),
                                            'body': _t("Payment line already paid!"),
                                                    });
                                        return;
                                    //self.pos.push_order(order);
//                                    self.validate_order_ext_cupon();
//                                    self.set_installment(1);
//                                    self.gui.show_screen('receipt');
                                    }
                                }
                            }
                            else{
                                order.pos.gui.show_popup('error',{
                                    'title': _t("Notice!"),
                                    'body': _t("Payment line already paid!"),
                                                    });
                                break;
                            }
                            }

                            }
                        }
                    else{
                        order.pos.gui.show_popup('error',{
                                'title': _t("Aviso!"),
                                'body': _t("Por favor inserir valor pago correto!"),
                            });
                    }
                }
                else{
                    if (order.selected_orderline.price > 0 && order.selected_orderline.quantity < 0){
                        self.validate_order_ext('confirm');
                        self.set_installment(1);
                    }
                    else{
                        order.pos.gui.show_popup('error',{
                                'title': _t("Aviso!"),
                                'body': _t("Por favor inserir valor pago correto!"),
                            });
                    }
                }

        }
        });

        this.$('.next2').click(function(options){

            var order = self.pos.get_order();

            if (!order.selected_paymentline){
                order.pos.gui.show_popup('error',{
                        'title': _t("Aviso!"),
                        'body': _t("Por favor Escolha uma Forma de Pagamento!"),
                    });
            }
            else{
                if (order.selected_paymentline.amount > 0){
                    var paid_value = 0
                    var test_paid = 0
                    for ( var i = 0; i < order.paymentlines.models.length; i++ ) {
                        paid_value += order.paymentlines.models[i].amount
                        if (order.paymentlines.models[i].paid != 'ok'){
                            test_paid = 1
                        }
                        }
                    if (test_paid == 0){
                        self.validate_order_ext();
                        self.set_installment(1);
                        self.gui.show_screen('receipt');
                        return;
                    }
                    if (parseFloat(paid_value.toFixed(2)) >= (parseFloat(order.get_total_with_tax()).toFixed(2))){
                        option_pay['g'] = true;
                        //self.validate_order_ext_cupon();

                        for ( var i = 0; i < order.paymentlines.models.length; i++ ) {
                            if (order.paymentlines.models[i].selected){
                            var index = i

                            if (order.paymentlines.models[i].paid != 'ok'){
                                if (order.paymentlines.models[i].cashregister.journal.is_contingency == true){
                                    if (order.paymentlines.models[i].paid != 'ok'){
                                        self.gui.show_popup('textinput',{
                                        'title': _t('Authorization Number'),
                                        'confirm': function(value) {

                                            if (!value) {
                                                this.gui.show_popup('error',_t('Authorization Number not found!'));
                                            }
                                            else {
                                                var opt = [];
                                                var parcelas = self.get_installment();
                                                if (parcelas){
                                                    parcelas = parcelas.replace('x','');
                                                }
                                                order['number_installment'] = parcelas;
                                                order['authorization_number'] = value;
                                                //self.pos.push_order(order);
    //                                            self.validate_order_ext_cupon();
                                                self.set_installment(1);
                                                order.paymentlines.models[index]['paid'] = 'ok';
                                                order.paymentlines.models[index]['authorization_number'] = value;
                                                order.paymentlines.models[index]['number_installment'] = parcelas;
                                                this.gui.show_popup('confirm',_t('Pagamento Efetuado'));
    //                                            self.gui.show_screen('receipt');
                                        }

                                    },
                                    })};

                                    }
                                else if (order.paymentlines.models[i].cashregister.journal.is_tef == true){
                                        if (order.paymentlines.models[i].paid != 'ok'){
                                            if (order.paymentlines.models[i].cashregister.journal.operation_code){
                                                self.solicitacao(order.paymentlines.models[i].amount, order.paymentlines.models[i].cashregister.journal.operation_code, i);
                                                self.set_installment(1);
                                                //order.paymentlines.models[i].paid = 'ok'
                                                break
                                                }
                                                //self.validate_order_ext_cupon();
                                                //self.gui.show_screen('receipt');
                                            else{
                                                order.pos.gui.show_popup('error',{
                                                    'title': _t("Notice!"),
                                                    'body': _t("No operation code registered for this journal! Please configure a operation code."),
                                                });
                                            }
                                            }
                                        else{
                                            continue
                                        }
                                }
                                else{
                                    if (order.paymentlines.models[i].paid != 'ok'){
                                        order.paymentlines.models[i].paid = 'ok'

                                        order.pos.gui.show_popup('confirm',_t('Pagamento Efetuado'));
                                    }
                                    else{
                                        order.pos.gui.show_popup('error',{
                                            'title': _t("Notice!"),
                                            'body': _t("Payment line already paid!"),
                                                    });
                                        return;
                                    //self.pos.push_order(order);
//                                    self.validate_order_ext_cupon();
//                                    self.set_installment(1);
//                                    self.gui.show_screen('receipt');
                                    }
                                }
                            }
                            else{
                                order.pos.gui.show_popup('error',{
                                    'title': _t("Notice!"),
                                    'body': _t("Payment line already paid!"),
                                                    });
                                break;
                            }
                            }

                            }
                        }
                    else{
                        order.pos.gui.show_popup('error',{
                                'title': _t("Aviso!"),
                                'body': _t("Por favor inserir valor pago correto!"),
                            });
                    }
                }
                else{
                    if (order.selected_orderline.price > 0 && order.selected_orderline.quantity < 0){
                        self.validate_order_ext('confirm');
                        self.set_installment(1);
                    }
                    else{
                        order.pos.gui.show_popup('error',{
                                'title': _t("Aviso!"),
                                'body': _t("Por favor inserir valor pago correto!"),
                            });
                    }
                }

        }
        });

        this.$('.js_set_customer').click(function(){
            self.click_set_customer();
        });

        this.$('.js_tip').click(function(){
            self.click_tip();
        });
        this.$('.js_invoice').click(function(){
            self.click_invoice();
        });

        this.$('.js_cashdrawer').click(function(){
            self.pos.proxy.open_cashbox();
        });

    },
    click_paymentmethods: function(id) {
        var cashregister = null;
        var user = this.pos.get_cashier();
        var ret = new $.Deferred();
        var self = this;
        var config = this.pos.config;
        var wallet_pwd = (config.is_password_wallet) ? config.password_wallet : config.is_password_wallet;
        var partner = this.pos.attributes.selectedClient;
        self.set_installment(option_pay['installment']);
        self.get_installment();
        for ( var i = 0; i < this.pos.cashregisters.length; i++ ) {
            if (this.pos.cashregisters[i].journal_id[0] === id){
                cashregister = this.pos.cashregisters[i];
                break;
            }
        }
        option_pay['id'] = id;
        if (option_pay['g'] === true && cashregister.journal.pay_installments != false){
            var list = this.gui.select_installments(cashregister.journal.installments);
            this.gui.show_popup_ext('selection',{
                'title': _t('Select Installments'),
                list: list,
                confirm: function(i){
                    option_pay['g'] = false;
                    option_pay['installment'] = i;
                    self.set_installment(i);
                    self.get_installment();
                    self.click_paymentmethods(option_pay['id']);
                    self.installment_ok = "ok";
                    for (var f = 0; f <  self.gui.pos.attributes.selectedOrder.paymentlines.models.length; f++ ) {
                        if (self.gui.pos.attributes.selectedOrder.paymentlines.models[f].selected === true){
                            self.gui.pos.attributes.selectedOrder.paymentlines.models[f].installment_ok = "ok";
                            self.gui.pos.attributes.selectedOrder.paymentlines.models[f].installment = i;

                            //self.gui.pos.attributes.selectedOrder.paymentlines.models[f].get_installment();
                        }
                    }

                      //  };

                },
                cancel:  function(){ ret.reject(); },
            });
        }
        else{
            option_pay['g'] = false;
        }

        if (option_pay['g'] !== true){
            if (partner && partner.trust !== 'bad' && partner.wallet_partner){
                option_pay['g'] = true
                return this._super(id);
            }

            option_pay['type'] = 'payment_method'
            if (partner && option_pay['value'] !== true){
                if (partner.wallet_partner == false && cashregister.journal.payment_wallet === true){
                    this.pos.gui.show_popup('error',{
                        'title': _t("Customer not allowed!"),
                        'body': _t("Customer doesn't has wallet payment authorization."),
                    });
                }
                else{
                    if ( cashregister.journal_id[0] === id && cashregister.journal.payment_wallet === true){
                        this.pos.gui.show_popup("confirm", {
                            'title': _t("Bloqueado"),
                            'body':  _t("Autorizar crédito para cliente com saldo devedor."),
                            confirm: function(){
                                this.gui.ask_password_ext(wallet_pwd).then(function(){
                                    return ret.resolve();
                                });
                            },
                        });
                    }
                    else {
                        option_pay['g'] = true
                        this._super(id);
                    }
                }
            }
            else if (!partner && cashregister.journal.payment_wallet == true){
                this.pos.gui.show_popup('error',{
                    'title': _t("Customer not allowed!"),
                    'body': _t("Customer doesn't has wallet payment authorization."),
                });
            }
            else{
                option_pay['g'] = true
                this._super(id);
            }
            }
        },

    click_delete_paymentline: function(cid){
        var lines = this.pos.get_order().get_paymentlines();
        var self  = this;
        option_pay['value'] = false;
        for ( var i = 0; i < lines.length; i++ ) {
            if (lines[i].cid === cid) {
                 if (lines[i].paid == 'ok'){
                        self.pos.gui.show_popup('error',{
                        'title': _t("Aviso!"),
                        'body': _t("Linha não pode ser deletada, Pagamento já efetuado!"),
                    });
                 }
                 else{
                     this.pos.get_order().remove_paymentline(lines[i]);
                     this.reset_input();
                     this.render_paymentlines();
                     return;
                 }
            }
        }
    },

    render_paymentlines: function() {
        var self  = this;
        var order = this.pos.get_order();
        option_pay['value'] = false
        if (!order) {
            return;
        }

        var lines = order.get_paymentlines();
        var due   = order.get_due();
        var extradue = 0;
        if (due && lines.length  && due !== order.get_due(lines[lines.length-1])) {
            extradue = due;
        }


        this.$('.paymentlines-container').empty();
        var lines = $(QWeb.render('PaymentScreen-Paymentlines', {
            widget: this,
            order: order,
            paymentlines: lines,
            extradue: extradue,
        }));

        lines.on('click','.delete-button',function(){
            option_pay['g'] = true;
            self.set_installment(1);
            self.click_delete_paymentline($(this).data('cid'));
        });

        lines.on('click','.paymentline',function(){
            self.click_paymentline($(this).data('cid'));
        });
        if (this.old_order.selected_paymentline){
            if (this.old_order.selected_paymentline.cashregister.journal.installments != false){
                if (this.old_order.selected_paymentline.installment != null){
                    this.installment = this.old_order.selected_paymentline.installment
                }
                this.old_order.selected_paymentline.installment = this.installment
            }
            else {
                this.installment = 1
                this.old_order.selected_paymentline.installment = 1
            }
        }
        lines.appendTo(this.$('.paymentlines-container'));
    },
    export_for_printing: function(){
        var self = this;
        var json = _super.prototype.export_for_printing.apply(this,arguments);

        var receipt_installment = self.get_installment();

        json.pos_ext = {
            receipt_installment: receipt_installment,
        };

        return json;
    },
    export_as_JSON: function(){
        var self = this;
        var json = _super.prototype.export_as_JSON.apply(this,arguments);
        var order = self.pos.get_order();
        if (order != undefined || order != null){
            json.number_installment = order.number_installment;
            json.card_banner = order.card_banner;
            json.number_card = order.number_card;
            json.return_tef = order.return_tef;
            json.return_tef_client = order.return_tef_client;
            json.return_tef_cancel = order.return_tef_cancel;
            json.return_tef_estab = order.return_tef_estab;
            json.authorization_number = order.authorization_number;
        }
        json.monthly_installment = self.get_installment();
        return json;
    },
    init_from_JSON: function(json){
        var self = this;
        _super.prototype.init_from_JSON.apply(this,arguments);
        self.set_installment(json.monthly_installment);
    },
});
gui.define_screen({name:'payment', 'widget': PaymentMethodButton});

gui.Gui.include({
        cpf_popup_ext: function(option_cpf){
            var self = this;
            this.show_popup('textinput',{
                title: _t('CPF na Nota Paulista'),
                'value': v,
                confirm: function(value) {
                option_cpf = true;
                var valida = self.valida_cpf(value);
                if (valida == false){
                    self.gui.show_popup('error',_t('CPF inválido!'));
                    this.$('.pay2').click(function(){
                        this._super;
                    });
                }
                else{
                    option_cpf = true;
                    value = value.replace(/[^\d]+/g,'');
                    self.set_cpf(value);
                    self.gui.show_screen('payment');
                }
                },
                });
        },

        show_popup_ext: function(name,options) {
        if (this.current_popup) {
            this.close_popup();
        }
        option_pay['g'] = true;
        this.current_popup = this.popup_instances[name];
        return this.current_popup.show(options);
        },

        ask_password_ext: function(password) {
            var self = this;
            var ret = new $.Deferred();
            var s = _super_NumpadWidget;

            if (password) {
                this.show_popup('password',{
                    'title': _t('Password ?'),
                    confirm: function(pw) {
                        if (pw !== password) {
                            if (option_pay['type'] == 'price'){
                                var newMode = event.currentTarget.attributes['data-mode'].value;
                                return this.state.changeMode(newMode);
                                option_pay['g'] = true;
                            }
                            else{
                                self.show_popup('error',_t('Incorrect Password'));
                                ret.reject();
                                option_pay['g'] = true;
                            }
                        } else {
                            option_pay['value'] = true
                            option_validate['value'] = true
                            if (option_pay['type'] === 'payment_method'){
                                self.current_screen.click_paymentmethods(option_pay['id'])
                            }
                            else if (option_pay['type'] === 'discount'){
                                self.screen_instances.products.numpad.clickAppendNewChar(option_pay['event'])
                            }
                            option_pay['g'] = true;
                            ret.resolve();
                        }
                    },
                });
            } else {
                this.pos.gui.show_popup('error',{
                    'title': _t("Password error!"),
                    'body': _t("A password is not configured for this type of authorization. Please call the Manager."),
                    });
            }
            return ret;
        },
    });

    chrome.Chrome.include({

        // show_error with the option of showing user-friendly errors
        // (without backtrace etc.)
        show_error: function(error) {
            if (error.message) {
                this.gui.show_popup('error',{
                    'title': "Aviso!",
                    'body':  error.message,
                });
            } else {
                this._super(error);
            }
        }
    });
});

