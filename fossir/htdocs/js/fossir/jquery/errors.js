

/* global showErrorDialog:false */

(function(global) {
    'use strict';

    global.handleAjaxError = function handleAjaxError(data) {
        if ('responseText' in data && data.readyState === 0 && data.status === 0 && !data.responseText) {
            // if data is an XHR object and we don't have any readyState, status or response text
            // the request most likely failed due to a page change so we just ignore the failure.
            // this is not 100% reliable, an interrupted connection could yield the same result.
            // since showing an error dialog in that case won't be very useful either this drawback
            // is acceptable.
            return true;
        }
        if (data.responseText) {
            // $.ajax error callback, so data is the xhr object
            try {
                data = JSON.parse(data.responseText);
            } catch (e) {
                showErrorDialog({
                    title: $T.gettext('Something went wrong'),
                    message: '{0} ({1})'.format(data.statusText.toLowerCase(), data.status),
                    suggest_login: false,
                    report_url: null
                });
                return true;
            }
        }
        // data.data.error is only needed for angular error handlers
        var error = data.error || (data.data && data.data.error);
        if (error) {
            showErrorDialog(error);
            return true;
        }
    };

    // Select the field of an i-form which has an error and display the tooltip.
    global.showFormErrors = function showFormErrors(context) {
        context = context || $('body');
        context.find(".i-form .has-error > .form-field, .i-form .has-error > .form-subfield").each(function() {
            var $this = $(this);
            // Try a custom tooltip anchor
            var input = $this.find('[data-tooltip-anchor]');

            if (!input.length) {
                // Try the first non-hidden input field
                input = $this.children(':input:not(:hidden)').eq(0);
            }

            if (!input.length) {
                // Try the first element that's not a hidden input
                input = $this.children(':not(:input:hidden)').eq(0);
            }
            input.stickyTooltip('danger', function() {
                return $this.data('error');
            });
        });
    };
})(window);
