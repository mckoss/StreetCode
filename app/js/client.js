namespace.module('streetcode.client', function (exports, requires) {
    exports.extend({
        'initProfile': initProfile,
        'initDonation' : initDonation,
        'initCard': initCard,
        'initSign': initSign,
        'initStory': initStory,
        'updateDonation': trackDonation,
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
        p.css("max-height",1000);
        //p.css("opacity", 100);

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
         // hide Loading panel
        $("#loading").remove();
        
        trackDonation(); 
    }

    function trackDonation() {
        console.log( new Date() );
        var shortCode = document.location.pathname.split('/').pop(); 

        var clientDonationTemplate = _.template($('#client-donation-template').html()); 
        var itemTransactionTemplate = _.template($('#item-transaction-template').html());
        
        var listHtml = ""; 
        var summaryHtml = ""; 

        var client; 

        $.ajax({
            url: '/data/client?shortCode=' + shortCode.toLowerCase(),
            dataType: 'json',
            success: function (data) {
                client = data[0]; 

                // ... Then get the transactions for this client id 
                $.ajax({
                    url: '/data/transaction?client=' + client.id + '&no-cache',
                    dataType: 'json', 
                    success: function(data) {
                        //Sort transactions such that the latest is in the front 
                        data.sort(     function (a, b) {
                            if (a.created == b.created ) return 0; 
                            else if (a.created > b.created ) return -1 ; 
                            else return 1; 
                        } );

                        client.totalDonation = 0; 
                        client.donors = {}; 
                        client.numDonors = 0; 
                        for ( var i = 0; i < data.length; i++ ) {
                            // accumulate total donation
                            client.totalDonation += data[i].amount;

                            // accumulate independent donor donation
                            if ( client.donors[data[i].donor.email] == null ) {
                                client.donors[data[i].donor.email]  = 0; 
                                client.numDonors += 1
                            }
                            client.donors[ data[i].donor.email ] += data[i].amount; 
                        }

                        client.goal = Math.max(client.goal, 0);

                        // Fetch latest 5 transactions
                        for ( var i = 0; i < Math.min(5, data.length); i++ ) {
                            var transaction = data[i]; 
                            transaction.donorName = data[i].donor.name;
                            transaction.ago = calcTimeAgo(data[i].created); 
                            listHtml += itemTransactionTemplate(transaction);
                        }

                        // Render the gauge, 
                        summaryHtml = clientDonationTemplate(client);
                        $("#donationSummary").html(summaryHtml); 
                        drawGauge(client.totalDonation, client.goal);
                        $("#listThanks").html(listHtml); 
                        
                        
                    }, 
                    failure: function(err) {
                        console.log(err);
                    }
                });
            
            }
        });
        
        setTimeout ( "namespace.streetcode.client.updateDonation()", 15000);
      }

    function drawGauge(amount, goal) {
        // Create and populate the data table.
        var data = google.visualization.arrayToDataTable([
            ['Label', 'Value'],
            ['Donations', amount]
        ]);

        var gaugeMax = Math.max( goal, amount);
        var options = {
            max: gaugeMax,
            height: 160,
            redFrom: 0.9 * goal, redTo: gaugeMax,
            yellowFrom:0.75 * goal, yellowTo: 0.90 * goal,
            minorTicks: 5
        };

      // Create and draw the visualization.
      new google.visualization.Gauge(document.getElementById('gauge')).draw(data, options);
    }


    function calcTimeAgo (pastTime ) {
        var d = new Date(); 

        var msDiff = d.getTime()-d.getMilliseconds() - pastTime ;
        if ( msDiff < 1000 ) 
            return "0 min ago"; 

        var minDiff = msDiff/1000/60; 
        if ( minDiff < 60 )
            return Math.floor( minDiff )+ ((Math.floor( minDiff )==1) ? " minute" : " minutes") + " ago"; 

        var hrDiff = minDiff/60; 
        if (hrDiff < 24) 
            return  Math.floor( hrDiff )+ ((Math.floor( hrDiff ) == 1) ? " hour" : " hours") + " ago" ; 

        var dayDiff = hrDiff / 24 ;
        return  Math.floor(dayDiff) + ((Math.floor(dayDiff) == 1) ? " day" : " days" )+ " ago";
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
