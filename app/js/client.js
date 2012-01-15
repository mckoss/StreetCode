namespace.module('streetcode.client', function (exports, requires) {
    exports.extend({
        'initProfile': initProfile,
    });

    function initProfile() {
        ClientMobileView.template =  _.template($('#client-view-template').html());
        exports.app = new ClientMobileView();
    }

    var Client = Backbone.Model.extend({
        url: function() {return '/data/client/' + this.id}
    });

    var ClientMobileView = Backbone.View.extend({
        el:  "#client-view",

        // The DOM events specific to an item.
        events: {
            'click .buy': 'buyIt'
        },

        // The ClientView listens for changes to its model, re-rendering.
        initialize: function() {
            // STUB
            var id = location.pathname.split('/').pop();
            this.model = new Client({id: id});
            this.model.bind('change', this.render, this);
            this.model.fetch();
        },

        // Re-render the contents of the todo item.
        render: function() {
            $(this.el).html(ClientMobileView.template(this.model.toJSON()));
            // Force page to be "re-enhanced" by jQuery mobile
            $('#client-page').trigger('create');
            return this;
        },

        buyIt: function() {
            alert("buying...");
        }

    });

}); // seagtug.todos
