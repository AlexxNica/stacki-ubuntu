Do this:

% Add bridge pallet

# stack add pallet ubuntu-bridge-3.1-7.x.x86_64.disk1.iso 

% Force the rpm install of stack-ubuntu
# rpm -ivh --force /state/partition1/stack/pallets/ubuntu-bridge/3.1/redhat/x86_64/RPMS/stack-ubuntu-3.1-1.0.x86_64.rpm

% List your pallet to make sure it's there

# stack list pallet

% Add an ubuntu box (can be named anything but the "os=ubuntu" must be given)

# stack add box ubuntu os=ubuntu

% Add an ubuntu iso.

#  stack add pallet ubuntu-14.04.4-server-amd64.iso

% Add pallets to the box

# stack enable pallet stacki Ubuntu-Server ubuntu-bridge box=ubuntu

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

% Set the installaction.

# stack list bootaction | grep ubuntu
# stack set host installaction backend action=ubuntu.trusty

% Install
# stack set host boot backend action=install

% Now reboot them.

Please note, if your interfaces are not named "eth" something, you'll
get your machine installed by network won't work. So yeah, do that.

This is true for Trusty. I will check Wily and Xenial.
