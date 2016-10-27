this.ckan.module('odm_spatial_range-module', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {
			$('#field-odm_spatial_range').change(function() {
				var spatialRangeArray = $(this).val();
				$('.odm_spatial_range-specific').each(function(){
					$(this).find('option').each(function() {
						var countryCodes = $(this).data('country_codes');
						var countryCodesArray = countryCodes.split(",");
						var intersection = $(countryCodesArray).filter(spatialRangeArray);
					  if (intersection.length===0){
							$(this).prop('disabled', true);
							//$(this).css('display', 'none');
							console.log("hiding", $(this).val());
						}else{
							$(this).prop('disabled', false);
							//$(this).css('display', 'inline');
							console.log("showing", $(this).val());
						}
					});
	      });
			});


    }
  };
});
