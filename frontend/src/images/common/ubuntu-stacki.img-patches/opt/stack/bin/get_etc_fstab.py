#!/opt/stack/bin/python
import subprocess
import tempfile

cmd = "list-devices disk"
p = subprocess.Popen(cmd.split(), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
o, e = p.communicate()
disks = o.split()
fstab_contents = None

print disks

# Search for /etc/fstab
for disk in disks:
	cmd = "lsblk -nro NAME %s" % disk
	p = subprocess.Popen(cmd.split(), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	parts = p.communicate()[0].split()
	print(parts)

	for part in parts:
		partname = '/dev/' + part
		if partname == disk:
			continue
		tmpfile = tempfile.mkdtemp()

		# Mount file
		mnt = 'mount %s %s' % (partname, tmpfile)
		mnt_p = subprocess.Popen(mnt.split(), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print(mnt_p.communicate()[1])
		fstab_path = tmpfile + '/etc/fstab'

		try:
			f = open(fstab_path, 'r')
			print('no exception while %s' % partname)
			fstab_contents = f.readlines()
			f.close()
		except:
			print ('exception while %s' % fstab_path)
			pass

		umnt = 'umount %s' % tmpfile
		umnt_p = subprocess.Popen(umnt.split(), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		rmdir = 'rm -rf %s' % tmpfile
		rmdir_p = subprocess.Popen(rmdir.split(), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		if fstab_contents:
			break

	if fstab_contents:
		break

old_fstab = open('/tmp/old_etc_fstab.txt', 'w+')
for line in fstab_contents:
	# Ignore comments
	if line.startswith('#'):
		continue
	fstab_entry = line.split()
	
	if line and len(fstab_entry) > 4:
		mntpt = line[1]
		#
		# Write entry to fstab only if mountpoint not in 
		# /, /var/, /boot
		#
		if mntpt not in ['/', '/var', '/boot']:
			old_fstab.write(line)

old_fstab.close()