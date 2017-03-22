function initMultiSelect(tSel) {
  tSel.select2('destroy');
  tSel.select2({
      tags: true,
      tokenSeparators: [',', ';'],
      dropdownCss: {display:'none'}
  });

  //manual add new values by Enter
  (function (t) {
      $('#s2id_' + t.attr('id')).on('keyup', function(e) {
          if(e.keyCode === 13 || e.keyCode === 9){
              //add new value
              t.val(t.val() + ',' + $('#s2id_' + t.attr('id') + ' input ').val());

              //refresh select2
              initMultiSelect(t);

              //get focus to select2 last position
              t.select2("close");
              t.select2("open");
          }
      });
  })(tSel);
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
