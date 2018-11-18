/*
* @Author: D.Jane
* @Email: jane.odoo.sp@gmail.com
*/
odoo.define('pos_speed_up.pos_model', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
    var Model = require('web.Model');

    var _super_pos = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            this.p_init();
            this.pricelist_modifier();

            var wait = this.get_model('res.users');
            if (wait) {
                var _super_loaded = wait.loaded;
                wait.loaded = function (self, users) {
                    var def = $.Deferred();
                    _super_loaded(self, users);

                    self.c_init().always(function () {
                        def.resolve();
                    });

                    return def;
                };
            }

            _super_pos.initialize.call(this, session, attributes);
        },
        get_model: function (_name) {
            var _index = this.models.map(function (e) {
                return e.model;
            }).indexOf(_name);
            if (_index > -1) {
                return this.models[_index]
            }
            return false;
        },
        c_init: function () {

        },
        c_save: function (model) {

        },
        c_sync: function (model) {

        },
        p_init: function () {

        },
        p_save: function (model) {

        },
        p_sync: function (model) {

        },
        set_price: function (pricelist, product, quantity) {
            var self = this;
            var date = moment().startOf('day');
            var pricelist_items = _.filter(pricelist.items, function (item) {
                return (!item.product_tmpl_id || item.product_tmpl_id[0] === product.product_tmpl_id[0]) &&
                    (!item.product_id || item.product_id[0] === self.id) &&
                    (!item.date_start || moment(item.date_start).isSame(date) || moment(item.date_start).isBefore(date)) &&
                    (!item.date_end || moment(item.date_end).isSame(date) || moment(item.date_end).isAfter(date));
            });

            var price = product.lst_price;

            _.find(pricelist_items, function (rule) {
                if (rule.min_quantity && quantity < rule.min_quantity) {
                    return false;
                }

                if (rule.base === 'pricelist') {
                    price = self.set_price(rule.base_pricelist, product);
                } else if (rule.base === 'standard_price') {
                    price = product.standard_price;
                }

                if (rule.compute_price === 'fixed') {
                    price = rule.fixed_price;
                    return true;
                } else if (rule.compute_price === 'percentage') {
                    price = price - (price * (rule.percent_price / 100));
                    return true;
                } else {
                    var price_limit = price;
                    price = price - (price * (rule.price_discount / 100));
                    if (rule.price_round) {
                        price = round_pr(price, rule.price_round);
                    }
                    if (rule.price_surcharge) {
                        price += rule.price_surcharge;
                    }
                    if (rule.price_min_margin) {
                        price = Math.max(price, price_limit + rule.price_min_margin);
                    }
                    if (rule.price_max_margin) {
                        price = Math.min(price, price_limit + rule.price_max_margin);
                    }
                    return true;
                }
            });
            product.price = price;
        },
        pricelist_modifier: function () {
            var model = this.get_model('product.pricelist');
            var _super_loaded = model.loaded;
            model.loaded = function (self, pricelists) {
                var done = $.Deferred();
                _super_loaded(self, pricelists);
                self.pricelist = _.findWhere(pricelists, {id: self.config.pricelist_id[0]});
                self.pricelist.items = [];

                self.get_pricelist_items([], [['pricelist_id', '=', self.pricelist.id]], [], false)
                    .then(function (pricelist_items) {
                        _.each(pricelist_items, function (item) {
                            self.pricelist.items.push(item);
                            item.base_pricelist = self.pricelist;
                        });
                        done.resolve();
                    });
                return done;
            }
        },
        get_pricelist_items: function (fields, domain, order, context) {
            return new Model('product.pricelist.item')
                .query(fields)
                .filter(domain)
                .order_by(order)
                .context(context)
                .all();
        }
    });
});