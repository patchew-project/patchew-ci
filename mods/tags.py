#!/usr/bin/env python3
#
# Copyright 2016 Red Hat, Inc.
#
# Authors:
#     Fam Zheng <famz@redhat.com>
#
# This work is licensed under the MIT License.  Please see the LICENSE file or
# http://opensource.org/licenses/MIT.

from mod import PatchewModule
from mbox import parse_address
from django.http import HttpResponse, Http404
from event import register_handler, emit_event, declare_event
from api.models import Message
from api.rest import PluginMethodField
from patchew.tags import lines_iter
import re
import www.views

REV_BY_PREFIX = "Reviewed-by:"
BASED_ON_PREFIX = "Based-on:"

_default_config = """
[default]
tags = Tested-by, Reported-by, Acked-by, Suggested-by

"""

BUILT_IN_TAGS = [REV_BY_PREFIX, BASED_ON_PREFIX]

_instance = None

# This is monkey-patched into www.views
def _view_series_mbox_patches(request, project, message_id):
    global _instance
    s = Message.objects.find_series(message_id, project)
    if not s:
        raise Http404("Series not found")
    if not s.is_complete:
        raise Http404("Series not complete")
    mbox = "\n".join(["From %s %s\n" % (x.get_sender_addr(), x.get_asctime()) + \
                      _instance.get_mbox_with_tags(x) for x in s.get_patches()])
    return HttpResponse(mbox, content_type="text/plain")
www.views.view_series_mbox_patches = _view_series_mbox_patches

class SeriesTagsModule(PatchewModule):
    """

Documentation
-------------

This module is configured in "INI" style.

It has only one section named `[default]`. The only supported option is tags:

    [default]
    tags = Reviewed-by, Tested-by, Reported-by, Acked-by, Suggested-by

The `tags` option contains the tag line prefixes (must be followed by colon)
that should be treated as meaningful patch status tags, and picked up from
series cover letter, patch mail body and their replies.

"""
    name = "tags"
    default_config = _default_config

    def __init__(self):
        global _instance
        assert _instance == None
        _instance = self
        register_handler("MessageAdded", self.on_message_added)
        declare_event("TagsUpdate", series="message object that is updated")

        # XXX: get this list through module config?
    def get_tag_prefixes(self):
        tagsconfig = self.get_config("default", "tags", default="")
        return set([x.strip() for x in tagsconfig.split(",") if x.strip()] + BUILT_IN_TAGS)

    def get_tag_regex(self):
        tags = self.get_tag_prefixes()
        tags_re = '|'.join(map(re.escape, tags))
        return re.compile('^(?i:%s):' % tags_re)

    def update_tags(self, s):
        old = s.get_property("tags", [])
        new = self.look_for_tags(s)
        if set(old) != set(new):
            s.set_property("tags", list(set(new)))
            return True

    def on_message_added(self, event, message):
        series = message.get_series_head()
        if not series:
            return

        def newer_than(m1, m2):
            return m1.version > m2.version and m1.date >= m2.date
        for m in series.get_alternative_revisions():
            if newer_than(m, series):
                series.set_property("obsoleted-by", m.message_id)
            elif newer_than(series, m):
                m.set_property("obsoleted-by", series.message_id)

        updated = self.update_tags(series)

        for p in series.get_patches():
            updated = updated or self.update_tags(p)

        reviewers = set()
        num_reviewed = 0
        def _find_reviewers(what):
            ret = set()
            for rev_tag in [x for x in what.get_property("tags", []) if x.lower().startswith(REV_BY_PREFIX.lower())]:
                ret.add(parse_address(rev_tag[len(REV_BY_PREFIX):]))
            return ret
        for p in series.get_patches():
            first = True
            this_reviewers = _find_reviewers(p)
            if this_reviewers:
                if first:
                    num_reviewed += 1
                    first = False
                reviewers = reviewers.union(this_reviewers)
        series_reviewers = _find_reviewers(series)
        reviewers = reviewers.union(series_reviewers)
        if num_reviewed == series.get_num()[1] or series_reviewers:
            series.set_property("reviewed", True)
            series.set_property("reviewers", list(reviewers))
        if updated:
            emit_event("TagsUpdate", series=series)

    def parse_message_tags(self, m):
        r = []
        regex = self.get_tag_regex()
        for l in m.get_body().splitlines():
            if regex.match(l):
                r.append(l)
        return r

    def look_for_tags(self, m):
        # Incorporate tags from non-patch replies
        r = self.parse_message_tags(m)
        for x in m.get_replies():
            if x.is_patch:
                continue
            r += self.look_for_tags(x)
        return r

    def get_tags(self, m, request, format):
        return m.get_property("tags", [])

    def rest_message_fields_hook(self, request, fields):
        fields['tags'] = PluginMethodField(obj=self)

    def prepare_message_hook(self, request, message, detailed):
        if not message.is_series_head:
            return
        if message.get_property("reviewed"):
            reviewers = message.get_property("reviewers")
            message.status_tags.append({
                "title": "Reviewed by " + ", ".join([x for x, y in reviewers]),
                "type": "success",
                "char": "R",
                })
        ob = message.get_property("obsoleted-by")
        if ob:
            new = Message.objects.find_series(ob, message.project.name)
            if new is not None:
                message.status_tags.append({
                    "title": "Has a newer version: " + new.subject,
                    "type": "default",
                    "char": "O",
                    "row_class": "obsolete"
                    })
        message.extra_links.append({"html": mark_safe(html), "icon": "exchange" })

    # FIXME: what happens with base64 messages?
    def get_mbox_with_tags(self, m):
        def result_iter():
            regex = self.get_tag_regex()
            old_tags = set()
            lines = lines_iter(m.get_mbox())
            need_minusminusminus = False
            for line in lines:
                if line.startswith('---'):
                    need_minusminusminus = True
                    break
                yield line
                if regex.match(line):
                    old_tags.add(line)

            # If no --- line, tags go at the end as there's no better place
            for tag in m.get_property("tags", []):
                if not tag in old_tags:
                    yield tag
            if need_minusminusminus:
                yield line
            yield from lines

        return '\n'.join(result_iter())
