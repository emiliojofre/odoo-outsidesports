/** @odoo-module **/
import { WebsiteSale } from 'website_sale.website_sale';

WebsiteSale.include({
    template: "addval_website_address.address_custom",
    events: Object.assign(WebsiteSale.prototype.events, {
        'change select[name="state_id"]': '_onChangeState',
    }),

    /**
    * @private
    */
    _noSelector: function () {
    },
    /**
    * @private
    */
    _changeState: function () {
        let country_id = $("#country_id").val();
        let state_id = $("#state_id").val();
        if (country_id === undefined || country_id === null || country_id === "") {
            var selector = $("select[name='city']");
            var input = $("input[name='city']");
            selector.get(0).setAttribute('style', 'display:none');
            selector.get(0).setAttribute('disabled', 'disabled');
            input.get(0).setAttribute('style', 'display:block');
            input.get(0).removeAttribute('disabled');
            return;
        }
        if (state_id === undefined || state_id === null || state_id === "") {
            var selector = $("select[name='city']");
            var input = $("input[name='city']");
            selector.get(0).setAttribute('style', 'display:none');
            selector.get(0).setAttribute('disabled', 'disabled');
            input.get(0).setAttribute('style', 'display:block');
            input.get(0).removeAttribute('disabled');
            return;
        }
        this._rpc({
            route: "/shop/state_infos/" + country_id + "/" + state_id,
        }).then(function (data) {
            if (!data.in_country) {
                var selector = $("select[name='city']");
                var input = $("input[name='city']");
                selector.get(0).setAttribute('style', 'display:none');
                selector.get(0).setAttribute('disabled', 'disabled');
                input.get(0).setAttribute('style', 'display:block');
                input.get(0).removeAttribute('disabled');
                return;
            }
            var selector = $("select[name='city']");
            var input = $("input[name='city']");
            if (!data.use_selector) {
                selector.get(0).setAttribute('style', 'display:none');
                selector.get(0).setAttribute('disabled', 'disabled');
                input.get(0).setAttribute('style', 'display:block');
                input.get(0).removeAttribute('disabled');
                return;
            }
            // populate cities and display
            var selectCities = $("select[name='city']");
            selectCities.html('');
            _.each(data.cities, function (x) {
                var opt = $('<option>').text(x.name)
                    .attr('value', x.id);
                selectCities.append(opt);
            });
            input.get(0).setAttribute('style', 'display:none');
            input.get(0).setAttribute('disabled', 'disabled');
            selector.get(0).setAttribute('style', 'display:block');
            selector.get(0).removeAttribute('disabled');
        }).catch((error) => {
            console.log(error);
        });
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onChangeState: function (ev) {
        if (!this.$('.checkout_autoformat').length) {
            return;
        }
        this._changeState();
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onChangeCountry: function (ev) {
        this._super.apply(this, arguments)
        this._rpc({
            route: "/shop/country_infos/" + $("#country_id").val(),
            params: {
                mode: $("#country_id").attr('mode'),
            },
        }).then(function (data) {
            var selectStates = $("select[name='state_id']");
            if (data.states.length || data.state_required) {
                selectStates.html('');
                _.each(data.states, function (x) {
                    var opt = $('<option>').text(x[1])
                        .attr('value', x[0])
                        .attr('data-code', x[2]);
                    selectStates.append(opt);
                });
                selectStates.parent('div').show();
            } else {
                selectStates.val('').parent('div').hide();
            }
        }).then(() => {
            this._changeState()
        });

    },
});