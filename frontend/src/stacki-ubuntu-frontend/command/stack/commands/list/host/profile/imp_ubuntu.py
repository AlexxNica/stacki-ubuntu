#! /opt/stack/bin/python
#
# @SI_Copyright@
#                             www.stacki.com
#                                  v3.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

import stack.commands
import stack.ubugen
from stack.license import *

class Implementation(stack.commands.Implementation):

	@licenseCheck
	def run(self, args):

		host = args[0]
		xml  = args[1]

		self.generator = stack.ubugen.Generator()
		self.generator.setArch(self.owner.arch)
		self.generator.setOS(self.owner.os)

		if xml == None:
			xml = self.owner.command('list.host.xml', 
			[
			 host,
			 'os=%s' % self.owner.os,
			])
		self.runXML(xml, host)


	def runXML(self, xml, host):
		"""Reads the XML host profile and outputs Ubuntu
		preseed.cfg file"""
		
		# This keeps everything in one command and the
		# output can easily be parsed and split into 
		# individual files.

		list = []	
		self.generator.parse(xml)
		self.owner.addOutput(host, '<profile lang="preseed.cfg">\n')
		self.get_section = ['main', 'packages', 'post', 'finish']
		
		for section in self.get_section:	
			list += self.generator.generate(section,
				annotation=self.owner.annotation)
		else:
			list += self.generator.generate(self.owner.section,
					annotation=self.owner.annotation)
		self.owner.addOutput(host,
			self.owner.annotate('<section name="preseed.cfg">'))
		self.owner.addOutput(host, self.owner.annotate('<![CDATA['))
		for i in list:
			self.owner.addOutput(host, i)
		self.owner.addOutput(host, self.owner.annotate(']]>'))
		self.owner.addOutput(host, self.owner.annotate('</section>'))
		self.owner.addOutput(host, self.owner.annotate('</profile>'))
