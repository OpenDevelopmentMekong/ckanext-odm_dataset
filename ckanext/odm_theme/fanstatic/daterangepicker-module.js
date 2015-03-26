this.ckan.module('datepicker-module', function($, _) {
	return {
		initialize: function() {

			$('input[class="odm_datepicker"]').daterangepicker({
					singleDatePicker: true,
					showDropdowns: true
				});
		}
	}
});

this.ckan.module('daterangepicker-module', function($, _) {
	return {
		initialize: function() {

      $('input[class="odm_daterangepicker"]').daterangepicker();

		}
	}
});
