export ROLL		= stacki-ubuntu-frontend

COLOR			= mauve
ISOSIZE			= 0
#RELEASE			= whatever
export RELEASE  	= $(shell /opt/stack/bin/stack list pallet Ubuntu-Server output-header=false | awk '{print $$2}')
