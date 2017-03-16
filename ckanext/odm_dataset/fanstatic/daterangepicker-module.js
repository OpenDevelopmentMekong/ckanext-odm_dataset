this.ckan.module('daterangepicker-module', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {
      $('[id^='+this.options.field_id+']').each(function(){
      	console.log('daterangepicker-module init for '+ $(this.options.field_id));
        $(this).daterangepicker({
          format: 'MM/DD/YYYY'
        });
      });
    }
  };
});
