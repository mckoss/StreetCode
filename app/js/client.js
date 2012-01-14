namespace.module('streetcode.client', function (exports, requires) {
    exports.init = init;

    function init() {
        Client.template =  _.template($('#client-profile-template').html());
        exports.app = new ClientView();
    }

    var Client = Backbone.Model.extend({

    });

    var ClientList = Backbone.Collection.extend({
        model: Client,
        url: '/data/client'
    });

    var ClientView = Backbone.View.extend({
        tagName:  "div",

        // The DOM events specific to an item.
        events: {
            'click .buy': 'buyIt'
        },

        // The ClientView listens for changes to its model, re-rendering.
        initialize: function() {
            this.model.bind('change', this.render, this);
            this.model.bind('error', this.reportError, this);
        },

        reportError: function(model, response, options) {
             var data = JSON.parse(response.responseText);
             alert(data.status || response.statusText);
        },

        // Re-render the contents of the todo item.
        render: function() {
            $(this.el).html(ClientView.template(this.model.toJSON()));
            return this;
        },

        buyIt: function() {
        }

    });

}); // seagtug.todos
