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
	
		

class NodeFilter(xml.dom.NodeFilter.NodeFilter):

	def __init__(self, attrs):
		self.attrs = attrs

	def isCorrectCond(self, node):

		attr = node.attributes.getNamedItem((None, 'arch'))
		if attr:
			arch = attr.value
		else:
			arch = None

		attr = node.attributes.getNamedItem((None, 'os'))
		if attr:
			os = attr.value
			if os == 'linux':
				os = 'redhat'
		else:
			os = None

		attr = node.attributes.getNamedItem((None, 'release'))
		if attr:
			release = attr.value
		else:
			release = None

		attr = node.attributes.getNamedItem((None, 'cond'))
		if attr:
			cond = attr.value
		else:
			cond = None

		expr = stack.cond.CreateCondExpr(arch, os, release, cond)
		return stack.cond.EvalCondExpr(expr, self.attrs)

		
class Generator:
	"""Base class for various DOM based kickstart graph generators.
	The input to all Generators is assumed to be the XML output of KPP."""
	
	def __init__(self):
		self.attrs	= {}
		self.arch	= None
		self.rcsFiles	= {}

	def setArch(self, arch):
		self.arch = arch
		
	def getArch(self):
		return self.arch
	
	def setOS(self, osname):
		self.os = osname
		
	def getOS(self):
		return self.os

	def isDisabled(self, node):
		return node.attributes.getNamedItem((None, 'disable'))

	def isMeta(self, node):
		attr  = node.attributes
		type  = attr.getNamedItem((None, 'type'))
		if type:
			type = type.value
		else:
			type = 'rpm'
		if type  == 'meta':
			return 1
		return 0
	
	def rcsBegin(self, file, owner, perms):
		"""
		If the is the first time we've seen a file ci/co it.  Otherwise
		just track the ownership and perms from the <file> tag .
		"""
		
		rcsdir	= os.path.join(os.path.dirname(file), 'RCS')
		rcsfile = '%s,v' % os.path.join(rcsdir, os.path.basename(file))
		l	= []

		l.append('')

		if file not in self.rcsFiles:
			l.append('if [ ! -f %s ]; then' % rcsfile)
			l.append('\tif [ ! -f %s ]; then' % file)
			l.append('\t\ttouch %s;' % file)
			l.append('\tfi')
			l.append('\tif [ ! -d %s ]; then' % rcsdir)
			l.append('\t\tmkdir -m 700 %s' % rcsdir)
			l.append('\t\tchown 0:0 %s' % rcsdir)
		 	l.append('\tfi;')
			l.append('\techo "original" | /opt/stack/bin/ci -q %s;' %
			 	file)
			l.append('\t/opt/stack/bin/co -q -f -l %s;' % file)
			l.append('fi')

		# If this is a subsequent file tag and the optional PERMS
		# or OWNER attributes are missing, use the previous value(s).
		
		if self.rcsFiles.has_key(file):
			(orig_owner, orig_perms) = self.rcsFiles[file]
			if not perms:
				perms = orig_perms
			if not owner:
				owner = orig_owner

		self.rcsFiles[file] = (owner, perms)
		
		if owner:
			l.append('chown %s %s' % (owner, file))
			l.append('chown %s %s' % (owner, rcsfile))

		if perms:
			l.append('chmod %s %s' % (perms, file))

		l.append('')

		return string.join(l, '\n')

	def rcsEnd(self, file, owner, perms):
		"""
		Run the final ci/co of a <file>.  The ownership of both the
		file and rcs file are changed to match the last requested
		owner in the file tag.  The perms of the file (not the file
		file) are also modified.

		The file is checked out locked, which is why we don't modify
		the perms of the RCS file itself.
		"""
		rcsdir	= os.path.join(os.path.dirname(file), 'RCS')
		rcsfile = '%s,v' % os.path.join(rcsdir, os.path.basename(file))
		l	= []

		l.append('')
		l.append('if [ -f %s ]; then' % file)
		l.append('\techo "stack" | /opt/stack/bin/ci -q %s;' % file)
		l.append('\t/opt/stack/bin/co -q -f -l %s;' % file)
		l.append('fi')		

		if owner:
			l.append('chown %s %s' % (owner, file))
			l.append('chown %s %s' % (owner, rcsfile))

		if perms:
			l.append('chmod %s %s' % (perms, file))

		return string.join(l, '\n')

	
	def order(self, node):
		"""
		Stores the order of traversal of the nodes
		Useful for debugging.
		"""
		roll, nodefile, color = self.get_context(node)
		if (roll, nodefile, color) not in self.ks['order']:
			self.ks['order'].append((roll, nodefile, color))
		
	def handle_mainChild(self, node):
		attr = node.attributes
		roll, nodefile, color = self.get_context(node)
		try:
			eval('self.handle_main_%s(node)' % node.nodeName)
		except AttributeError:
			self.ks['main'].append(('%s %s' % (node.nodeName,
				self.getChildText(node)), roll, nodefile, color))

		
	def parseFile(self, node):
		attr = node.attributes

		if attr.getNamedItem((None, 'os')):
			os = attr.getNamedItem((None, 'os')).value
			if os != self.getOS():
				return ''

		if attr.getNamedItem((None, 'name')):
			fileName = attr.getNamedItem((None, 'name')).value
		else:
			fileName = ''

		if attr.getNamedItem((None, 'mode')):
			fileMode = attr.getNamedItem((None, 'mode')).value
		else:
			fileMode = 'create'

		if attr.getNamedItem((None, 'owner')):
			fileOwner = attr.getNamedItem((None, 'owner')).value
		else:
			fileOwner = ''

		if attr.getNamedItem((None, 'perms')):
			filePerms = attr.getNamedItem((None, 'perms')).value
		else:
			filePerms = ''

		if attr.getNamedItem((None, 'vars')):
			fileQuoting = attr.getNamedItem((None, 'vars')).value
		else:
			fileQuoting = 'literal'

		if attr.getNamedItem((None, 'expr')):
			fileCommand = attr.getNamedItem((None, 'expr')).value
		else:
			fileCommand = None

		# Have the ability to turn off/on RCS checkins
		if attr.getNamedItem((None, 'rcs')):
			t = attr.getNamedItem((None, 'rcs')).value.lower()
			if t == 'false' or t == 'off':
				rcs = False
		else:
			rcs = True

		fileText = self.getChildText(node)

		if fileName:

			s = ''
			if rcs:
				s += self.rcsBegin(fileName, fileOwner, filePerms)

			if fileMode == 'append':
				gt = '>>'
			else:
				gt = '>'

			if fileCommand:
				s += '%s %s %s\n' % (fileCommand, gt, fileName)
			if not fileText:
				s += 'touch %s\n' % fileName
			else:
				if fileQuoting == 'expanded':
					eof = "EOF"
				else:
					eof = "'EOF'"

				s += "cat %s %s << %s" % (gt, fileName, eof)
				if fileText[0] != '\n':
					s += '\n'
				s += fileText
				if fileText[-1] != '\n':
					s += '\n'
				s += 'EOF\n'

			# If RCS is disabled, we still need to have support
			# for changing permissions, and owners.
			if not rcs:
				if fileOwner:
					s += 'chown %s %s\n' % (fileOwner, fileName)
				if filePerms:
					s += 'chmod %s %s\n' % (filePerms, fileName)
		return s
	
	# <*>
	#	<*> - tags that can go inside any other tags
	# </*>

	def getChildText(self, node):
		text = ''
		for child in node.childNodes:
			if child.nodeType == child.TEXT_NODE:
				text += child.nodeValue
			elif child.nodeType == child.ELEMENT_NODE:
				text += eval('self.handle_child_%s(child)' \
					% (child.nodeName))
		return text

	
	# <*>
	#	<file>
	# </*>
	
	def handle_child_file(self, node):
		return self.parseFile(node)

	##
	## Generator Section
	##
			
	def generate(self, section, annotation=False):
		"""Dump the requested section of the kickstart file.  If none 
		exists do nothing."""
		list = []
		try:
			f = getattr(self, "generate_%s" % section)
		except AttributeError:
			f = None
		if f:
			list += f()

		return self.annotate(list, annotation)

	def generate_order(self):
		list = []
		list.append('#')
		list.append('# Node Traversal Order')
		list.append('#')
		for (roll, nodefile, color) in self.ks['order']:
			list.append(('# %s (%s)' % (nodefile, roll),
				roll, nodefile, color))
		list.append('#')
		return list

	def generate_debug(self):
		list = []
		list.append('#')
		list.append('# Debugging Information')
		list.append('#')
		for text in self.ks['debug']:
			for line in string.split(text, '\n'):
				list.append('# %s' % line)
		list.append('#')
		return list

	def annotate(self, l, annotation=False):
		o = []
		if annotation:
			for line in l:
				if type(line) == str or \
					type(line) == unicode:
					o.append([line, None, 'Internal', None])
				else:
					o.append(list(line))
		else:
			for line in l:
				if type(line) == tuple:
					o.append(line[0])
				else:
					o.append(line)
		return o

class MainNodeFilter_ubuntu(NodeFilter):
	"""
	This class either accepts or reject tags
	from the node XML files. All tags are under
	the <main>*</main> tags.
	Each and every one of these tags needs to
	have a handler for them in the Generator
	class.
	"""
	def acceptNode(self, node):

		if node.nodeName not in [
			'kickstart',
			'main', 	# <main><*></main>
			'debian-installer',
			'auto-install',
			'time',
			'console-setup',
			'keyboard-configuration',
			'debconf',
			'mirror',
			'apt-setup',
			'pkgsel',
			'live-installer',
			'netcfg',
			'clock-setup',
			'user-setup',
			'passwd',
			'partman',
			'partman-auto',
			'partman-lvm',
			'partman-auto-lvm',
			'pkgsel',
			'tasksel',
			'timezone',
			]:
			return self.FILTER_SKIP
			
		if not self.isCorrectCond(node):
			return self.FILTER_SKIP

		return self.FILTER_ACCEPT

class OtherNodeFilter_ubuntu(NodeFilter):
	"""
	This class accepts tags that define the
	pre section, post section and the packages
	section in the node XML files. The handlers
	for these are present in the Generator class.
	"""
	def acceptNode(self, node):
		if node.nodeName == 'kickstart':
			return self.FILTER_ACCEPT

		if node.nodeName not in [
			'cluster',
			'package',
			'patch',
			'pre',
			'late_command',
			'grub_installer',
			'finish_install',
			'post',
			]:
			return self.FILTER_SKIP

		if not self.isCorrectCond(node):
			return self.FILTER_SKIP
			
		return self.FILTER_ACCEPT

class Generator_ubuntu(Generator):

	def __init__(self):
		Generator.__init__(self)	
		self.ks                 = {}
		self.ks['order']	= []
		self.ks['main']         = []
		self.ks['packages']     = []
		self.ks['finish']	= []
		self.ks['pre']          = []
		self.ks['post']         = []
		self.finish_section     = 0
		self.log = '/var/log/stack-install.log'
	
	##
	## Parsing Section
	##
	
	def parse(self, xml_string):
		import cStringIO
		xml_buf = cStringIO.StringIO(xml_string)
		doc = xml.dom.ext.reader.Sax2.FromXmlStream(xml_buf)
		filter = MainNodeFilter_ubuntu(self.attrs)
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT,
			filter, 0)
		node = iter.nextNode()
		while node:

			if node.nodeName == 'kickstart':
				self.handle_kickstart(node)
			elif node.nodeName == 'main':
				#print ('printing node name in main while 2 %s' ,node.nodeName)
				child = iter.firstChild()
				while child:
					self.handle_mainChild(child)
					child = iter.nextSibling()
			node = iter.nextNode()

		filter = OtherNodeFilter_ubuntu(self.attrs)
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT,
			filter, 0)
		node = iter.nextNode()
		while node:
			if node.nodeName != 'kickstart':
				self.order(node)
				eval('self.handle_%s(node)' % (node.nodeName))
			node = iter.nextNode()


	# <kickstart>
	
	def handle_kickstart(self, node):
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

