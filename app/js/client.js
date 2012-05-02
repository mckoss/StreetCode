namespace.module('streetcode.client', function (exports, requires) {
    exports.extend({
        'initProfile': initProfile,
        'initDonation' : initDonation,
        'initCard': initCard,
        'initSign': initSign,
        'initStory': initStory,
    });

    // Page navigation vars
    var pageCurr = null;

    function initPages()
    {
        // bind links to Accordian 
        $("a").bind('click', function(e) {
            // prevent navigation
            e.preventDefault();

            // call link handler
            handleClick(e);
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
        $( "a[href='" + hash + "']:first").trigger('click');
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
        _gaq.push(['_trackPageview', loc]);
    }

    // Toggle application pages
    function Accordian(page)
    {
        var p = $(page);

        // collapse currently loaded page
        if(pageCurr) {
            // exit if page is same as page loaded
            if(pageCurr.attr("id") == p.attr("id") ) {
                return false;
            }
            //pageCurr.css("opacity", 0);
            pageCurr.css("max-height",0);
        }

        // expand target page
        //p.css("opacity", 100);
        p.css("max-height",400);

        // store pointer to current page
        pageCurr = p;
    }

    function initDonationPage() {
        // hide Loading panel
        $("#loading").remove();
    }

    function initProfile() {
        ClientMobileView.template =  _.template($('#client-view-template').html());
        exports.app = new ClientMobileView();
    }

    function initDonation() {
        ClientDonationView.template = _.template($('#client-donation-template').html()); 
        exports.app = new ClientDonationView(); 
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

    var ClientDonationView = Backbone.View.extend({
        // el: "#client-donation-view", 
        el: "#page-container",

        // Get client and transactions 
        initialize: function() {
            var shortCode = location.pathname.split('/').pop();
            var self = this; 

            self.getTransactions(self, shortCode);
        }, 

        getTransactions: function(self, shortCode) {
            self.transactions = new Array(5); 
            self.itemTransactionTemplate = _.template($('#item-transaction-template').html());

            // First query for the client ... 
            $.ajax({
                url: '/data/client?shortCode=' + shortCode.toLowerCase(),
                dataType: 'json',
                success: function (data) {
                    self.client = data[0];

                    // ... Then get the transactions for this client id 
                    $.ajax({
                        url: '/data/transaction?client=' + self.client.id,
                        dataType: 'json', 
                        success: function(data) {
                            if ( data.length == 0 ) {
                                self.render();
                                return; 
                            }

                            //Sort transactions such that the latest is in the front 
                            data.sort( function(a, b) {
                                if (a.created == b.created ) return 0; 
                                else if (a.created > b.created ) return -1 ; 
                                else return 1; 
                            });

                            self.client.totalDonation = 0; 
                            for ( var i = 0; i < data.length; i++ ) {
                                self.client.totalDonation += data[i].amount;
                                
                            }

                            var listHtml = ""; 
                            for ( var i = 0; i < Math.min(5, data.length); i++ ) {
                                var transaction = data[i]; 
                                transaction.donorName = data[i].donor.name;
                                transaction.ago = self.calcTimeAgo(data[i].created); 
                                listHtml += self.itemTransactionTemplate(transaction);
                            }
                            $("#listThanks").append(listHtml); 

                            self.render();
                        }, 
                        failure: function(err) {
                            console.log(err);
                        }
                    });

                }});
        },

        calcTimeAgo: function(pastTime ) {
            var d = new Date(); 

            var msDiff = d.getTime()-d.getMilliseconds() - pastTime ;
            if ( msDiff < 1000 ) 
                return "0 min ago"; 

            var minDiff = msDiff/1000/60; 
            if ( minDiff < 60 )
                return Math.floor( minDiff )+ " min ago"; 

            var hrDiff = minDiff/60; 
            if (hrDiff < 24) 
                return  Math.floor( hrDiff )+ " hrs ago" ; 

            return  Math.floor(hrDiff / 24 ) + " days ago";
        },
 
        // Render the content 
        render: function() {
            $(this.el).append(ClientDonationView.template(this)); 
            initDonationPage(); 
            return this; 
        }
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
