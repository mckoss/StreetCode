namespace.module('startpad.json-rest', function(exports, require) {
    /* An object request broker (ORB) for making REST calls to JSON
       objects stored on a backend server.

       Usage:

         db = jsonRest.Connection('/data');
         collection = db.Collection('type');
         model = collection.Model();
         model.put() -> POST /data/model -> {id: , ...}

         model.get(id) -> GET /data/model/id -> JSON
         model.put() -> PUT /data/model/id
         model.delete() -> DELETE /data/model/id

         db.collections() -> GET /data -> [collections list]

         query = collection.Query({params});
         query.fetch -> GET /data/model?params -> [ model list ]



         db.get(id) -> object
         db.put(obj)
         db.Query(
         db.find({params}) -> [object list]

       From a given data root we expect to make calls like these:

       /
    */

    exports.extend({
        'ensureSchema': ensureSchema,
    });

    var dataRoot = '/data';

    var dataInfo;

    // Returns schema if initialized, else calls callback when it is.
    function ensureSchema(callback) {
        if (dataInfo) {
            return dataInfo.schema;
        }

        $.ajax({
            url: '/data',
            success: function (result, textStatus, xmlhttp) {
                dataInfo = result;
                callback(dataInfo.schema);
            }
        });
    }
})