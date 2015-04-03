this.ckan.module('multiselect-module-languages', function($, _) {
  return {
    initialize: function() {
      console.log("multiselect-module-languages " + this.options.suggestions);
      console.log($(this).find('input'));

      $('#field-odm_language').select2({
        multiple: true,
        data: this.options.suggestions
      });
    }
  }
});

this.ckan.module('multiselect-module-countries', function($, _) {
  return {
    initialize: function() {
      console.log("multiselect-module-countries " + this.options.suggestions);
      console.log(this.options.suggestions);

      $('#field-odm_spatial_range').select2({
        multiple: true,
        data: this.options.suggestions
      });
    }
  }
});

this.ckan.module('free-multiselect-module', function($, _) {
  return {
    initialize: function() {
      console.log("free-multiselect-module " + this.options.suggestions + " " + this.options.init_value);

      var final =  $.merge(this.options.suggestions, this.options.init_value);

      $('#field-marc21_650').select2({
        createSearchChoice: function(term, data) {
          if ($(data).filter(function() {
              return this.text.localeCompare(term) === 0;
            }).length === 0) {
            return {
              id: term,
              text: term
            };
          }
        },
        multiple: true,
        data: final
      });
    }
  }
});
