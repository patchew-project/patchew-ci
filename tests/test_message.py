#!/usr/bin/env python3
#
# Copyright 2016 Red Hat, Inc.
#
# Authors:
#     Fam Zheng <famz@redhat.com>
#
# This work is licensed under the MIT License.  Please see the LICENSE file or
# http://opensource.org/licenses/MIT.

import time
import datetime
import json
from tests.patchewtest import PatchewTestCase, main

class ProjectTest(PatchewTestCase):

    def setUp(self):
        self.create_superuser()

    def test_0_second(self):
        from api.models import Message
        message = Message()
        message.date = datetime.datetime.utcnow()
        age = message.get_age()
        self.assertEqual(age, "0 second")

    def test_now(self):
        from api.models import Message
        message = Message()
        dt = datetime.datetime.fromtimestamp(time.time() + 100)
        message.date = dt
        age = message.get_age()
        self.assertEqual(age, "now")

    def test_1_day(self):
        from api.models import Message
        message = Message()
        dt = datetime.datetime.fromtimestamp(time.time() - 3600 * 25)
        message.date = dt
        age = message.get_age()
        self.assertEqual(age, "1 day")

    def test_delete(self):
        self.cli_login()
        self.add_project("QEMU", "qemu-devel@nongnu.org")
        self.cli_import("0002-unusual-cased-tags.mbox.gz")
        self.cli_import("0004-multiple-patch-reviewed.mbox.gz")
        a, b = self.check_cli(["search", "-r", "-o", "subject,properties,message-id"])
        ao = json.loads(a)[0]
        self.assertEqual(["Fam Zheng", "famz@redhat.com"],
                         ao["properties"]["reviewers"][0])
        self.cli_delete("from:Fam")
        a, b = self.check_cli(["search", "-r", "-o", "message-id"])
        ao = json.loads(a)[0]
        self.assertEqual("1469192015-16487-1-git-send-email-berrange@redhat.com", ao['message-id'])

    def test_asctime(self):
        from api.models import Message
        message = Message()
        dt = datetime.datetime(2016, 10, 22, 10, 16, 40)
        message.date = dt
        asctime = message.get_asctime()
        self.assertEqual(asctime, "Sat Oct 22 10:16:40 2016")

        message = Message()
        dt = datetime.datetime(2016, 10, 22, 9, 6, 4)
        message.date = dt
        asctime = message.get_asctime()
        self.assertEqual(asctime, "Sat Oct 22 9:06:04 2016")

if __name__ == '__main__':
    main()
