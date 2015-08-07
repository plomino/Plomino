require([
    'jquery',
    'mockup-patterns-base'
], function($, Base) {
    'use strict';
    var Table = Base.extend({
        name: 'plominotable',
        trigger: '.plomino-table',
        defaults: {},
        init: function() {
            var self = this;
            self.init_search();
            self.refresh({});
        },
        refresh: function(options) {
            var self = this;
            if(self.options.source) {
                $.get(self.options.source, options, function(data) {
                    self.$el.find('tr:not(.header-row)').remove();
                    for(var i=0; i<data.rows.length; i++) {
                        var row = data.rows[i];
                        var html = '<tr><td><a href="'
                            + self.options.source
                            + '../../document/' + row[0]
                            + '">' + row[1]
                            + '</a></td>';
                        if(row.length > 2) {
                            for(var j=2; j<row.length; j++) {
                                html += '<td>' + row[j] + '</td>';
                            }
                        }
                        html += '</tr>';
                        self.$el.append(html);
                    }
                });
            }
        },
        init_search: function() {
            var self = this;
            var search = $('<form id="plomino-search"><input type="text" /></form>');
            self.$el.before(search);
            search.on('submit', function() {return false;});
            var wait;
            var filtered = false;
            search.on('keyup', function() {
                var query = $('#plomino-search input').val();
                if(query.length < 3 && !filtered) {
                    return;
                } 
                if(wait) {
                    clearTimeout(wait);
                }
                wait = setTimeout(function() {
                    self.refresh({search: query});
                    if(query) {
                        filtered = true;
                    } else {
                        filtered = false;
                    }
                    clearTimeout(wait);
                }, 1000);
            });
        }
    });
    return Table;
});