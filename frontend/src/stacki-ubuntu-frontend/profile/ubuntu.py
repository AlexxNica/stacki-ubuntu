#! /opt/stack/bin/python
#
# @SI_Copyright@
# @SI_Copyright@

from __future__ import print_function
import os
import sys
import string
import syslog
import stack.api
import profile

class Profile(profile.ProfileBase):

        def main(self, client):

                report = []
		cmd = '/opt/stack/bin/stack list host profile %s document=false' % client.addr
                for line in os.popen(cmd).readlines():
                        report.append(line[:-1])

                #
                # Done
                #
                if report:
                        out = string.join(report, '\n')
                        print('Content-type: application/octet-stream')
                        print('Content-length: %d' % (len(out)))
                        print('')
                        print(out)
		
