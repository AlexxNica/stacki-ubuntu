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
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
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
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@

import string
import types
import sys
import os
import time
import xml.dom.NodeFilter
import xml.dom.ext.reader.Sax2
import stack.js
import stack.cond
import stack.gen
	
		
class Generator(stack.gen.Generator):

	def __init__(self):
		stack.gen.Generator.__init__(self)	
		self.ks                 = {}
		self.ks['order']	= []
		self.ks['debug']	= []
		self.ks['main']         = []
		self.ks['packages']     = []
		self.ks['finish']	= []
		self.ks['pre']          = []
		self.ks['post']         = []
		self.finish_section     = 0
		self.log = '/var/log/stack-install.log'

                # We could set these elsewhere but this is the current
                # definition of the Ubuntu Generator.

                self.setOS('ubuntu')
		self.setArch('x86_64')
	
	##
	## Parsing Section
	##
	
	def parse(self, xml_string):
		import cStringIO
		xml_buf = cStringIO.StringIO(xml_string)
		doc = xml.dom.ext.reader.Sax2.FromXmlStream(xml_buf)
		filter = stack.gen.MainNodeFilter(self.attrs)
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT,
			filter, 0)
		node = iter.nextNode()
		while node:
			if node.nodeName == 'profile':
				self.handle_profile(node)
			elif node.nodeName == 'main':
				child = iter.firstChild()
				while child:
					self.handle_mainChild(child)
					child = iter.nextSibling()
			node = iter.nextNode()

		filter = stack.gen.OtherNodeFilter(self.attrs)
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT, filter, 0)
		node = iter.nextNode()
		while node:
			if node.nodeName != 'profile':
				self.order(node)
                                try:
                                        fn = eval('self.handle_%s' % node.nodeName)
                                except AttributeError:
                                        fn = None
                                if fn:
                                        fn(node)
			node = iter.nextNode()


	# <profile>
	
	def handle_profile(self, node):
		# pull out the attr to handle generic conditionals
		# this replaces the old arch/os logic but still
		# supports the old syntax

		if node.attributes:
			attrs = node.attributes.getNamedItem((None, 'attrs'))
			if attrs:
				dict = eval(attrs.value)
				for (k,v) in dict.items():
					self.attrs[k] = v

	def handle_mainChild(self, node):
		attr = node.attributes
		roll, nodefile, color = self.get_context(node)
		if 'tasksel' in node.nodeName:
			self.ks['main'].append('%s %s' % (node.nodeName, self.getChildText(node)))
		else:
			self.ks['main'].append('d-i %s/%s' % (node.nodeName, self.getChildText(node)))
	
	def handle_late_command(self, node):
		txt = self.getChildText(node)
		commands = txt.split(";")
		
		for (idx, command) in enumerate(commands):
			command = command.strip()
			if not command:
				continue
			
			if not self.ks['post']:
				self.ks['post'].append('d-i preseed/%s string %s;\\' % (node.nodeName.strip(), command))
			elif idx < len(commands) - 2:
				self.ks['post'].append('%s;\\' % command)
			else:
				self.ks['post'].append('%s' % command)
			

	def handle_grub_installer(self, node):
		self.ks['finish'].append('d-i grub-installer/%s' % self.getChildText(node))

	def handle_finish_install(self, node):
		self.ks['finish'].append('d-i finish-install/%s' % self.getChildText(node))

	def handle_pre(self, node):
		pass

	def handle_package(self, node):
		pass


		
	def get_context(self, node):
		# This function returns the rollname,
		# and nodefile of the node currently being
		# processed
		attr = node.attributes
		roll = None
		nodefile = None
		color = None
		if attr.getNamedItem((None, 'roll')):
			roll = attr.getNamedItem((None, 'roll')).value
		if attr.getNamedItem((None, 'file')):
			nodefile = attr.getNamedItem((None, 'file')).value
		if attr.getNamedItem((None, 'color')):
			color = attr.getNamedItem((None, 'color')).value
		return (roll, nodefile, color)
	
	# <post>
	def handle_post(self, node):
		"""Function works in an interesting way. On solaris the post
		sections are executed in the installer environment rather than
		in the installed environment. So the way we do it is to write
		a script for every post section, with the correct interpreter
		and execute it with a chroot command.
		"""
		# TODO remove return later
		return
		attr = node.attributes
		# By default we always want to chroot, unless
		# otherwise specified
		if attr.getNamedItem((None, 'chroot')):
			chroot = attr.getNamedItem((None, 'chroot')).value
		else:
			chroot = 'yes'

		# By default, the interpreter is always /bin/sh, unless
		# otherwise specified.
		if attr.getNamedItem((None, 'interpreter')):
			interpreter = attr.getNamedItem((None,
				'interpreter')).value
		else:
			interpreter = '/bin/sh'

		# The args that are supplied are for the command that
		# you want to run, and not to the installer section.
		if attr.getNamedItem((None, 'arg')):
			arg = attr.getNamedItem((None, 'arg')).value
		else:
			arg = ''

		list = []

		if self.finish_section == 0:
			list.append("d-i preseed/late_command string in-target")

		if chroot == 'yes':
			list.append("\tin-target cat > /a/tmp/post_section_%d << '__eof__'; \\"
					% self.finish_section)
			list.append("#!%s" % interpreter)
			list.append(self.getChildText(node))
			list.append("__eof__")
			list.append("\tin-target chmod a+rx /a/tmp/post_section_%d; \\"
					% self.finish_section)
			list.append("\tin-target chroot /a /tmp/post_section_%d %s; \\"
					% (self.finish_section, arg))
		else:
			if interpreter is not '/bin/sh':
				list.append("\tin-target cat > /tmp/post_section_%d "
					"<< '__eof__'; \\"
					% self.finish_section)
				list.append("#!%s" % interpreter)
				list.append(self.getChildText(node))
				list.append("__eof__")
				list.append("\tin-target chmod a+rx /tmp/post_section_%d;"
					% self.finish_section)
				list.append("\t%s /tmp/post_section_%d;"
					% (interpreter, self.finish_section))
			
			else:
				list.append(self.getChildText(node))

		self.finish_section = self.finish_section+1
		self.ks['finish'] += list

	def generate_main(self):
		list = []
		list.append('')
		list += self.ks['main']
		return list

	def generate_packages(self):
		list = []
		list.append('')
		list += self.ks['packages']
		return list

	def generate_post(self):
		list = []
		list.append('')
		list += self.ks['post']
		return list

	def generate_finish(self):
		list = []
		list.append('')
		list += self.ks['finish']
		return list

