require([
    'jquery',
    'pat-base'
], function($, Base) {
    'use strict';
    var Table = Base.extend({
        name: 'plominotable',
        parser: 'mockup',
        trigger: '.plomino-table',
        defaults: {},
        init: function() {
            var self = this;
            self.init_search();
            self.init_sorting();
            self.refresh({});
            self.params = {};
        },
        refresh: function() {
            var self = this;
            if(self.options.source) {
                self.$el.find('tr:not(.header-row)').remove();
                var counter = self.$el.find('tr.header-row.count')
                counter.find('td').text('Loading...');
                $.get(self.options.source, self.params, function(data) {
                    var html = '';
                    for(var i=0; i<data.rows.length; i++) {
                        var row = data.rows[i];
                        html += '<tr><td><a href="'
                            + self.options.source
                            + '/../../document/' + row[0]
                            + '">' + row[1]
                            + '</a></td>';
                        if(row.length > 2) {
                            for(var j=2; j<row.length; j++) {
                                html += '<td>' + row[j] + '</td>';
                            }
                        }
                        html += '</tr>';
                    }
                    if(data.rows.length > 1) {
                        counter.find('td').text(data.rows.length + ' documents');
                    } else {
                        counter.find('td').text(data.rows.length + ' document');
                    }
                    counter.before(html);
                });
            }
        },
        init_search: function() {
            var self = this;
            var search = $('<form id="plomino-search"><input type="text" placeholder="Search"/></form>');
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
                    self.params.search = query;
                    self.refresh();
                    if(query) {
                        filtered = true;
                    } else {
                        filtered = false;
                    }
                    clearTimeout(wait);
                }, 1000);
            });
        },
        init_sorting: function() {
            var self = this;
            self.$el.find('th').on('click', function() {
                self.$el.find('th').removeClass('icon-down-dir icon-up-dir');
                var sort_on = $(this).attr('data-column');
                if(sort_on == self.params.sorton) {
                    self.params.reverse = (self.params.reverse==1) ? 0 : 1;
                } else {
                    self.params.sorton = sort_on;
                    self.params.reverse = 0;
                }
                if (self.params.reverse === 0) {
                    $(this).addClass('icon-down-dir');
                } else {
                    $(this).addClass('icon-up-dir');
                }
                self.refresh();
            });
        }
    });
    return Table;
});