this.ckan.module('datepicker-module', function($, _) {
	return {
		initialize: function() {
			console.log("init datepicker-module");
			$('.datepicker').daterangepicker({
				singleDatePicker: true,
				showDropdowns: true
			});
		}
	}
});
