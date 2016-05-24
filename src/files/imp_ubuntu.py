import stack.commands
import stack.gen

class Implementation(stack.commands.Implementation):
	def run(self, args):

		host = args[0]
		xml = args[1]

		c_gen = getattr(stack.gen,'Generator_%s' % self.owner.os)
		self.generator = c_gen()
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
		self.owner.addOutput(host, '&lt;profile lang="preseed.cfg"&gt;\n')
		self.get_section = ['main', 'packages', 'post', 'finish']
		
		for section in self.get_section:	
			list += self.generator.generate(section,
				annotation=self.owner.annotation)
		else:
			list += self.generator.generate(self.owner.section,
					annotation=self.owner.annotation)
		self.owner.addOutput(host,
			self.owner.annotate('&lt;section name="preseed.cfg"&gt;'))
		self.owner.addOutput(host, self.owner.annotate('&lt;![CDATA['))
		for i in list:
			self.owner.addOutput(host, i)
		self.owner.addOutput(host, self.owner.annotate(']]&gt;'))
		self.owner.addOutput(host, self.owner.annotate('&lt;/section&gt;'))
		self.owner.addOutput(host, self.owner.annotate('&lt;/profile&gt;'))
