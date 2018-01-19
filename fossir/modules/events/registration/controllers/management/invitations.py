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

from flask import flash, request
from sqlalchemy.orm import joinedload

from fossir.core.db import db
from fossir.modules.events.registration.controllers.management import RHManageRegFormBase
from fossir.modules.events.registration.forms import InvitationFormExisting, InvitationFormNew
from fossir.modules.events.registration.models.invitations import InvitationState, RegistrationInvitation
from fossir.modules.events.registration.notifications import notify_invitation
from fossir.modules.events.registration.views import WPManageRegistration
from fossir.util.i18n import ngettext
from fossir.web.flask.templating import get_template_module
from fossir.web.forms.base import FormDefaults
from fossir.web.util import jsonify_data, jsonify_template


def _query_invitation_list(regform):
    return (RegistrationInvitation.query
            .with_parent(regform)
            .options(joinedload('registration'))
            .order_by(db.func.lower(RegistrationInvitation.first_name),
                      db.func.lower(RegistrationInvitation.last_name),
                      RegistrationInvitation.id)
            .all())


def _render_invitation_list(regform):
    tpl = get_template_module('events/registration/management/_invitation_list.html')
    return tpl.render_invitation_list(_query_invitation_list(regform))


class RHRegistrationFormInvitations(RHManageRegFormBase):
    """Overview of all registration invitations"""

    def _process(self):
        invitations = _query_invitation_list(self.regform)
        return WPManageRegistration.render_template('management/regform_invitations.html', self.event,
                                                    regform=self.regform, invitations=invitations)


class RHRegistrationFormInvite(RHManageRegFormBase):
    """Invite someone to register"""

    NOT_SANITIZED_FIELDS = {'email_from'}

    def _create_invitation(self, user, skip_moderation, email_from, email_subject, email_body):
        invitation = RegistrationInvitation(
            skip_moderation=skip_moderation,
            email=user['email'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            affiliation=user['affiliation']
        )
        self.regform.invitations.append(invitation)
        db.session.flush()
        notify_invitation(invitation, email_subject, email_body, email_from)

    def _process(self):
        tpl = get_template_module('events/registration/emails/invitation_default.html', event=self.event)
        form_cls = InvitationFormExisting if request.args.get('existing') == '1' else InvitationFormNew
        defaults = FormDefaults(email_body=tpl.get_html_body(), email_subject=tpl.get_subject())
        form = form_cls(obj=defaults, regform=self.regform)
        skip_moderation = form.skip_moderation.data if 'skip_moderation' in form else False
        if form.validate_on_submit():
            for user in form.users.data:
                self._create_invitation(user, skip_moderation, form.email_from.data,
                                        form.email_subject.data, form.email_body.data)
            num = len(form.users.data)
            flash(ngettext("The invitation has been sent.",
                           "{n} invitations have been sent.",
                           num).format(n=num), 'success')
            return jsonify_data(invitation_list=_render_invitation_list(self.regform))
        return jsonify_template('events/registration/management/regform_invite.html', regform=self.regform, form=form)


class RHRegistrationFormInvitationBase(RHManageRegFormBase):
    """Base class for RH working on one invitation."""

    normalize_url_spec = {
        'locators': {
            lambda self: self.invitation
        }
    }

    def _process_args(self):
        RHManageRegFormBase._process_args(self)
        self.invitation = RegistrationInvitation.get_one(request.view_args['invitation_id'])


class RHRegistrationFormDeleteInvitation(RHRegistrationFormInvitationBase):
    """Delete a registration invitation"""

    def _process(self):
        db.session.delete(self.invitation)
        return jsonify_data(invitation_list=_render_invitation_list(self.regform))


class RHRegistrationFormManagerDeclineInvitation(RHRegistrationFormInvitationBase):
    """Mark a registration is declined by the invitee."""

    def _process(self):
        if self.invitation.state == InvitationState.pending:
            self.invitation.state = InvitationState.declined
            db.session.flush()
        return jsonify_data(invitation_list=_render_invitation_list(self.regform))
