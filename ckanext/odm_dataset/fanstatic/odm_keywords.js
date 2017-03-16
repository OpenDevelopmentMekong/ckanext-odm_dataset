this.ckan.module('odm_keywords_field', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {

			$('[id^='+this.options.field_id+']').select2({
			  tags: true,
			  tokenSeparators: [',', ' ']
			});

    }
  };
});
