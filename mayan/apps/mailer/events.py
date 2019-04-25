from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.events import EventTypeNamespace

namespace = EventTypeNamespace(label=_('Mailing'), name='mailing')

event_email_sent = namespace.add_event_type(
    label=_('Email sent'), name='email_send'
)
