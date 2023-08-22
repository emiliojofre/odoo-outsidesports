odoo.define('website_product_brands.tour', function(require) {
"use strict";
  var base = require('web_editor.base');
  var core = require('web.core');
  var tour = require('web_tour.tour');
  var _t = core._t;
  var options =  {
      test: true,
      url: "/web",
      rainbowMan: false,
      wait_for: base.ready(),
  };

  var seo_steps = [tour.STEPS.MENU_MORE, {
      trigger: '.o_app[data-menu-xmlid="website.menu_website_configuration"], .oe_menu_toggler[data-menu-xmlid="website.menu_website_configuration"]',

  }, {
      trigger: '.oe_menu_leaf[data-menu-xmlid="website_product_brands.menu_product_brand_config"]',
  }, {
      trigger: '.oe_kanban_global_click',
      extra_trigger: '.o_kanban_ungrouped',

  }, {
    trigger: '.o_form_button_edit',
    extra_trigger: '.o_form_view',
  }, {
      trigger: ".o_field_many2manytags input",
      extra_trigger: ".o_form_view",
      position: "top",
      // run: "text iPad Retina Display",
  }, {
      trigger: ".ui-menu-item > a",
      auto: true,
      in_modal: false,
  }, {
   trigger: '.o_form_button_save',
   extra_trigger: '.o_form_view',
 },
  tour.STEPS.TOGGLE_APPSWITCHER,
  tour.STEPS.MENU_MORE,  {
      trigger: '.o_app[data-menu-xmlid="website.menu_website_configuration"], .oe_menu_toggler[data-menu-xmlid="website.menu_website_configuration"]',

  }, {
      trigger: '.oe_menu_leaf[data-menu-xmlid="website_sale.menu_catalog_products"]',
  }, {
      trigger: '.o_facet_remove',
  }, {
      trigger: '.o_searchview input',
      position: "top",
      // run: "text iPad Retina Display",
  }, {
      trigger: "ul.o_searchview_autocomplete > li",
  },  {
      trigger: '.o_kanban_record:eq(0)',
  }, {
      trigger: '.o_form_button_edit',
      extra_trigger: '.o_form_view',
  }, {
      trigger: 'div[name="product_brand_id"] input',
      extra_trigger: '.o_form_view',
  },
  //  {
  //     trigger: ".o_pager_next",
  //     auto: true,
  //     run: function (actions) {
  //         // actions.auto();
   //
  //         // if($(".o_pager_value").text()<=this.$anchor.find(".o_pager_limit").text()){
  //         //   // console.log(actions)
  //         //   // actions.auto(".o_pager_next");
  //         //   actions.auto();
  //         //   // while ($(".o_pager_value").text<=$(".o_pager_limit").text)
  //         //
  //         //   // actions.text("Blog content", this.$anchor.find("p"));
  //         //
  //         // }
  //         //
  //         // while ($(".o_pager_value").text()<=this.$anchor.find(".o_pager_limit").text()){
  //         //   $(".o_pager_next").click();
  //         //   // actions.auto('.o_pager_next')
  //         //   console.log('11111');
  //         //   console.log($(".o_pager_value").text(),$(".o_pager_limit").text());
  //         // }
  //         var o_pager_value = $(".o_pager_value").text();
  //         var o_pager_limit = $(".o_pager_limit").text();
  //         do{
  //             // $(".o_pager_next").click();
  //             actions.auto();
  //             console.log(o_pager_value);
  //             // console.log($(".o_pager_value").text(),$(".o_pager_limit").text());
  //             o_pager_value++;
  //         } while (o_pager_value<=o_pager_limit);
  //           console.log('dddddddddddddddddddddddddd');
  //           console.log($(".o_pager_value").text(),$(".o_pager_limit").text());
  //     },
      // id: "quotation_product_selected",
  // }
];

tour.register('brands_tour', options ,seo_steps);

});
