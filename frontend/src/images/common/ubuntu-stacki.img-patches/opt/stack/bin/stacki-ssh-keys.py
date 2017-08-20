#!/opt/stack/bin/python

import sys
import os

sys.path.append('/tmp')
from stack_site import *


for k,v in ssh_keys.iteritems():

	if k == 'authorized_key':
		fname = '/target/root/.ssh/authorized_keys'
		f = open(fname, 'w')	
		f.write(ssh_keys[k])
		os.chmod(fname, 0o600)
		f.close()
	else:
		fname = '/target/etc/ssh/ssh_host_%s' % k
		f = open(fname, 'w')	
		f.write(ssh_keys[k])
		f.close()
		if 'pub' in k:
			os.chmod(fname, 0o444)
		else:
			os.chmod(fname, 0o400)
