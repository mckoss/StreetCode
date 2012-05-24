namespace.module('streetcode.donation', function (exports, requires) {
    exports.extend({
          'initDonation' : initDonation,
      });

    var REFRESH_INTERVAL = 15000;

    function initDonation() {
         // hide Loading panel
        $("#loading").remove();

        trackDonation();
        setInterval(trackDonation, REFRESH_INTERVAL);
    }

    function trackDonation() {
        // console.log( new Date() );
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
                        client.goalPercentage = 0;
                        client.donors = {};
                        client.numDonors = 0;
                        for ( var i = 0; i < data.length; i++ ) {
                            // Count "Completed" payments only
                            if ( data[i].paymentStatus !='Completed' )
                                continue;

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
                        client.goalPercentage = Math.floor( client.totalDonation / client.goal * 100); 

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

      }

    function drawGauge(amount, goal) {
        // Create and populate the data table.
        var data = google.visualization.arrayToDataTable([
            ['Label', 'Value'],
            ['$ donated', amount]
        ]);

        var gaugeMax = Math.max( goal, amount);
        var tickMark = {}; 
        for ( var i = 0; i < gaugeMax ; i += 0.2 * gaugeMax)
            tickMark[i] = i.toString(); 
        var options = {
            max: gaugeMax,
            width: 300, height: 500,
            redFrom: 0, redTo: 0.60 * goal,
            yellowFrom:0.60 * goal, yellowTo: 0.90 * goal,
            greenFrom: 0.9 * goal, greenTo: gaugeMax,
            minorTicks: 10, majorTicks: tickMark
        };

      // Create and draw the visualization.
      var gaugeChart = new google.visualization.Gauge(document.getElementById('gauge'));
      gaugeChart.draw(data, options);
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

});