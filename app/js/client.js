namespace.module('streetcode.client', function (exports, requires) {
    exports.extend({
        'initProfile': initProfile,
        'initCard': initCard,
        'initSign': initSign,
        'initStory': initStory,
    });

    // Page navigation vars
    var pageCurr = null;

    // Only Android and Iphone use Touch event
    // Mixed results for Click
    // So we'll use legacy Mousedown - should have universal support
    // Todo: mousedown cancels on mouseup... probably need to figure out how to work around that
    var clickEvent = "click";

    function initPages()
    {
        // disable moving on touch-capable devices
        document.ontouchmove = function(event) {
        //    event.preventDefault();
        };

        // bind links to Accordian
        $("a[class!='external']").bind(clickEvent, function(e) {
            var event = e;

            // prevent navigation
            event.preventDefault();

            // stop propegation
            event.cancelBubble = true;
            if (event.stopPropagation) event.stopPropagation();

            // call link handler
            handleClick(event);
        });

        // hide Loading panel
        $("#loading").remove();

        // select hash on initial load
        // load home if no hash
        var hash = document.location.hash;
        if( hash.length < 1 ) {
            hash = "#home";
        // load needs if app if navigationg back from paypal
        } else if(hash.indexOf("give/") > -1) {
            hash = "#needs"
        }
        $( "a[href='" + hash + "']:first").trigger( clickEvent );

        // window.scollTo(0,0);
    }

    function handleClick(e) {
        var to = e.target.hash;

        // send event to Google Analytics
        // don't fire on initial page render
        if(pageCurr) {
            pushNavigation(to);
        }

        // Dipslay target
        if(to.indexOf("/") < 0) {
            Accordian(e.target.hash);
        // Submit donation on #give/x event
        } else {
            $("#amount").val(to.split("/")[1]);
            $("#ppPayment").submit();
        }
    }

    // Send navigation event to Google Analytics
    function pushNavigation(loc){
        //window.location.hash = loc;
        _gaq.push(["_trackPageview", loc]);
    }

    // Toggle application pages
    function Accordian(page)
    {
        var p = $(page);

        if (pageCurr) {
            if (pageCurr.attr("id") == p.attr("id")) {
                return;
            }
            pageCurr.removeClass('open');
        }

        p.addClass('open');
        pageCurr = p;
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

        // Re-render the contents of the mobile view
        render: function() {
            $(this.el).append(ClientMobileView.template(this.client));

            // initialize app pages
            initPages();

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
