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
    var pagePrev = null;
    var pageNext = null;

    function debug( p, o) {

      console.log( p + ": " + (o ? (o.attr("id") + " " + o.css("left")): "<>") );
    }

    function linkHandler(e) {
        // Prevent clicked A tag from attempting to navigate
        e.preventDefault();

        // todo: backbone history

        // Send navigation event to Google Analytics
        _gaq.push(['_trackPageview', location.pathname + location.search + e.target.hash]);

        // grab a handle the # section of the navigation link clicked
        pageNext = $(e.target.hash);

        console.log("---------------------------");
        debug("prev", pagePrev );
        debug("curr", pageCurr );
        debug("next", pageNext );

        var PageNextToPos;
        var PageCurrToPos;

        // todo: clean up this page sliding logic
        if( !pagePrev )
        {
                        pageNextToPos = 0;
                        pageCurrToPos = -1*pageWidth;
        } else {
                if( pageNext.attr("id") == pagePrev.attr("id") )
                {
                        if( parseInt(pageNext.css("left")) == pageWidth ) {
                                pageNextToPos = 0;
                                pageCurrToPos = -1*pageWidth;
                        } else {
                                pageNextToPos = 0;
                                pageCurrToPos = pageWidth;
                        };
                } else {
                        if( parseInt(pagePrev.css("left")) == parseInt(pageNext.css("left"))  ) {
                                pageNextToPos = 0;
                                pageCurrToPos = -1*pageWidth;
                        } else {
                                if(parseInt(pageNext.css("left")) == parseInt(pageWidth)) {
                                        pageNextToPos = 0;
                                        pageCurrToPos = -1*pageWidth;
                                } else {
                                        pageNextToPos = 0;
                                        pageCurrToPos = pageWidth;
                                };
                        };
                };
        }
        pageNext.css("left", pageNextToPos);
        pageCurr.css("left", pageCurrToPos);

        // update page pointers
        pagePrev = pageCurr;
        pageCurr = pageNext;
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
        url: function() {return '/data/client/' + this.id}
    });


    var ClientMobileView = Backbone.View.extend({
        el:  "#page-container",

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
            $(this.el).append(ClientMobileView.template(this.client));

            // resize pages on window resize;
            // todo: adjust pagePrev offset on resize
            $(window).resize(function() {
              pageWidth = $(window).width();
            });

            // initialize pages and bind linkHandler to links
            $(".page").css("left", pageWidth);
            $(".page").css("top", 65);
            $(".page").addClass("transform");
            $("A").bind("click", function(e) {
              linkHandler(e);
            });

            // hide Loading panel
            $("#loading").remove();

            // load initial page
            // todo: look into a more appropriate way to select first page
            pageCurr = $(".page:eq(0)");
            pageCurr.css("left",0);

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
            var qrUrl = "http://chart.apis.google.com/chart?cht=qr&chs=100x100&chld=H|0&chl="+shortCode;
            dict['qrUrl']=qrUrl;
            $(this.el).html(ClientCardView.template(dict));
            return this;
        },

        buyIt: function() {
            alert("buying...");
        }

    });

    var ClientSignView = Backbone.View.extend({
        el:  "#client-sign-view",

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
            var qrUrl = "http://chart.apis.google.com/chart?cht=qr&chs=500x500&chld=H|0&chl="+shortCode;
            dict['qrUrl']=qrUrl;
            $(this.el).html(ClientSignView.template(dict));
            return this;
        },

        buyIt: function() {
            alert("buying...");
        }

    });

    var ClientStoryView = Backbone.View.extend({
        el:  "#client-story-view",

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
            var qrUrl = "http://chart.apis.google.com/chart?cht=qr&chs=100x100&chld=H|0&chl="+shortCode;
            dict['qrUrl']=qrUrl;
            $(this.el).html(ClientStoryView.template(dict));
            return this;
        },

        buyIt: function() {
            alert("buying...");
        }

    });

});
