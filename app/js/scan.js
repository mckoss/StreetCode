namespace.module('streetcode.scans', function (exports, requires) {
    function init() {
        Scan.template =  _.template($('#scan-template').html());
        exports.app = new ScanView();
    }

    var Scan = Backbone.Model.extend({

    });

    var ScanList = Backbone.Collection.extend({
        model: Scan,
        url: '/data/scan'
    });

    var ScanView = Backbone.View.extend({
        tagName:  "div",

        // The DOM events specific to an item.
        events: {
            'click .buy': 'buyIt'
        },

        // The ScanView listens for changes to its model, re-rendering.
        initialize: function() {
            this.model.bind('change', this.render, this);
            this.model.bind('error', this.reportError, this);
        },

        reportError: function(model, response, options) {
             var data = JSON.parse(response.responseText);
             alert(data.status || response.statusText);
        },

        // Re-render the contents of the todo item.
        render: function() {
            $(this.el).html(ScanView.template(this.model.toJSON()));
            this.setText();
            return this;
        },

        setText: function() {
            var text = this.model.get('text');
            this.$('.todo-text').text(text);
            this.input = this.$('.todo-input');
            this.input.bind('blur', _.bind(this.close, this)).val(text);
        },

        // Toggle the `"done"` state of the model.
        toggleDone: function() {
            this.model.toggle();
        },

        // Switch this view into `"editing"` mode, displaying the input field.
        edit: function() {
            $(this.el).addClass("editing");
            this.input.focus();
        },

        // Close the `"editing"` mode, saving changes to the todo.
        close: function() {
            this.model.save({text: this.input.val()});
            $(this.el).removeClass("editing");
        },

        // If you hit `enter`, we're through editing the item.
        updateOnEnter: function(e) {
            if (e.keyCode == 13) this.close();
        },

        // Remove this view from the DOM.
        remove: function() {
            $(this.el).remove();
        },

        // Remove the item, destroy the model.
        clear: function() {
            this.model.destroy();
        }

    });

    // The Application
    // ---------------

    // Our overall **AppView** is the top-level piece of UI.
    var AppView = Backbone.View.extend({

        // Instead of generating a new element, bind to the existing skeleton of
        // the App already present in the HTML.
        el: '#todoapp',

        // Delegated events for creating new items, and clearing completed ones.
        events: {
            "keypress #new-todo":  "createOnEnter",
            "keyup #new-todo":     "showTooltip",
            "click .todo-clear a": "clearCompleted"
        },

        // At initialization we bind to the relevant events on the `Scans`
        // collection, when items are added or changed. Kick things off by
        // loading any preexisting todos that might be saved in *localStorage*.
        initialize: function() {
            this.input    = this.$("#new-todo");

            Scans.bind('add',   this.addOne, this);
            Scans.bind('reset', this.addAll, this);
            Scans.bind('all',   this.render, this);

            Scans.fetch();
        },

        // Re-rendering the App just means refreshing the statistics -- the rest
        // of the app doesn't change.
        render: function() {
            this.$('#todo-stats').html(AppView.statsTemplate({
                total:      Scans.length,
                done:       Scans.done().length,
                remaining:  Scans.remaining().length
            }));
        },

        // Add a single todo item to the list by creating a view for it, and
        // appending its element to the `<ul>`.
        addOne: function(todo) {
            var view = new ScanView({model: todo});
            this.$("#todo-list").append(view.render().el);
        },

        // Add all items in the **Scans** collection at once.
        addAll: function() {
            Scans.each(this.addOne);
        },

        // If you hit return in the main input field, and there is text to save,
        // create new **Scan** model persisting it to *localStorage*.
        createOnEnter: function(e) {
            var text = this.input.val();
            if (!text || e.keyCode != 13) return;
            Scans.create({text: text});
            this.input.val('');
        },

        // Clear all done todo items, destroying their models.
        clearCompleted: function() {
            _.each(Scans.done(), function(todo){ todo.destroy(); });
            return false;
        },

        // Lazily show the tooltip that tells you to press `enter` to save
        // a new todo item, after one second.
        showTooltip: function(e) {
            var tooltip = this.$(".ui-tooltip-top");
            var val = this.input.val();
            tooltip.fadeOut();
            if (this.tooltipTimeout) clearTimeout(this.tooltipTimeout);
            if (val == '' || val == this.input.attr('placeholder')) return;
            var show = function(){ tooltip.show().fadeIn(); };
            this.tooltipTimeout = _.delay(show, 1000);
        }

    });

}); // seagtug.todos
