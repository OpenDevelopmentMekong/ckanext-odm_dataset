this.ckan.module('datepicker-module', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {
			console.log('datepicker-module init for '+ this.options.field_id);
      $('[id^='+this.options.field_id+']').each(function(){
        $(this).daterangepicker({
           singleDatePicker: true,
           showDropdowns: true,
           format: 'MM/DD/YYYY'
         });
      });
    }
  };
});
