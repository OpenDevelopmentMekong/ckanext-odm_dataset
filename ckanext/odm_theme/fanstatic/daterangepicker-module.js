this.ckan.module('datepicker-module', function($, _) {
  return {
    initialize: function() {

      $(this).find('input').daterangepicker({
          singleDatePicker: true,
          showDropdowns: true
        });
    }
  }
});

this.ckan.module('daterangepicker-module', function($, _) {
  return {
    initialize: function() {

      $(this).find('input').daterangepicker();

    }
  }
});
