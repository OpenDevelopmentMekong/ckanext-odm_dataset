this.ckan.module('datepicker-module', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {
      $('[id^='+this.options.field_id+']').each(function(){
      	console.log('datepicker-module init for '+ $(this));
        $(this).daterangepicker({
           singleDatePicker: true,
           showDropdowns: true,
           format: 'DD/MM/YYYY'
         });
      });
    }
  };
});
