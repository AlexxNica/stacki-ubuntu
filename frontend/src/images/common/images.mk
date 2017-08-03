# @SI_Copyright@
# @SI_Copyright@

YUMLIST = MegaCLI storcli hpssacli 	\
		stack-pylib		\
		foundation-python	\
		foundation-python-xml	\
		stack-command

LOCALYUMLIST = stacki-ubuntu-frontend-command \
		stacki-ubuntu-frontend-pylib

RPMLOC = $(wildcard ../common/RPMS/*.rpm ./RPMS/*.rpm)
TEMPDIR := $(shell mktemp -d)
RPMLOC += $(shell repoquery --location $(YUMLIST))

PALLET_PATCH_DIR = /opt/stack/Ubuntu-pallet-patches/$(UBUNTU_VERSION)

localrepo:
	mkdir -p $(CURDIR)/localrepo
	ln -fs $(REDHAT.RPMS) $(CURDIR)/localrepo 
	createrepo $(CURDIR)/localrepo
	@echo -e "[localdir] \n\
name=local \n\
baseurl=file://$(CURDIR)/localrepo\n\
assumeyes=1 \n\
gpgcheck=0 \n\
enabled=0" > localdir.repo
localrepo:
RPMLOC += $(shell repoquery --repoid=localdir -c localdir.repo --location $(LOCALYUMLIST))

dirs:
	@mkdir -p $(CURDIR)/ubuntu-stacki

#rpminst: localrepo
#	rpm --dbpath $(TEMPDIR) -ivh --nodeps --force --badreloc \
#		--relocate=/=$(CURDIR)/ubuntu-stacki $(RPMLOC)
#	find $(CURDIR)/ubuntu-stacki -name '*.pyc' -exec rm -fr {} \;
#	find $(CURDIR)/ubuntu-stacki -name '*.pyo' -exec rm -fr {} \;
#	rm -rf $(TEMPDIR)

#rpminst:

debinst:
	( \
	pwd; \
	for f in `ls ../common/PKGS`; do \
		dpkg-deb -x ../common/PKGS/$$f ../common/DEBS; \
	done; \
	)
	pwd;
	rsync -qlavzup ../common/DEBS/* $(CURDIR)/ubuntu-stacki/;

build: dirs rpminst debinst
	@echo "Building ubuntu-stacki.img"
	# SymLink /usr/bin/python to foundation-python
	mkdir -p $(CURDIR)/ubuntu-stacki/usr/bin
	ln -fs /opt/stack/bin/python $(CURDIR)/ubuntu-stacki/usr/bin/python
	ln -fs /usr/bin/vim.tiny $(CURDIR)/ubuntu-stacki/usr/bin/vi
	# Patch the ubuntu-stacki image
	-(cd ../common/ubuntu-stacki.img-patches && \
		(find . -type f  | cpio -pudv ../../$(UBUNTU_VERSION)/ubuntu-stacki/) )
#	-(cd ubuntu-stacki.img-patches && (find . -type f | cpio -pudv ../ubuntu-stacki/) )
	$(EXTRACT) initrd.xenial | ( cd ubuntu-stacki; cpio -iudcm ) 
	(				\
		cd ubuntu-stacki;	\
		rm -f lib/libuuid* lib/libblkid* lib/libnl* lib/libgcrypt* lib/libgpg-error.so.0; \
		find . | cpio -oc | gzip -c - > ../ubuntu-stacki.img; \
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	mkdir -p $(ROOT)/$(PALLET_PATCH_DIR)
	$(INSTALL) -m0644 linux $(ROOT)/$(PKGROOT)/ubuntu-linux-$(UBUNTU_VERSION)-$(ARCH)
	$(INSTALL) -m0644 ubuntu-stacki.img $(ROOT)/$(PKGROOT)/initrd.$(UBUNTU_VERSION)
#	$(INSTALL) -m0644 ubuntu-stacki.img $(ROOT)/$(PKGROOT)/ubuntu-initrd-$(UBUNTU_VERSION)-$(ARCH)
	# Copy over patch files
#	cd Ubuntu-pallet-patches && (find . -type f | cpio -pudv $(ROOT)/$(PALLET_PATCH_DIR))
	$(INSTALL) -m0644 ubuntu-stacki.img $(ROOT)/$(PALLET_PATCH_DIR)/boot/x86_64/ubuntu-stacki.img

clean::
	rm -rf $(CURDIR)/localrepo
	rm -rf $(CURDIR)/localdir.repo
	rm -rf $(CURDIR)/stacki
	rm -rf $(CURDIR)/ubuntu-stacki.img
	rm -rf $(CURDIR)/ubuntu-stacki
	rm -rf ../common/DEBS/*
