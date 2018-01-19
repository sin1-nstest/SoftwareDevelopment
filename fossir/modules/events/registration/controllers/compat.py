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

from flask import current_app, redirect, request

from fossir.modules.events.registration.models.legacy_mapping import LegacyRegistrationMapping
from fossir.web.flask.util import url_for
from fossir.web.rh import RHSimple


@RHSimple.wrap_function
def compat_registration(event_id, path=None):
    url = url_for('event_registration.display_regform_list', confId=event_id)
    try:
        registrant_id = int(request.args['registrantId'])
        authkey = request.args['authkey']
    except KeyError:
        pass
    else:
        mapping = (LegacyRegistrationMapping
                   .find(event_id=event_id, legacy_registrant_id=registrant_id, legacy_registrant_key=authkey)
                   .first())
        if mapping:
            url = url_for('event_registration.display_regform', mapping.registration.locator.registrant)
    return redirect(url, 302 if current_app.debug else 301)
