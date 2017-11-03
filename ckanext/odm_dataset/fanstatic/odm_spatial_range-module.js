ckan.module('odm_spatial_range-module', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {

			console.log('odm_spatial_range-module init');

			var adaptFields = function(spatialRangeField){
				var spatialRangeArray = spatialRangeField.val();
				$('.odm_spatial_range-specific').each(function(){
					$(this).find('option').each(function() {
						var countryCodes = $(this).data('country_codes');
						var countryCodesArray = countryCodes.split(",");
						var intersection = $(countryCodesArray).filter(spatialRangeArray);
						if (intersection.length===0){
							$(this).attr('disabled', 'disabled');
							console.log("hiding", $(this).val());
						}else{
							$(this).removeAttr('disabled');
							console.log("showing", $(this).val());
						}
					});
				});
			};

			adaptFields(this.el);
			$('#field-odm_spatial_range').change(function() {
				adaptFields($(this));
			});
    }
  };
});

console.log('odm_spatial_range-module loaded');
