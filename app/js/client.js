namespace.module('streetcode.client', function (exports, requires) {
    exports.extend({
        'initProfile': initProfile,
    });

    function initProfile() {
        ClientMobileView.template =  _.template($('#client-view-template').html());
        exports.app = new ClientMobileView();
        
        ClientCardView.template =  _.template($('#client-view-template').html());
        exports.app = new ClientCardView();
    }

    var ClientList = Backbone.Collection.extend({
        model: Client,
        url: '/data/client'
    });

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
            var shortCode = location.pathname.split('/').pop().slice(1);
            var self = this;
            $.ajax({
                url: '/data/client?shortCode=' + shortCode,
                dataType: 'json',
                success: function (data) {
                    self.client = data[0];
                    self.render();
                }});
        },

        // Re-render the contents of the todo item.
        render: function() {
            $(this.el).html(ClientMobileView.template(this.client));
            // Force page to be "re-enhanced" by jQuery mobile
            $('#client-page').trigger('create');
            return this;
        },

        buyIt: function() {
            alert("buying...");
        }

    });
    
    var ClientCardView = Backbone.View.extend({
        el:  "#client-card-view",

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
            var dict = this.model.toJSON();
            var shortCode = encodeURIComponent('http://'+location.hostname+'/1'+dict['shortCode']);
            var qrUrl = "http://chart.apis.google.com/chart?cht=qr&chs=300x300&chld=H|0&chl="+shortCode;
            dict['qrUrl']=qrUrl;
            $(this.el).html(ClientMobileView.template(dict));
            // Force page to be "re-enhanced" by jQuery mobile
            $('#client-page').trigger('create');
            return this;
        },

        buyIt: function() {
            alert("buying...");
        }

    });

}); // seagtug.todos
