odoo.define('web_studio.OldViewRenderers', function (require) {
"use strict";

var AbstractRenderer = require('web.AbstractRenderer');
var Bus = require('web.Bus');
var data = require('web.data');
var ViewManager = require('web.ViewManager');

return AbstractRenderer.extend({
    className: 'o_web_studio_old_view_renderer',
    view_type: undefined,
    init: function() {
        this._super.apply(this, arguments);
        this.fields_view = {
            arch: this.arch,
            fields: this.fields,
            model: this.state.model,
        };
        var views = [{
            view_type: this.view_type,
            fields_view: this.fields_view,
        }];
        var dataset = new data.DataSetSearch(this, this.state.model);
        this.view_manager = new ViewManager(this, dataset, views, {
            auto_search: true,
            search_view: true,
        });
        this.view_manager.set_cp_bus(new Bus());
    },
    start: function() {
        // Put a div over the view_manager to intercept all clicks
        this.$el.append($('<div>', { 'class': 'o_web_studio_overlay' }));
        return this.view_manager.prependTo(this.$el);
    },
});

});
