"use strict";


/* odm_theme_review_system_logic
 *
 * Review System Logic
 *
 * This Javascript modules extends the functionalities provided by
 * the CKAN base module dataset-visibility.js which was originally
 * referenced in the package_basic_fields.html snippet (The one which
 * generates the form to create/edit datasets)
 *
 * The additional lines of code aim to implement following Issue:
 * https://github.com/OpenDevelopmentMekong/ckanext-odm_theme/issues/1
 *
 * Import in templates using
 * {% resource 'odm_theme/odm_theme_review_system_logic.js' %}
 *
 */

ckan.module('odm_theme_review_system_logic', function ($, _) {

  return {

    currentValue: false,
    options: {
      organizations: $('#field-organizations'),
      visibility: $('#field-private'),
      visibility_backup: $('#field-private').clone(),
      currentValue: null,
      user_id: null,
      owner_org: null,
      debug: false
    },

    initialize: function () {

      if (this.options.debug) console.log("odm_theme_review_system_logic initialized for element: ", this.el, this.options.owner_org);

      $.proxyAll(this, /_on/);
      this.options.currentValue = this.options.visibility.val();
      this.options.organizations.on('change', this._onOrganizationChange);
      this._onOrganizationChange();

      // In case owner_org is initialized, we won't wait for _onOrganizationChange
      // we call member_list directly
      if (this.options.owner_org){
        var params = { 'id': this.options.owner_org, 'object_type': 'user', 'capacity': 'admin' };
        this.sandbox.client.call('POST', 'member_list', params, this._onDone);
      }

    },

    _onOrganizationChange: function() {

      this.options.user_id = $('.account').attr('data-me');
      var orgaInTheList = this.options.organizations.val();

      if (this.options.debug) console.log("odm_theme_review_system_logic _onOrganizationChange: " + orgaInTheList + " " + this.options.user_id);

      // If there is any organisation on the list (the user belongs to it)
      if (orgaInTheList) {

        // Call the API to check whether the user has Admin role in the orga
        var params = { 'id': orgaInTheList, 'object_type': 'user', 'capacity': 'admin' };
        this.sandbox.client.call('POST', 'member_list', params, this._onDone);

      } else {

        // if not in the list, just disable and set to Private (this should not happen since all user must belong to an orga)
        this._removePublicOption();

      }

    },

    _onDone: function(response) {

      var debug = this.options.debug;
      var user_id = this.options.user_id;
      var showPublicOption = false;

      if (response.success){

        // we need to extract the ids of the admins found
        var result = response.result;

        result.map( function(member) {

          // if the user is on the list it means it is admin for that orga
          if (member[0] == user_id){

            showPublicOption = true;

          }

        })

      }

      if (showPublicOption){

        if (debug) console.log("Member is an admin, restore <select>");

        this._resetAllOptions();

      }else{

        if (debug) console.log("Member is not an admin, hiding Public option");

        this._removePublicOption();

      }
    },

    _removePublicOption: function() {

      this.options.visibility.find('option').filter(function () {
        return $(this).val() === 'False';
      }).remove();

      // Do not disable field.
      //this.options.visibility.prop('disabled', true);

      //Show disclaimer
      $("#field-private-disclaimer").show();

    },

    _resetAllOptions: function(){

      var debug = this.options.debug;

      if (debug) console.log("Resetting #field-private-container",this.options.visibility_backup);

      this.options.visibility = this.options.visibility_backup.clone();

      $('#field-private').replaceWith(this.options.visibility);

      //Hide disclaimer
      $("#field-private-disclaimer").hide();
    }

  };

});
