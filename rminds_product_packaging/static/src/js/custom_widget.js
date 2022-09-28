odoo.define('rminds_product_packaging.custom_widget', function(require) {
"use strict";

var field_registry = require('web.field_registry');
var AbstractField = require('web.AbstractField');
var FormController = require('web.FormController');

FormController.include({
    _update: function () {
        var _super_update = this._super.apply(this, arguments);
 
        this.trigger('view_updated');
        return _super_update;
    },
});

var package_qty = AbstractField.extend({
    template: 'PackageQtyWidget',
    _render: function () {
        var self = this;
        console.log(this, "tttt")
        var qty = this.recordData.packaging_qty || ''
        var type = this.recordData.packaging_type || ''
        if (qty && type && parseInt(qty) > 1){
            type = type+'s'
        }
        if (qty){
            qty = "<span>" + qty + "</span>"
        }
        if (type){
            type = "<span style='font-style: italic;'>" + type + "</span>"
        }
        var text = qty + " " + type
        if (qty){
            this.$el.html(text)
        }
        return this._super();
    },

});

field_registry.add('package_qty', package_qty);

return {
    package_qty: package_qty,
};

});