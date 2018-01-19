# This file is part of fossir.
# Copyright (C) 2002 - 2017 European Organization for Nuclear Research (CERN).
#
# fossir is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# fossir is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fossir; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from flask import render_template

from fossir.core.notifications import email_sender, make_email


@email_sender
def notify_amount_inconsistency(registration, amount, currency):
    event = registration.registration_form.event
    to = event.creator.email
    body = render_template('events/payment/emails/payment_inconsistency_email_to_manager.txt',
                           event=event, registration=registration, amount=amount, currency=currency)
    return make_email(to, subject='Payment inconsistency', body=body)
