this.ckan.module('daterangepicker-module', function($, _) {
	return {
    options: {
      format: 'dd/mm/yyyy',
      id: ''
    },
		initialize: function() {
      $('[id^='+this.options.field_id+']').each(function(){
      	console.log('daterangepicker-module init for '+ $(this));
        $(this).daterangepicker({
          format: 'DD/MM/YYYY'
        });
      });
    }
  };
});
