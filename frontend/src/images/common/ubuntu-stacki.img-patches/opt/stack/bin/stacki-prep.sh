#!/bin/sh
log "======================="
log "Starting F08-stacki ..."
log "======================="

#=============================================
# do the voodoo that we do
#---------------------------------------------

/opt/stack/bin/python /opt/stack/bin/stacki-profile.py

#
# stacki-profile.py outputs the file /tmp/stacki-profile.xml which contains
# two "chapters":
#
#	1) "yast" chapter. This is the autoinst.xml file.
# 	2) "stacki" chapter. This is python code that will be imported into
#		other programs that run during the install in order to
#		configure the system.
#

cat /tmp/stacki-profile.xml \
	| /opt/stack/bin/stack list host profile chapter=preseed \
	> /tmp/profile/preseed.xml

mkdir -p /tmp/stack_site/

cat /tmp/stacki-profile.xml \
	| /opt/stack/bin/stack list host profile chapter=stacki \
	> /tmp/stack_site/__init__.py

/opt/stack/bin/python /opt/stack/bin/stacki-status.py install profile parsed

#
# configure the hardware disk array controller first
#
/opt/stack/bin/python /opt/stack/bin/storage-controller-client.py

#
# then configure the partitions
#
/opt/stack/bin/python /opt/stack/bin/output-partition.py > /tmp/partition.xml

#
# give ourselves the ability to hold the installation prior to the start of yast
#
grep stack-debug /proc/cmdline 2>&1 > /dev/null
if [ $? -eq 0 ]
then
	touch /tmp/wait
	while [ -f /tmp/wait ]
	do
		echo "Stacki debug wait loop - remove /tmp/wait to continue"
		sleep 1
		/opt/stack/bin/python /opt/stack/bin/stacki-status.py install wait 1
	done
fi

