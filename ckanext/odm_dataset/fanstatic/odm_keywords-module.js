this.ckan.module('odm_keywords-module', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {

			console.log('odm_keywords-module init for '+ $(this.options.field_id));

			$('[id^='+this.options.field_id+']').select2({
			  tags: true,
			  tokenSeparators: [',', ' ']
			});

    }
  };
});
