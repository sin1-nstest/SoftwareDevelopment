.

from __future__ import unicode_literals

from fossir.modules.events.papers.models.competences import PaperCompetence
from fossir.modules.events.papers.models.reviews import PaperReviewType
from fossir.modules.events.papers.settings import PaperReviewingRole, paper_reviewing_settings
from fossir.modules.events.settings import EventSettingProperty
from fossir.util.caching import memoize_request
from fossir.util.date_time import now_utc
from fossir.util.string import MarkdownText, return_ascii


class CallForPapers(object):
    """Proxy class to facilitate access to the call for papers settings"""

    def __init__(self, event):
        self.event = event

    @return_ascii
    def __repr__(self):
        return '<CallForPapers({}, start_dt={}, end_dt={})>'.format(self.event.id, self.start_dt, self.end_dt)

    start_dt = EventSettingProperty(paper_reviewing_settings, 'start_dt')
    end_dt = EventSettingProperty(paper_reviewing_settings, 'end_dt')
    content_reviewing_enabled = EventSettingProperty(paper_reviewing_settings, 'content_reviewing_enabled')
    layout_reviewing_enabled = EventSettingProperty(paper_reviewing_settings, 'layout_reviewing_enabled')
    judge_deadline = EventSettingProperty(paper_reviewing_settings, 'judge_deadline')
    layout_reviewer_deadline = EventSettingProperty(paper_reviewing_settings, 'layout_reviewer_deadline')
    content_reviewer_deadline = EventSettingProperty(paper_reviewing_settings, 'content_reviewer_deadline')

    @property
    def has_started(self):
        return self.start_dt is not None and self.start_dt <= now_utc()

    @property
    def has_ended(self):
        return self.end_dt is not None and self.end_dt <= now_utc()

    @property
    def is_open(self):
        return self.has_started and not self.has_ended

    def schedule(self, start_dt, end_dt):
        paper_reviewing_settings.set_multi(self.event, {
            'start_dt': start_dt,
            'end_dt': end_dt
        })

    def open(self):
        if self.has_ended:
            paper_reviewing_settings.set(self.event, 'end_dt', None)
        else:
            paper_reviewing_settings.set(self.event, 'start_dt', now_utc(False))

    def close(self):
        paper_reviewing_settings.set(self.event, 'end_dt', now_utc(False))

    def set_reviewing_state(self, reviewing_type, enable):
        if reviewing_type == PaperReviewType.content:
            self.content_reviewing_enabled = enable
        elif reviewing_type == PaperReviewType.layout:
            self.layout_reviewing_enabled = enable
        else:
            raise ValueError('Invalid reviewing type: {}'.format(reviewing_type))

    def get_reviewing_state(self, reviewing_type):
        if reviewing_type == PaperReviewType.content:
            return self.content_reviewing_enabled
        elif reviewing_type == PaperReviewType.layout:
            return self.layout_reviewing_enabled
        else:
            raise ValueError('Invalid reviewing type: {}'.format(reviewing_type))

    @property
    def managers(self):
        return {p.principal for p in self.event.acl_entries if p.has_management_role('paper_manager', explicit=True)}

    @property
    def judges(self):
        return {p.principal for p in self.event.acl_entries if p.has_management_role('paper_judge', explicit=True)}

    @property
    def content_reviewers(self):
        return {p.principal for p in self.event.acl_entries
                if p.has_management_role('paper_content_reviewer', explicit=True)}

    @property
    def layout_reviewers(self):
        return {p.principal for p in self.event.acl_entries
                if p.has_management_role('paper_layout_reviewer', explicit=True)}

    @property
    def content_review_questions(self):
        return [q for q in self.event.paper_review_questions if q.type == PaperReviewType.content]

    @property
    def layout_review_questions(self):
        return [q for q in self.event.paper_review_questions if q.type == PaperReviewType.layout]

    @property
    def assignees(self):
        users = set(self.judges)
        if self.content_reviewing_enabled:
            users |= self.content_reviewers
        if self.layout_reviewing_enabled:
            users |= self.layout_reviewers
        return users

    @property
    @memoize_request
    def user_competences(self):
        user_ids = {user.id for user in self.event.cfp.assignees}
        user_competences = (PaperCompetence.query.with_parent(self.event)
                            .filter(PaperCompetence.user_id.in_(user_ids))
                            .all())
        return {competences.user_id: competences for competences in user_competences}

    @property
    def announcement(self):
        return MarkdownText(paper_reviewing_settings.get(self.event, 'announcement'))

    def get_questions_for_review_type(self, review_type):
        return (self.content_review_questions
                if review_type == PaperReviewType.content
                else self.layout_review_questions)

    @property
    def rating_range(self):
        return tuple(paper_reviewing_settings.get(self.event, key) for key in ('scale_lower', 'scale_upper'))

    def is_staff(self, user):
        return self.is_manager(user) or self.is_judge(user) or self.is_reviewer(user)

    def is_manager(self, user):
        return self.event.can_manage(user, role='paper_manager')

    def is_judge(self, user):
        return self.event.can_manage(user, role='paper_judge', explicit_role=True)

    def is_reviewer(self, user, role=None):
        if role:
            enabled = {
                PaperReviewingRole.content_reviewer: self.content_reviewing_enabled,
                PaperReviewingRole.layout_reviewer: self.layout_reviewing_enabled,
            }
            return enabled[role] and self.event.can_manage(user, role=role.acl_role, explicit_role=True)
        else:
            return (self.is_reviewer(user, PaperReviewingRole.content_reviewer) or
                    self.is_reviewer(user, PaperReviewingRole.layout_reviewer))

    def can_access_reviewing_area(self, user):
        return self.is_staff(user)

    def can_access_judging_area(self, user):
        return self.is_manager(user) or self.is_judge(user)
