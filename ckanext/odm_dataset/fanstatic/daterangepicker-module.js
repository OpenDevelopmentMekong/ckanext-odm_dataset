this.ckan.module('daterangepicker-module', function($, _) {
	return {
		initialize: function() {
			console.log("init daterangepicker-module");
			$('.daterangepicker').daterangepicker();

      $('.daterangepicker').on('apply.daterangepicker', function(ev, picker) {
    		console.log(picker);
    	});
		}
	};

});
