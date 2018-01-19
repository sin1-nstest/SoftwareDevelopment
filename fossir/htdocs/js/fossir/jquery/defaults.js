/* This file is part of fossir.
 * Copyright (C) 2002 - 2017 European Organization for Nuclear Research (CERN).
 *
 * fossir is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 3 of the
 * License, or (at your option) any later version.
 *
 * fossir is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with fossir; if not, see <http://www.gnu.org/licenses/>.
 */

// -----------------------------------------------------------------------------
// fossir-specific settings
// -----------------------------------------------------------------------------

$.datepicker.setDefaults({
    autoSize: true,
    buttonText: '',
    dateFormat: 'dd/mm/yy',
    firstDay: 1,
    nextText: $T('Next'),
    prevText: $T('Previous'),
    showOn: 'both'
});


$.extend(true, $.fossir.daterange.prototype.options, {
    pickerOptions: {
        dateFormat: 'dd/mm/yy'
    },
    labelAttrs: {
        class: 'label titleCellFormat'
    },
    labels: [
        $T('Choose the start date'),
        $T('Choose the end date')
    ]
});


$.fn.qtip.defaults = $.extend(true, {}, $.fn.qtip.defaults, {
    position: {
        my: 'top left',
        at: 'bottom right',
        viewport: $(window)},
    style: {
        tip: {corner: true}}
});


$.extend($.colorbox.settings, {
    opacity: 0.6
});


$.tablesorter.defaults.sortReset = true;


$.ajaxSetup({
    traditional: true,
    beforeSend: function(xhr, settings) {
        'use strict';
        if (!/^https?:.*/.test(settings.url)) {
            // Add CSRF token to local requests
            xhr.setRequestHeader('X-CSRF-Token', $('#csrf-token').attr('content'));
        }
    }
});

// Disabling autoDiscover, otherwise Dropzone will try to attach twice.
if (window.Dropzone) {
    window.Dropzone.autoDiscover = false;
}
