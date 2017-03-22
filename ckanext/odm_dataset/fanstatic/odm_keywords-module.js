this.ckan.module('odm_keywords-module', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {

			console.log('odm_keywords-module init');

			this.el.select2({
				tags: true,
				tokenSeparators: [",", "\t", "\n"]
			});

    }
  };
});
