this.ckan.module('free-multiselect-module', function($, _) {
	return {
		initialize: function() {
			console.log("free-multiselect-module " + this.options.suggestions + " " + this.options.init_value);
			console.log(this.options.suggestions);
			console.log(this.options.init_value);

			var final =  $.merge(this.options.suggestions, this.options.init_value);
			console.log(final);
			$('#field-marc21_650').select2({
				createSearchChoice: function(term, data) {
					if ($(data).filter(function() {
							return this.text.localeCompare(term) === 0;
						}).length === 0) {
						return {
							id: term,
							text: term
						};
					}
				},
				multiple: true,
				data: final
			});
		}
	}
});
