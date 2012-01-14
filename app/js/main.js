namespace.module('streetcode.main', function (exports, require) {
    var client = require('streetcode.client');

    $(document).ready(init);

    function init() {
        client.init();
    }

}); // streetcode.main
