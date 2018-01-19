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

from flask import session

from fossir.core import signals
from fossir.modules.admin.controllers.base import RHAdminBase
from fossir.util.i18n import _
from fossir.web.flask.util import url_for
from fossir.web.menu import SideMenuSection, TopMenuItem


__all__ = ('RHAdminBase',)


@signals.menu.sections.connect_via('admin-sidemenu')
def _sidemenu_sections(sender, **kwargs):
    yield SideMenuSection('security', _("Security"), 90, icon='shield')
    yield SideMenuSection('user_management', _("User Management"), 60, icon='users')
    yield SideMenuSection('customization', _("Customization"), 50, icon='wrench')
    yield SideMenuSection('integration', _("Integration"), 30, icon='earth')
    yield SideMenuSection('homepage', _("Homepage"), 40, icon='home')


@signals.menu.items.connect_via('top-menu')
def _topmenu_items(sender, **kwargs):
    if session.user and session.user.is_admin:
        yield TopMenuItem('admin', _('Administration'), url_for('core.admin_dashboard'), 70)
