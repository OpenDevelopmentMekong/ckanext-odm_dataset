this.ckan.module('odm_keywords-module', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {

			console.log('odm_keywords-module init');

			$('[id^='+this.options.field_id+']').each(function(){
				$(this).select2({
				  tags: true,
				  tokenSeparators: [',', ' ']
				});
			});

    }
  };
});
