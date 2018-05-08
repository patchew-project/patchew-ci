#!/usr/bin/env python3
#
# Copyright 2017 Red Hat, Inc.
#
# Authors:
#     Fam Zheng <famz@redhat.com>
#
# This work is licensed under the MIT License.  Please see the LICENSE file or
# http://opensource.org/licenses/MIT.

import os
import sys
import mbox
sys.path.append(os.path.dirname(__file__))
from patchewtest import PatchewTestCase, main

class MboxTest(PatchewTestCase):

    def test_multipart_in_multipart(self):
        expected = """
On 07/25/2017 10:57 AM, Jeff Cody wrote:
> Signed-off-by: Jeff Cody <jcody@redhat.com>
> ---
>  redhat/build_configure.sh     | 3 +++
>  redhat/qemu-kvm.spec.template | 7 +++++++
>  2 files changed, 10 insertions(+)
> 

ACK

-- 
Eric Blake, Principal Software Engineer
Red Hat, Inc.           +1-919-301-3266
Virtualization:  qemu.org | libvirt.org
        """.strip()
        dp = self.get_data_path("0016-nested-multipart.mbox.gz")
        with open(dp, "r") as f:
            msg = mbox.MboxMessage(f.read())
        self.assertEqual(msg.get_body().strip(), expected)

    def test_mime_word_recipient(self):
        dp = self.get_data_path("0018-mime-word-recipient.mbox.gz")
        with open(dp, "r") as f:
            msg = mbox.MboxMessage(f.read())
        utf8_recipient = msg.get_cc()[1]
        self.assertEqual(utf8_recipient[0], "Philippe Mathieu-Daudé")
        self.assertEqual(utf8_recipient[1], "f4bug@amsat.org")

    def test_mode_only_patch(self):
        dp = self.get_data_path("0021-mode-only-patch.mbox.gz")
        with open(dp, "r") as f:
            msg = mbox.MboxMessage(f.read())
        self.assertTrue(msg.is_patch())

    def test_get_json(self):
        expected = {'message_id': '20160628014747.20971-1-famz@redhat.com',
                    'in_reply_to': '',
                    'date': '2016-06-28T01:47:47',
                    'subject': '[Qemu-devel] [PATCH] quorum: Only compile when supported',
                    'sender': {'name': 'Fam Zheng', 'address': 'famz@redhat.com'},
                    'recipients': [{'address': 'qemu-devel@nongnu.org'},
                                   {'name': 'Kevin Wolf', 'address': 'kwolf@redhat.com'},
                                   {'name': 'Alberto Garcia', 'address': 'berto@igalia.com'},
                                   {'address': 'qemu-block@nongnu.org'},
                                   {'name': 'Max Reitz', 'address': 'mreitz@redhat.com'}],
                    'mbox': 'Delivered-To: importer@patchew.org\nReceived-SPF: '
                            'Pass (zoho.com: domain of qemu-devel-bounces@nongnu.org '
                            'designates 208.118.235.17 as permitted sender )  client-ip: '
                            '208.118.235.17\nReceived-SPF: pass (zoho.com: domain of '
                            'gnu.org designates 208.118.235.17 as permitted sender) '
                            'client-ip=208.118.235.17; envelope-from=qemu-devel-bounces+'
                            'importer=patchew.org@nongnu.org; helo=lists.gnu.org;\n'
                            'Return-Path: <qemu-devel-bounces+importer=patchew.org@nongnu.org>'
                            '\nReceived: from lists.gnu.org (lists.gnu.org [208.118.235.17]) '
                            'by mx.zohomail.com\n\twith SMTPS id 1467078971424862.8927889595075;'
                            ' Mon, 27 Jun 2016 18:56:11 -0700 (PDT)\nReceived: from localhost '
                            '([::1]:33689 helo=lists.gnu.org)\n\tby lists.gnu.org with esmtp '
                            '(Exim 4.71)\n\t(envelope-from <qemu-devel-bounces+importer='
                            'patchew.org@nongnu.org>)\n\tid 1bHi94-0006LP-Ok\n\tfor '
                            'importer@patchew.org; Mon, 27 Jun 2016 21:48:58 -0400\nReceived: '
                            'from eggs.gnu.org ([2001:4830:134:3::10]:53270)\n\tby lists.gnu.org'
                            ' with esmtp (Exim 4.71)\n\t(envelope-from <famz@redhat.com>) id '
                            '1bHi8E-0002Lm-KR\n\tfor qemu-devel@nongnu.org; Mon, 27 Jun 2016 '
                            '21:48:07 -0400\nReceived: from Debian-exim by eggs.gnu.org with '
                            'spam-scanned (Exim 4.71)\n\t(envelope-from <famz@redhat.com>) '
                            'id 1bHi8D-0008T4-N7\n\tfor qemu-devel@nongnu.org; Mon, 27 Jun '
                            '2016 21:48:06 -0400\nReceived: from mx1.redhat.com '
                            '([209.132.183.28]:47972)\n\tby eggs.gnu.org with esmtp '
                            '(Exim 4.71)\n\t(envelope-from <famz@redhat.com>)\n\tid '
                            '1bHi86-0008SN-IZ; Mon, 27 Jun 2016 21:47:58 -0400\nReceived: '
                            'from int-mx10.intmail.prod.int.phx2.redhat.com\n\t'
                            '(int-mx10.intmail.prod.int.phx2.redhat.com [10.5.11.23])\n\t'
                            '(using TLSv1.2 with cipher ECDHE-RSA-AES256-GCM-SHA384 '
                            '(256/256 bits))\n\t(No client certificate requested)\n\tby '
                            'mx1.redhat.com (Postfix) with ESMTPS id BDB007F088;\n\tTue, '
                            '28 Jun 2016 01:47:57 +0000 (UTC)\nReceived: '
                            'from ad.usersys.redhat.com (dhcp-15-133.nay.redhat.com\n\t'
                            '[10.66.15.133])\n\tby int-mx10.intmail.prod.int.phx2.redhat.com'
                            ' (8.14.4/8.14.4) with ESMTP\n\tid u5S1lssT024908; Mon, 27 Jun '
                            '2016 21:47:55 -0400\nFrom: Fam Zheng <famz@redhat.com>\nTo: '
                            'qemu-devel@nongnu.org\nDate: Tue, 28 Jun 2016 09:47:47 '
                            '+0800\nMessage-Id: <20160628014747.20971-1-famz@redhat.com>\n'
                            'X-Scanned-By: MIMEDefang 2.68 on 10.5.11.23\nX-Greylist: '
                            'Sender IP whitelisted, not delayed by milter-greylist-4.5.16\n\t'
                            '(mx1.redhat.com [10.5.110.26]);\n\tTue, 28 Jun 2016 01:47:57 '
                            '+0000 (UTC)\nX-detected-operating-system: by eggs.gnu.org: '
                            'GNU/Linux 2.2.x-3.x [generic]\nX-Received-From: 209.132.183.28\n'
                            'Subject: [Qemu-devel] [PATCH] quorum: Only compile when supported\n'
                            'X-BeenThere: qemu-devel@nongnu.org\nX-Mailman-Version: 2.1.21\n'
                            'Precedence: list\nList-Id: <qemu-devel.nongnu.org>\nList-Unsubscribe:'
                            ' <https://lists.nongnu.org/mailman/options/qemu-devel>,\n\t'
                            '<mailto:qemu-devel-request@nongnu.org?subject=unsubscribe>\n'
                            'List-Archive: <http://lists.nongnu.org/archive/html/qemu-devel/>\n'
                            'List-Post: <mailto:qemu-devel@nongnu.org>\nList-Help: '
                            '<mailto:qemu-devel-request@nongnu.org?subject=help>\nList-Subscribe:'
                            ' <https://lists.nongnu.org/mailman/listinfo/qemu-devel>,\n\t'
                            '<mailto:qemu-devel-request@nongnu.org?subject=subscribe>\nCc:'
                            ' Kevin Wolf <kwolf@redhat.com>, Alberto Garcia <berto@igalia.com>,'
                            '\n\tqemu-block@nongnu.org, Max Reitz <mreitz@redhat.com>\nErrors-To:'
                            ' qemu-devel-bounces+importer=patchew.org@nongnu.org\nSender: '
                            '"Qemu-devel" <qemu-devel-bounces+importer=patchew.org@nongnu.org>\n'
                            'X-ZohoMail-Owner: <20160628014747.20971-1-famz@redhat.com>+zmo_0_'
                            '<qemu-devel-bounces+importer=patchew.org@nongnu.org>\n'
                            'X-ZohoMail-Sender: 209.132.183.28\nX-ZohoMail: RSF_0  Z_629925259 '
                            'SPT_1 Z_629926901 SPT_1  SS_1 SFPD SFPP UW2468 UB2468 ZFF-EB_1'
                            ' COSF  ODL   SGR3_1_2_0_27046_53\nX-Zoho-Virus-Status: 2\n\n'
                            'This was the only exceptional module init function that does '
                            'something\nelse than a simple list of bdrv_register() calls, '
                            'in all the block\ndrivers.\n\nThe qcrypto_hash_supports is actually'
                            ' a static check, determined at\ncompile time.  Follow the '
                            'block-job-$(CONFIG_FOO) convention for\nconsistency.\n\n'
                            'Signed-off-by: Fam Zheng <famz@redhat.com>\n---\n block/'
                            'Makefile.objs | 2 +-\n block/quorum.c      | 4 ----\n 2 files'
                            ' changed, 1 insertion(+), 5 deletions(-)\n\ndiff --git a/block/'
                            'Makefile.objs b/block/Makefile.objs\nindex 44a5416..c87d605 '
                            '100644\n--- a/block/Makefile.objs\n+++ b/block/Makefile.objs\n@@'
                            ' -3,7 +3,7 @@ block-obj-y += qcow2.o qcow2-refcount.o qcow2-cluster.o'
                            ' qcow2-snapshot.o qcow2-c\n block-obj-y += qed.o qed-gencb.o '
                            'qed-l2-cache.o qed-table.o qed-cluster.o\n block-obj-y += '
                            'qed-check.o\n block-obj-$(CONFIG_VHDX) += vhdx.o vhdx-endian.o'
                            ' vhdx-log.o\n-block-obj-y += quorum.o\n+block-obj-$(CONFIG_GNUTLS_HASH)'
                            ' += quorum.o\n block-obj-y += parallels.o blkdebug.o blkverify.o '
                            'blkreplay.o\n block-obj-y += block-backend.o snapshot.o qapi.o\n '
                            'block-obj-$(CONFIG_WIN32) += raw-win32.o win32-aio.o\ndiff --git '
                            'a/block/quorum.c b/block/quorum.c\nindex 331b726..18fbed8 100644\n'
                            '--- a/block/quorum.c\n+++ b/block/quorum.c\n@@ -1113,10 +1113,6 @@'
                            ' static BlockDriver bdrv_quorum = {\n \n static void bdrv_quorum_init'
                            '(void)\n {\n-    if (!qcrypto_hash_supports(QCRYPTO_HASH_ALG_SHA256))'
                            ' {\n-        /* SHA256 hash support is required for quorum device */\n-'
                            '        return;\n-    }\n     bdrv_register(&bdrv_quorum);\n }\n \n-- \n'
                            '2.9.0\n\n\n'}
        dp = self.get_data_path("0001-simple-patch.mbox.gz")
        with open(dp, "r") as f:
            msg = mbox.MboxMessage(f.read()).get_json()
        self.assertEqual(msg, expected)

if __name__ == '__main__':
    main()
