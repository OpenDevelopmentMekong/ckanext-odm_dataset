this.ckan.module('odm_spatial_range-module', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {

			var adaptFields = function(spatialRangeField){
				var spatialRangeArray = spatialRangeField.val();
				$('.odm_spatial_range-specific').each(function(){
					$(this).find('option').each(function() {
						var countryCodes = $(this).data('country_codes');
						var countryCodesArray = countryCodes.split(",");
						var intersection = $(countryCodesArray).filter(spatialRangeArray);
						if (intersection.length===0){
							$(this).attr('disabled', 'disabled');
							//$(this).css('display', 'none');
							console.log("hiding", $(this).val());
						}else{
							$(this).removeAttr('disabled');
							//$(this).css('display', 'inline');
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
