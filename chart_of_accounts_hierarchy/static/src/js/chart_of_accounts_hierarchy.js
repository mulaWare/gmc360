odoo.define('chart_of_accounts_hierarchy.coa_hierarchy', function (require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    
    var crash_manager = require('web.crash_manager');
    var session = require('web.session');

    var _t = core._t;
    var QWeb = core.qweb;

    
    var tree = "";
    var rowids = [];
    var allchildids = [];
    var Level = 0;

    var ChartOfAccountsHierarchy= AbstractAction.extend({        
        events: {
            'click .toggle': 'onclicktoggle',
            'click #download_pdf': 'action_download_coa_hierarchy_pdf',
            'click #download_xls': 'action_download_coa_hierarchy_xls',
        },
        init: function(parent, action) {            
            this._super.apply(this, arguments);            
            var self = this;           
            var datalist =[];
            var def = self._rpc({
                model: 'account.account',
                method: 'get_coa_hierarchy_info',
            }, []).then(function (res) {                
                self.datalist = JSON.parse(JSON.stringify(res));
                self.datalist.sort(function(a, b){
                    return b.Child_Length - a.Child_Length;
                });
            }).done(function(){
                self.render();
            });
        },
        start: function() {
            var self = this;           
            return this._super();
        },
        render: function() {
            var self = this;
            this.$el.empty()  
            var template = self.$el.html(QWeb.render("ChartOfAccountsHierarchy", {widget: self}));

            self.getrowids();          
            self.populatetreenode("0");

            var togglerow = this.$el.find("#togglerow");
            togglerow.innerHTML = "";
            togglerow.html(tree);
            tree = "";
            return template
        },
        getrowids: function(){  
            var self = this;
            var datalist = this.datalist;
            if (undefined !== datalist && datalist.length) {
                for (var i = 0; i < datalist.length; i++) { 
                    rowids.push(datalist[i].ID)
                }
            }
        },    
        
        getallchildids: function(parentid){            
            var self = this;   
            var datalist = this.datalist;
            if (undefined !== datalist && datalist.length) {
                var newdata = datalist.filter(function (value) {
                    return (value.ParentID == (parentid));
                });

                newdata.forEach(function (e) {
                    allchildids.push(e.ID);
                    self.getallchildids(e.ID);
                })
            }
            return allchildids;
        },
        getchildids: function(parentid){
            var self = this; 
            var datalist = this.datalist;  
            var cids = []       
            if (undefined !== datalist && datalist.length) {              
                var newdata = datalist.filter(function (value) {
                    return (value.ParentID == (parentid));
                });

                newdata.forEach(function (e) {
                    cids.push(e.ID);
                })
            }
            return cids;
        },
        
        onclicktoggle: function(ev){
            ev.stopPropagation();
            ev.preventDefault();
            var self= this;            
            var datalist = this.datalist;
            var targetid = ev.currentTarget.id;
            
            var allchildids = self.getallchildids(targetid);
            var childids = self.getchildids(targetid);
            var targettr = document.getElementById(targetid).closest('tr');


            if ($(targettr).hasClass('ccollapse') && (childids.length > 0)){

                for (var i = 0; i < allchildids.length; i++) {
                    var allchildtargettr = document.getElementById(allchildids[i]).closest('tr');
                    $(allchildtargettr).hide();
                }
                allchildids.length=0;  
                $(targettr).removeClass('ccollapse').addClass('cexpand');
            }
            else {
                for (var i = 0; i < allchildids.length; i++) {
                    var allchildtargettr = document.getElementById(allchildids[i]).closest('tr');
                    $(allchildtargettr).removeClass('cexpand').addClass('ccollapse');
                    $(allchildtargettr).show();
                }
                $(targettr).removeClass('cexpand').addClass('ccollapse');
                allchildids.length=0;           
            }
        },
        nodelevel: function(ID){            
            var self = this;
            var datalist = this.datalist;
            if (undefined !== datalist && datalist.length) {
                var newdata = datalist.filter(function (value) {
                    return (value.ID == ID);
                });
        
                newdata.forEach(function (e) {
                    Level++;
                    self.nodelevel(e.ParentID);
                });
            }
            return Level;
        },
        populatetreenode: function(parentid){
            var self = this;
            var datalist = this.datalist;

            if (undefined !== datalist && datalist.length) {
                var newdata = datalist.filter(function (value) {                
                    return (value.ParentID == parentid);
                });
                
                newdata.forEach(function (e) {
                    
                    var childids = self.getchildids(e.ID);                
                    var levl = 'clevel'+self.nodelevel(e.ID);
                    
                    Level = 0;

                    tree += "<tr class='ccollapse "+ levl +"'>";       
                    var parentItem = "<td><span class='toggle' id='"+ e.ID +"'>" + e.Code + "</td><td>" + e.Name + "</td><td>" + e.Type + "</td><td>" + e.Debit + "</td><td>" + e.Credit + "</td><td>" + e.Balance + "</td>";


                    if ((childids.length > 0) && ((rowids.indexOf(e.ParentID) !== -1)== false)){   
                        
                        tree += "<tr class='ccollapse "+ levl +"'>";       
                        var parentItem = "<td><span class='toggle' id='"+ e.ID +"'>" + e.Code + "</td><td>" + e.Name + "</td><td>" + e.Type + "</td><td>" + e.Debit + "</td><td>" + e.Credit + "</td><td>" + e.Balance + "</td>";
                    }

                    if ((childids.length > 0) && ((rowids.indexOf(e.ParentID) !== -1)== true)){                   
                        tree += "<tr class='ccollapse "+ levl +"'>";       
                        var parentItem = "<td><span class='toggle' id='"+ e.ID +"'>" + e.Code + "</td><td>" + e.Name + "</td><td>" + e.Type + "</td><td>" + e.Debit + "</td><td>" + e.Credit + "</td><td>" + e.Balance + "</td>";
                    }

                    if ((childids.length == 0) && ((rowids.indexOf(e.ParentID) !== -1)== true)){                    
                        tree += "<tr class='ccollapse "+ levl +"'>";       
                        var parentItem = "<td><span id='"+ e.ID +"'>" + e.Code + "</td><td>" + e.Name + "</td><td>" + e.Type + "</td><td>" + e.Debit + "</td><td>" + e.Credit + "</td><td>" + e.Balance + "</td>";
                    }

                    if ((childids.length == 0) && ((rowids.indexOf(e.ParentID) !== -1)== false)){                    
                        tree += "<tr class='ccollapse "+ levl +"'>";       
                        var parentItem = "<td><span id='"+ e.ID +"'>" + e.Code + "</td><td>" + e.Name + "</td><td>" + e.Type + "</td><td>" + e.Debit + "</td><td>" + e.Credit + "</td><td>" + e.Balance + "</td>";
                    }
                    tree = tree + parentItem;
                    self.populatetreenode(e.ID);
                    tree += "</tr>";                              
                })
            }else{
                self.do_warn(_t('Warning: Please Configure Chart of Accounts'));
            }
        },
        action_download_coa_hierarchy_pdf: function(){
            var self = this;
            var action = {
                'type': 'ir.actions.report',
                'report_type': 'qweb-pdf',
                'data' : {'Report Name' : 'Char Of Accounts Hierarchy PDF'},
                'report_name': 'chart_of_accounts_hierarchy.report_coa_hierarchy',
                'report_file': 'chart_of_accounts_hierarchy.report_coa_hierarchy',              
                'display_name': 'Char Of Accounts Hierarchy',
            };
            return this.do_action(action);
        },
        action_download_coa_hierarchy_xls: function(){
            var self = this;
            session.get_file({
                url: 'coa_export_xls',                
                error: crash_manager.rpc_error.bind(crash_manager)
            });
        }
        

    });
    
    core.action_registry.add('chart_of_accounts_hierarchy.coa_hierarchy', ChartOfAccountsHierarchy);
    
    return ChartOfAccountsHierarchy;
    
    });