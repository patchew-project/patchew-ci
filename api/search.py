#!/usr/bin/env python3
#
# Copyright 2016 Red Hat, Inc.
#
# Authors:
#     Fam Zheng <famz@redhat.com>
#
# This work is licensed under the MIT License.  Please see the LICENSE file or
# http://opensource.org/licenses/MIT.

from .models import Message, MessageResult, Result, QueuedSeries
from functools import reduce

from django.db import connection
from django.db.models import Q

from django.contrib.postgres.search import SearchQuery, SearchVector, SearchVectorField
from django.db.models import Lookup
from django.db.models.fields import Field


@Field.register_lookup
class NotEqual(Lookup):
    lookup_name = "ne"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s <> %s" % (lhs, rhs), params


class InvalidSearchTerm(Exception):
    pass


# Hack alert: Django wraps each argument to to_tsvector with a COALESCE function,
# and that causes postgres not to use the index.  Monkeypatch the constructor
# to skip that step, which we do not need since the subject field is not nullable.
class NonNullSearchVector(SearchVector):
    function = "to_tsvector"
    arg_joiner = " || ' ' || "
    _output_field = SearchVectorField()
    config = None

    def __init__(self, *expressions, **extra):
        super(SearchVector, self).__init__(*expressions, **extra)
        self.config = self.extra.get("config", self.config)
        self.weight = None


class SearchEngine(object):
    """

The general form of search string is a list of terms separated with space:

    QUERY = TERM TERM ...

Each term can be either a plain keyword, or a predict in the form of
`PRED:EXP`, where PRED is the predefined filter and EXP is the parameters to be
applied to the filter. As a simple example:

    bugfix from:Bob to:George age:>1w

to search emails titled as 'bugfix' (a subject keyword filter) from Bob (a
sender filter) to George (a recipient filter) before 1 week ago (an age
filter).

or

    bugfix from:Bob is:reviewed not:obsoleted

to search all emails from Bob that have "bugfix" in subject, and have been
reviewed but is not obsoleted (by a new revision of this series). Because there
are syntax shortcut for some predicts, it can be simplified as:

    from:Bob fix +reviewed -tested

---

## Supported filter types

### Search by age

 - Syntax: age:AGE
 - Syntax: >AGE
 - Syntax: <AGE

Filter by age of the message. Supports "d" (day), "w" (week), "m" (month) and "y" (year) as units. Examples:

 - age:1d
 - age:>2d
 - age:<1w
 - <1m
 - \>1w

---

### Search by series state

Syntax:

 - is:reviewed - all the patches in the series is reviewed
 - is:obsolete, is:obsoleted, is:old - the series has newer version
 - is:complete - the series has all the patches it contains
 - is:merged - the series is included in the project's git tree
 - is:pull - the series is a pull request
 - is:applied - a git tree is available for the series
 - has:replies - the series received a reply (apart from patches sent by the submitter)

Example:

    is:reviewed

"not:X" is the opposite of "is:X". "+X" and "-X" are shorter synonyms of "is:X"
and "not:X" respectively.

---

### Search addresses

 - Syntax: from:ADDRESS
 - Syntax: to:ADDRESS

Compare the address info of message. Example:

    from:alice to:bob

---

### Search by maintainer associated with the changeset

 - Syntax: maintained-by:NAME
 - Syntax: maint:NAME

NAME can be the name, email or a substring of MAINTAINERS file entries of the
maintainer.

---

### Search by result

Syntax:

 - pending:NAME, failure:NAME, running:NAME - any result with the given
   name is in the pending/failure/running state
 - success:NAME - all results with the given name are in the success state
   (and there is at least one result with the given name)

where NAME can be e.g. "git", "testing", "testing.TEST-NAME"

Example:

    success:git
    failure:testing.FreeBSD

---

### Search by review state

Syntax:

 - accept:USERNAME or ack:USERNAME - the series was marked as accepted by the user
 - reject:USERNAME or nack:USERNAME - the series was marked as reject by the user
 - review:USERNAME - the series was marked as accepted or rejected by the user
 - watch:USERNAME - the series is in the user's watched queue

USERNAME can be "me" to identify the current user

---

### Reverse condition

 - Syntax: !TERM

Negative of an expression. Example:

    !is:reviewed     (query series that are not reviewed)
    !has:replies     (query series that have not received any comment)

---

### Search by message id

 - Syntax: id:MESSAGE-ID
 - Syntax: rfc822msgid:MESSAGE-ID

Exact match of message-id. Example:

    id:<1416902879-17422-1-git-send-email-user@domain.com>

or

    id:1416902879-17422-1-git-send-email-user@domain.com

The two prefixes are equivalent.

---

### Search by text

 - Syntax: KEYWORD

Search text keyword in the email message. Example:

    regression

"""

    def _make_filter_subquery(self, model, q):
        message_ids = model.objects.filter(q).values("message_id")
        return Q(id__in=message_ids)

    def _make_filter_result(self, term, **kwargs):
        q = Q(name=term, **kwargs) | Q(name__startswith=term + ".", **kwargs)
        return self._make_filter_subquery(MessageResult, q)

    def _make_filter_age(self, cond):
        import datetime

        def human_to_seconds(n, unit):
            if unit == "d":
                return n * 86400
            elif unit == "w":
                return n * 86400 * 7
            elif unit == "m":
                return n * 86400 * 30
            elif unit == "y":
                return n * 86400 * 365
            raise Exception("No unit specified")

        if cond.startswith("<"):
            less = True
            cond = cond[1:]
        elif cond.startswith(">"):
            less = False
            cond = cond[1:]
        else:
            less = False
        num, unit = cond[:-1], cond[-1].lower()
        if not num.isdigit() or unit not in "dwmy":
            raise InvalidSearchTerm("Invalid age string: %s" % cond)
        sec = human_to_seconds(int(num), unit)
        p = datetime.datetime.now() - datetime.timedelta(0, sec)
        if less:
            q = Q(date__gte=p)
        else:
            q = Q(date__lte=p)
        return q

    def _add_to_keywords(self, t):
        self._last_keywords.append(t)
        return Q()

    def _make_filter_is(self, cond):
        if cond == "complete":
            return Q(is_complete=True)
        elif cond == "pull":
            self._add_to_keywords("PULL")
            return Q(subject__contains="[PULL") | Q(subject__contains="[GIT PULL")
        elif cond == "reviewed":
            return Q(is_reviewed=True)
        elif cond in ("obsoleted", "old", "obsolete"):
            return Q(is_obsolete=True)
        elif cond == "applied":
            return self._make_filter_subquery(
                MessageResult, Q(name="git", status=Result.SUCCESS)
            )
        elif cond == "tested":
            return Q(is_tested=True)
        elif cond == "merged":
            return Q(is_merged=True)
        return None

    def _make_filter_queue(self, username, user, **kwargs):
        if username == "me":
            if not user.is_authenticated:
                # Django hack to return an always false Q object
                return Q(pk=None)
            q = Q(user=user, **kwargs)
        else:
            q = Q(user__username=username, **kwargs)
        return self._make_filter_subquery(QueuedSeries, q)

    def _make_filter(self, term, user):
        if term.startswith("age:"):
            cond = term[term.find(":") + 1 :]
            return self._make_filter_age(cond)
        elif term[0] in "<>" and len(term) > 1:
            return self._make_filter_age(term)
        elif term.startswith("from:"):
            cond = term[term.find(":") + 1 :]
            return Q(sender__icontains=cond)
        elif term.startswith("to:"):
            cond = term[term.find(":") + 1 :]
            return Q(recipients__icontains=cond)
        elif term.startswith("subject:"):
            cond = term[term.find(":") + 1 :]
            return self._add_to_keywords(cond)
        elif term.startswith("id:") or term.startswith("rfc822msgid:"):
            cond = term[term.find(":") + 1 :]
            if cond[0] == "<" and cond[-1] == ">":
                cond = cond[1:-1]
            return Q(message_id=cond)
        elif term.startswith("is:"):
            return self._make_filter_is(term[3:]) or self._add_to_keywords(term)
        elif term.startswith("not:"):
            return ~self._make_filter_is(term[4:]) or self._add_to_keywords(term)
        elif term.startswith("has:"):
            cond = term[term.find(":") + 1 :]
            if cond == "replies":
                return Q(last_comment_date__isnull=False)
            else:
                return Q(properties__name=cond)
        elif term.startswith("failure:"):
            return self._make_filter_result(term[8:], status=Result.FAILURE)
        elif term.startswith("success:"):
            # What we want is "all results are successes", but the only way to
            # express it is "there is a result and not (any result is not a success)".
            return self._make_filter_result(term[8:]) & ~self._make_filter_result(
                term[8:], status__ne=Result.SUCCESS
            )
        elif term.startswith("pending:"):
            return self._make_filter_result(term[8:], status=Result.PENDING)
        elif term.startswith("running:"):
            return self._make_filter_result(term[8:], status=Result.RUNNING)
        elif (
            term.startswith("ack:")
            or term.startswith("accept:")
            or term.startswith("accepted:")
        ):
            username = term[term.find(":") + 1 :]
            return self._make_filter_queue(username, user, name="accept")
        elif (
            term.startswith("nack:")
            or term.startswith("reject:")
            or term.startswith("rejected:")
        ):
            username = term[term.find(":") + 1 :]
            return self._make_filter_queue(username, user, name="reject")
        elif term.startswith("review:") or term.startswith("reviewed:"):
            username = term[term.find(":") + 1 :]
            return self._make_filter_queue(
                username, user, name__in=["accept", "reject"]
            )
        elif term.startswith("watch:") or term.startswith("watched:"):
            username = term[term.find(":") + 1 :]
            return self._make_filter_queue(username, user, name="watched")
        elif term.startswith("project:"):
            cond = term[term.find(":") + 1 :]
            self._projects.add(cond)
            return Q(project__name=cond) | Q(project__parent_project__name=cond)
        elif term.startswith("maintained-by:") or term.startswith("maint:"):
            cond = term[term.find(":") + 1 :]
            if cond == "me" and user:
                cond = user.email
            return Q(maintainers__icontains=cond)

        # Keyword in subject is the default
        return self._add_to_keywords(term)

    def _process_term(self, term, user):
        """ Return a Q object that will be applied to the query """
        is_plusminus = neg = False
        if term[0] in "+-!":
            neg = term[0] != "+"
            is_plusminus = term[0] != "!"
            term = term[1:]

        if is_plusminus and ":" not in term:
            q = self._make_filter_is(term) or self._add_to_keywords(term)
        else:
            q = self._make_filter(term, user)
        if neg:
            return ~q
        else:
            return q

    def last_keywords(self):
        return getattr(self, "_last_keywords", [])

    def project(self):
        return next(iter(self._projects)) if len(self._projects) == 1 else None

    def search_series(self, *terms, user=None, queryset=None):
        self._last_keywords = []
        self._projects = set()
        q = reduce(
            lambda x, y: x & y, map(lambda t: self._process_term(t, user), terms), Q()
        )
        if queryset is None:
            queryset = Message.objects.series_heads()
        if self._last_keywords:
            if connection.vendor == "postgresql":
                queryset = queryset.annotate(
                    subjsearch=NonNullSearchVector("subject", config="english")
                )
                searchq = reduce(
                    lambda x, y: x & y,
                    map(
                        lambda x: SearchQuery(x, config="english"), self._last_keywords
                    ),
                )
                q = q & Q(subjsearch=searchq)
            else:
                q = reduce(
                    lambda x, y: x & Q(subject__icontains=y), self._last_keywords, q
                )

        return queryset.filter(q)

    def query_test_message(self, query, message):
        queryset = Message.objects.filter(id=message.id)
        terms = [x.strip() for x in query.split() if x.strip()]
        return self.search_series(*terms, queryset=queryset).first()
