namespace.module('streetcode.client', function (exports, requires) {
    exports.extend({
        'initProfile': initProfile,
        'initCard': initCard,
        'initSign': initSign,
        'initStory': initStory,
    });

  // Page navigation vars
    var pageWidth = $(window).width();
    var pageCurr = null;
    var pageNext = null;

    function initRouter()
    {
        // Initiate the router
        var router = new AppRouter;
        // Start Backbone history a neccesary step for bookmarkable URL's
        Backbone.history.start();
    }

    var AppRouter = Backbone.Router.extend({
        routes: {
            "give/:amount": "give",
            "*actions": "linkHandler" // matches http://example.com/#anything-here

        },
        pushLocation: function( loc ){
            _gaq.push(['_trackPageview', loc]);
        },
        give: function( amount ){
            // Send navigation event to Google Analytics
            this.pushLocation( location.pathname + location.hash);

            // set PayPal donation amount
            $("#amount").val(amount);

            // Submit donation to PayPal
            $("#_xclick").submit();
        },
        linkHandler: function( actions ){
            // Send navigation event to Google Analytics
            this.pushLocation( location.pathname + location.hash);

            // grab a handle the # section of the navigation link clicked
            // if no actions, navigate home
            var page = (actions) ? actions : "home";
            page = "#" + page;
            pageNext = $(page);

            // slide pages
            $('div .page').each(function(index) {
                $(this).css("left",-1*pageWidth);
                $(this).removeClass("transform");
            });
            if(pageCurr) {
                //alert(pageCurr.css("left"));
                //pageCurr.css("left", -1*pageWidth);
                //pageCurr.removeClass("transform");
            }
            pageNext.css("left", pageWidth);
            pageNext.addClass("transform");
            pageNext.css("left", 0);

            // update page pointers
            pageCurr = pageNext;
        }
    });

    function debug( p, o) {
      console.log( p + ": " + (o ? (o.attr("id") + " " + o.css("left")): "<>") );
    }

    function initProfile() {
        ClientMobileView.template =  _.template($('#client-view-template').html());
        exports.app = new ClientMobileView();
    }

    function initCard() {
        ClientCardView.template =  _.template($('#client-view-template').html());
        exports.app = new ClientCardView();
    }

    function initSign() {
        ClientSignView.template =  _.template($('#client-view-template').html());
        exports.app = new ClientSignView();
    }

    function initStory() {
        ClientStoryView.template =  _.template($('#client-view-template').html());
        exports.app = new ClientStoryView();
    }

    var ClientList = Backbone.Collection.extend({
        model: Client,
        url: '/data/client'
    });

    var Client = Backbone.Model.extend({
        url: function() {return '/data/client/shortCode=' + this.id}
    });

    var ClientMobileView = Backbone.View.extend({
        el:  "#page-container",

        // The ClientView listens for changes to its model, re-rendering.
        initialize: function() {
            var shortCode = location.pathname.split('/').pop();
            var self = this;
            $.ajax({
                url: '/data/client?shortCode=' + shortCode.toLowerCase(),
                dataType: 'json',
                success: function (data) {
                    self.client = data[0];
                    self.render();
                }});
        },

        // Re-render the contents of the todo item.
        render: function() {
            $(this.el).append(ClientMobileView.template(this.client));

            // resize pages on window resize;
            // todo: adjust pagePrev offset on resize
            $(window).resize(function() {
              pageWidth = $(window).width();
            });

            // hide Loading panel
            $("#loading").remove();

            // initialize pages
            $("div .page").css("left", pageWidth);
            $("div .page").css("top", 65);

            // initialize backbone router
            initRouter();

            return this;
        },

    });

    var ClientCardView = Backbone.View.extend({
        el:  "#client-card-view",

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
            var qrUrl = "http://chart.apis.google.com/chart?cht=qr&chs=100x100&chld=H|0&chl="+shortCode;
            dict['qrUrl']=qrUrl;
            $(this.el).html(ClientCardView.template(dict));
            return this;
        },

    });

    var ClientSignView = Backbone.View.extend({
        el:  "#client-sign-view",

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
            var qrUrl = "http://chart.apis.google.com/chart?cht=qr&chs=500x500&chld=H|0&chl="+shortCode;
            dict['qrUrl']=qrUrl;
            $(this.el).html(ClientSignView.template(dict));
            return this;
        },

    });

    var ClientStoryView = Backbone.View.extend({
        el:  "#client-story-view",

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
            var qrUrl = "http://chart.apis.google.com/chart?cht=qr&chs=100x100&chld=H|0&chl="+shortCode;
            dict['qrUrl']=qrUrl;
            $(this.el).html(ClientStoryView.template(dict));
            return this;
        },

    });

});
