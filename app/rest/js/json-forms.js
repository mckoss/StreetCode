namespace.module('startpad.json-forms', function(exports, require) {
    var jsonRest = require('startpad.json-rest');
    var types = require('org.startpad.types');

    exports.extend({
        'onFormsPage': onFormsPage,
        'onListPage': onListPage,
        'onItemPage': onItemPage
    });

    var markdown;
    var schema;
    var pageInfo;
    var currentItem;

    var controlTemplates = {
        'text': _.template(
            '<label for="<%- name %>"><%- name %>:</label>' +
            '<input type="<%- property.control %>" name="<%- name %>" id="<%- name %>" ' +
            '    value="<%- value %>"/>'),

        'textarea': _.template(
            '<label for="<%- name %>"><%- name %>:</label>' +
            '<textarea id="<%- name %>" name="<%- name %>"><%- value %></textarea>'),

        'computed': _.template('<div><%= value %></div>'),

        'reference': _.template(
            '<label for="<%- name %>"><%- name %>:</label>' +
            '<input type="text" name="<%- name %>" id="<%- name %>" ' +
            '    value="<%- value.id %> (<%- value.name %>)"/>' +
            '<div>' +
            '  Current <a href="/admin/forms/<%- property.type %>"><%- property.type %></a>: ' +
            '<a href="/admin/forms/<%- property.type %>/<%- value.id %>">' +
            '<%- value.name %></a>' +
            '</div>')
    };

    function onFormsPage() {
        if (!ensureInit(onFormsPage)) {
            return;
        }

        var schemaTemplate = _.template($('#schema-links-template').html());
        var linksHTML = ""
        for (model in schema) {
            linksHTML += schemaTemplate(schema);
        }
        $('#schema-links-body').html(linksHTML);
    }

    function onListPage() {
        if (!ensureInit(onListPage)) {
            return;
        }

        $('#list-heading').text(pageInfo.model + ' list.')
        $('#_new').click(onNew);

        var modelRowTemplate = _.template($('#model-row-template').html());
        $.ajax({
            // Override default caching since the list is likely to change frequently
            // while editing.
            url: '/data/' + pageInfo.model + '?no-cache',
            success: function (result) {
                var listHTML = ""
                for (var i = 0; i < result.length; i++) {
                    var item = result[i];
                    item.modelName = pageInfo.model;
                    if (item.name === null) {
                        item.name = '#' + item.id;
                    }
                    listHTML += modelRowTemplate(item);
                }
                $('#list-table-body').html(listHTML);
            }
        });
    }

    function onItemPage() {
        if (!ensureInit(onItemPage)) {
            return;
        }

        $('#item-form-legend').text(pageInfo.model + ' item #' + pageInfo.id);
        markdown = markdown || new Showdown.converter().makeHtml;

        $('#_save').click(onSave);
        $('#_delete').click(onDelete);

        $.ajax({
            url: '/data/' + pageInfo.model + '/' + pageInfo.id,
            success: function (result) {
                currentItem = result;
                var modelSchema = schema[pageInfo.model];
                var modelProperties = modelSchema.properties;
                var formProperties = modelSchema.formOrder || types.keys(modelProperties);

                var formHTML = "";
                for (var i = 0; i < formProperties.length; i++) {
                    var propName = formProperties[i];
                    var property = modelProperties[propName];
                    var template;
                    var data;
                    if (property) {
                        data = {name: propName,
                                property: property,
                                value: result[propName]
                                };
                    } else {
                        data = {name: 'computed',
                                property: {control: 'computed'},
                                value: computeWrapper(currentItem, propName)
                                };
                    }

                    if (data.value === null) {
                        data.value = '';
                    }

                    template = controlTemplates[data.property.control];
                    formHTML += template(data);
                }
                $('#item-form-body').append(formHTML);
            }
        });
    }

    // Initialize schema and url parsing - call callback when ready.
    function ensureInit(callback) {
        if (!schema && !(schema = jsonRest.ensureSchema(callback))) {
            return false;
        }

        pageInfo = parsePageURL();
        return true;
    }

    function computeWrapper(item, expr) {
        return eval(expr);
    }

    function onSave() {
        data = getFields();

        var computed = schema[pageInfo.model].computed;
        if (computed) {
            for (var i = 0; i < computed.length; i++) {
                computeWrapper(data, computed[i]);
            }
        }

        $.ajax({
            type: 'PUT',
            url: '/data/' + pageInfo.model + '/' + pageInfo.id,
            data: JSON.stringify(data),
            error: function (result, textStatus) {
                alert(textStatus);
            },
            success: function (result, textStatus) {
                console.log("saved");
                window.location.href = '/admin/forms/' + pageInfo.model;
            }
        });
    }

    function onDelete() {
        if (confirm("Are you sure you want to delete " +
            (currentItem.name || ('#' + currentItem.id)) + "?")) {
            $.ajax({
                type: 'DELETE',
                url: '/data/' + pageInfo.model + '/' + pageInfo.id,
                error: function (result, textStatus) {
                    alert(textStatus);
                },
                success: function (result, textStatus) {
                    window.location.href = '/admin/forms/' + pageInfo.model;
                }
            });
        }
    }

    function onNew() {
        $.ajax({
            type: 'POST',
            url: '/data/' + pageInfo.model,
            data: '{"title": "New ' + pageInfo.model + '"}',
            error: function (result, textStatus) {
                alert(textStatus);
            },
            success: function (result, textStatus) {
                window.location.href = '/admin/forms/' + pageInfo.model;
            }
        });
    }

    function getFields() {
        var fields = $('input, textarea');
        var result = {};

        for (var i = 0; i < fields.length; i++) {
            var field = fields[i];
            if (field.id[0] == '_') {
                continue;
            }
            result[field.id] = $(field).val();
        }
        return result;
    }

    // Parse /admin/forms/<model>/<id> from location
    function parsePageURL() {
        parts = window.location.pathname.split('/').slice(3)
        return {'model': parts[0],
                'id': parts[1]
               }
    }

    var qrTemplate = _.template(
        '<img src="http://chart.googleapis.com/chart?cht=qr&chs=<%= size %>x<%= size %>&' +
            'chl=<%= encURL %>">' +
        '<div><a href="<%= url %>"><%- url %></a></div>');

    function QRCode(url, size, urlDisplay) {
        if (!size) {
            size = 300;
        }
        if (!urlDisplay) {
            urlDisplay = url;
        }
        var sep = url.indexOf('?') == -1 ? '?' : '&';
        var encURL = encodeURIComponent(url + sep + 's=s');
        return qrTemplate({url: urlDisplay, encURL: encURL, size: size});
    }

});
