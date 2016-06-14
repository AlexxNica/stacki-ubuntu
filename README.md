Requirements:
	- ubuntu-bridge pallet (e.g., ubuntu-bridge-1.0-7.x.x86_64.disk1.iso)
	- Ubuntu-Server iso from Trusty, Wily, or Xenial (e.g., ubuntu-16.04-server-amd64.iso)
	- Stacki Pro license (maybe)
	- stacki-pro pallet v3.2 or greater (e.g., stacki-pro-3.2-7.x.x86_64.disk1.iso)


Setup:

% Install stacki-pro pallet

	# stack add pallet stacki-pro-3.2-7.x.x86_64.disk1.iso
	# stack enable pallet stacki-pro
	# stack run pallet stacki-pro | bash

% Reboot the frontend

	# init 6

% Add an ubuntu iso.

	#  stack add pallet ubuntu-16.04-server-amd64.iso

% Add an ubuntu box (can be named anything but the "os=ubuntu" must be given)

	# stack add box ubuntu os=ubuntu

% Install bridge pallet

	# stack add pallet ubuntu-bridge-1.0-7.x.x86_64.disk1.iso

% Add pallets to the box

	# stack enable pallet stacki stacki-pro Ubuntu-Server ubuntu-bridge box=ubuntu

% Set the frontend to the ubuntu box

	# stack set host box frontend box=ubuntu

% Run the pallet.

	# stack run pallet ubuntu-bridge

% Run it for real.

	# stack run pallet ubuntu-bridge | bash

% Set the frontend back to default box

	# stack set host box frontend box=default

% Assign nodes to the ubuntu box

	# stack set host box backend box=ubuntu

% Set the installaction

	# stack list bootaction | grep ubuntu
	# stack set host installaction backend action=ubuntu.xenial

% Install

	# stack set host boot backend action=install

% Reboot the backend nodes
