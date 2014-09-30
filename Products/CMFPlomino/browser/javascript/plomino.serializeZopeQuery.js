(function( $ ) {
  $.fn.serializeZopeQuery = function() {
    var query = {};
    var form = this;
    /* Checkboxes become arrays (Zope by default ORs them) */

    this.find('input[type=checkbox]').each(function(){
        
        if (this.checked) {
            query[this.name] = query[this.name] || [];
            query[this.name].push(this.value);
        }
    });
    /* selects that don't have the selectop class become equality query */
    this.find('select:not([class~=selectop])').each(function(){
        if (this.value !== '') {
            query[this.name] = this.value;
        }
    });
    this.find('input[type=text]').each(function(){
        var fieldType = $(this).attr('data-searchtype');
        converter = function(val,type) {
            
            switch(type){
                case 'date':
                    // We have dates in Italian format: dd/mm/YYYY
                    // So we reverse the values to be ISO 8601 compliant 
                    return val.split('/').reverse().join('/');
                default:
                    return val;
            }
        }

        var name = this.name;
        var operator = form.find('#' + name + '_op');
        if (!$(this).val() && !operator.length) {
            query[this.name] = this.value;
        } else if (operator.length && $(this).val()) {
            var option = operator.find(':checked').attr('value');
            var fields = form.find('[name=' + name + ']');
            var value = converter(fields.attr('value'),fieldType);
            if (option) {
                /* Switch-like construct: an object with strings as keys and
                   functions as values is used to choose the right function to call */
                if (!value) {return;} /* don't include in the query valueless stanzas */
                ({
                    'eq': function() { /* less than value: value is max */
                        query[name] = (fieldType=='number')?(parseFloat(value)):(value);
                    },
                    'in': function() { /* less than value: value is max */
                        query[name] = ' *' + value +'*' ;
                    },
                    'wi': function() {
                        /* In this case we have two fields with the same name
                           The first represents 'min', the second 'max'
                           We must take care of the fact that this function will be called
                           twice: once for each field. We make sure it's idempotent. */
                        to = converter(fields[1].value,fieldType); /* value holds the first; we need the second */
                        query[name] = {'query': [(fieldType=='number')?(parseFloat(value)):(value), (fieldType=='number')?(parseFloat(to)):(to)], 'range':'min:max'};
                    }, 'lt': function() { /* less than value: value is max */
                        query[name] = {'query': (fieldType=='number')?(parseFloat(value)):(value), 'range':'max'};
                    }, 'gt': function() { /* greater than value: value is min */
                        query[name] = {'query': (fieldType=='number')?(parseFloat(value)):(value), 'range':'min'};
                    }
                })[option](); // We select the right function and call it.
            } else if (value) {
                /* The operator has an empty name. This meas equality is implied */
                query[name] = value;
            }
        }
    });

    /*Ricerca di campi tipo nascosto*/
    this.find('input[type=hidden]').each(function(){

        if (jQuery(this).val()){
            var name = this.name;
            var static_query=jQuery.parseJSON((jQuery(this).val()));
            query = jQuery.extend(query,static_query);
        }
    });
    return query;
    //return JSON.stringify(query);
  };
})( jQuery );