odoo.define('ks_dashboard_ninja.domain_fix', function (require) {

"use strict";

var BasicModel = require('web.BasicModel');
var BasicFields = require('web.basic_fields');
var view_dialogs = require('web.view_dialogs');
var core = require("web.core");

var _t = core._t;

// Whole Point of this file is to enable users to use %UID to calculate domain dynamically.
BasicModel.include({

        _fetchSpecialDomain: function (record, fieldName, fieldInfo) {
           var fieldName_temp = fieldName;
           if(record._changes && record._changes[fieldName]) {
                if(record._changes[fieldName].includes("%UID")){
                    fieldName_temp = fieldName+'_temp';
                    record._changes[fieldName_temp] = record._changes[fieldName].replace('"%UID"',record.getContext().uid);
                }
           } else if (record.data[fieldName] && record.data[fieldName].includes("%UID")){
                fieldName_temp = fieldName+'_temp';
                record.data[fieldName_temp] = record.data[fieldName].replace('"%UID"',record.getContext().uid);
           }

           return this._super(record, fieldName_temp, fieldInfo);
        },

    });

BasicFields.FieldDomain.include({

           _onShowSelectionButtonClick: function (e) {
                if(this.value && this.value.includes("%UID")){
                    var temp_value = this.value.replace('"%UID"',this.record.getContext().uid);
                    e.preventDefault();
                    new view_dialogs.SelectCreateDialog(this, {
                        title: _t("Selected records"),
                        res_model: this._domainModel,
                        domain: temp_value,
                        no_create: true,
                        readonly: true,
                        disable_multiple_selection: true,
                    }).open();
                }else{
                    this._super.apply(this, arguments);
                }
           },
    });

});