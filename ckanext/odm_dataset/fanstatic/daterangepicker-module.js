ckan.module('daterangepicker-module', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {
			console.log('daterangepicker-module init for '+ this.options.field_id);
      $('[id^='+this.options.field_id+']').each(function(){
        $(this).daterangepicker({
          format: 'MM/DD/YYYY'
        });
      });
    }
  };
});

console.log('daterangepicker-module loaded');
