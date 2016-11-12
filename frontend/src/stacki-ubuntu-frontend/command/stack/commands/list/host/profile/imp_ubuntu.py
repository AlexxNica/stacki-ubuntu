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

import string
from xml.sax import saxutils
from xml.sax import handler
from xml.sax import make_parser
from stack.license import *
import stack.commands
import stack.ubuntu.gen


class ProfileHandler(handler.ContentHandler,
                     handler.DTDHandler,
                     handler.EntityResolver,
                     handler.ErrorHandler):

	def __init__(self):
		handler.ContentHandler.__init__(self)
                self.recording = False
                self.text      = ''
                self.chapters  = {}
                self.chapter   = None

	def startElement(self, name, attrs):
                if name == 'chapter':
                        self.chapter   = self.chapters[attrs.get('name')] = []
                        self.recording = True

	def endElement(self, name):
                if self.recording:
                        self.chapter.append(self.text)
                        self.text = ''

                if name == 'chapter':
                        self.recording = False

	def characters(self, s):
                if self.recording:
                        self.text += s

        def getChapter(self, chapter):
                doc = []
                if chapter in self.chapters:
                        for text in self.chapters[chapter]:
                        	doc.append(text.strip())
                return doc


class Implementation(stack.commands.Implementation):


	@licenseCheck
	def run(self, args):

                host        = args[0]
                xmlinput    = args[1]
                profileType = args[2]
                isDocument  = args[3]
                profile     = []
		generator   = stack.ubuntu.gen.Generator()

                generator.setProfileType(profileType)
		generator.parse(xmlinput)

                profile.append('<?xml version="1.0" standalone="no"?>')
                profile.append('<profile-%s os="ubuntu">' % generator.getProfileType())
		profile.append('<chapter name="meta">')
                profile.append('\t<section name="order">')
                for line in generator.generate('order'):
	                profile.append('%s' % line)
                profile.append('\t</section>')
                profile.append('\t<section name="debug">')
                for line in generator.generate('debug'):
                        profile.append(line)
                profile.append('\t</section>')
		profile.append('</chapter>')

                if generator.getProfileType() == 'native':
                        profile.append('<chapter name="preseed">')
                        for section in [ 'main',
                                         'packages',
                                         'post',
                                         'finish']:
                                profile.append('\t<section name="%s">' % section)
                                for line in generator.generate(section):
                                        profile.append(line)
                                profile.append('\t</section>')
                        profile.append('</chapter>')

                elif generator.getProfileType() == 'shell':
                        profile.append('<chapter name="bash">')
                        profile.append('#! /bin/bash')
                        for section in [ 'packages',
                                         'post',
					 'boot' ]:
                                profile.append('\t<section name="%s">' % section)
                                for line in generator.generate(section):
                                        profile.append(line)
                                profile.append('\t</section>')
                        profile.append('</chapter>')


                profile.append('</profile-%s>' % generator.getProfileType())

                if not isDocument:
			parser  = make_parser()
                        handler = ProfileHandler()
			parser.setContentHandler(handler)
                        for line in profile:
                                parser.feed('%s\n' % line)
                        profile = handler.document()

                for line in profile:
                        self.owner.addOutput(host, line)


RollName = "stacki"
