odoo.define('rminds_worksheet_templates.relational_fields', function (require) {
"use strict";

const FieldsRegistry = require('web.field_registry');
var relational_fields = require('web.relational_fields');

var scale_title = relational_fields.FieldMany2Many.include({
    //when click on 'add a line' O2M field scale_ids in workcenter, change wizard title to "Maintenance Scale"
    onAddRecordOpenDialog: function () {
        if (this.model == 'mrp.workcenter' && this.name == 'scale_ids'){
            this.string = "Maintenance Scales"
        }
        return this._super();
    }
});


$(document).on('click', '.nav-item', function () {
    if($(this).text().indexOf('Checklist/Instructions') !=-1){
        var element_id = $(this).find('a').attr('href')
        $(element_id).find('th[data-name="name"]').css('color', 'white')
    }

});


return {
    scale_title: scale_title,
};

});