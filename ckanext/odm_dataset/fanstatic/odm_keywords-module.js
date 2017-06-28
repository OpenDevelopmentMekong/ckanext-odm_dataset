function initMultiSelect(tSel) {

	tSel.select2('destroy');
  tSel.select2({
      tags: true,
      tokenSeparators: null,
			maximumSelectionLength: 5,
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
		  ajax: {
		    url: 'https://solr.opendevelopmentmekong.net/solr/collection1/select?q=*%3A*&fq=extras_odm_keywords%3A*&wt=json&indent=true&facet=true&facet.field=extras_odm_keywords',
		    dataType: "json",
		    data: function(term, page) {
		      return {
		        q: term
		      };
		    },
		    results: function(data, page) {
					var suggestions;
			    if (data.facet_counts){
			      suggestions = data.facet_counts.facet_fields.extras_odm_keywords;
			    }

			    var string_suggestions = [];
			    for (var index in suggestions){
			      if (typeof suggestions[index] === 'string'){
			        string_suggestions.push({
			          "id": suggestions[index],
			          "text": suggestions[index]
			        });
			      }
			    }

		      return {
		        results: string_suggestions
		      };
		    }
	  },
    initSelection: function (element, callback) {
      var data = [];

      function splitVal(string, separator) {
        var val, i, l;
        if (string === null || string.length < 1) return [];
        val = string.split(separator);
        for (i = 0, l = val.length; i < l; i = i + 1) val[i] = $.trim(val[i]);
        return val;
      }

      $(splitVal(element.val(), ",")).each(function () {
        data.push({
          id: this,
          text: this
        });
      });

      callback(data);
    }
  });

	tSel.on("select2-selecting", function (evt) {
		console.log(evt);
	  var element = evt.params.data.element;
	  var $element = $(element);

		var enteredTaxonomies = $('#field-taxonomy').val();
		var enteredTaxonomiesLowerCase = enteredTaxonomies.map(function(term) {
			 return term.toLowerCase();
		});

		if (enteredTaxonomiesLowerCase.indexOf($element.toLowerCase()) > -1){
			alert("keyword " +  $element + " has been already entered on the topic field.");
		}else{

		  $element.detach();
		  $(this).append($element);
		  $(this).trigger("change");

		}
	});

}
this.ckan.module('odm_keywords-module', function($, _) {
	return {
    options: {
      id: ''
    },
		initialize: function() {

			console.log('odm_keywords-module init');

			initMultiSelect(this.el);

    }
  };
});
