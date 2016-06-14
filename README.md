Here is Phase 2 of the Ubuntu installation on Stacki.
More better than Phase 1, automates a bunch of things.
Not as most better than Phase 3 (detailed below), 
which someday we may get to if someone cuts us a check.

The ubuntu-bridge roll allows you to automatically
install a minimal version of Ubuntu Server from Trusty 
to the most recent.  Don't ask me about the desktop 
version because I have no idea what that will do. 

Requirements:

This pallet.
A license.
An Ubuntu-Server iso from Trusty, Wily, or Xenial.
stacki-pro pallet.
Stacki 3.2 or greater. It won't work with 3.1 or less.

Setup:

% Install a license

# rpm -ivh stackiq-license.rpm

% Add bridge pallet

# stack add pallet ubuntu-bridge-3.1-7.x.x86_64.disk1.iso 

% List your pallet to make sure it's there

# stack list pallet

% Add an ubuntu box (can be named anything but the "os=ubuntu" must be given)

# stack add box ubuntu os=ubuntu

% Add an ubuntu iso.

#  stack add pallet ubuntu-14.04.4-server-amd64.iso

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

% Set the installaction.

# stack list bootaction | grep ubuntu
# stack set host installaction backend action=ubuntu.trusty

% Install
# stack set host boot backend action=install

% Now reboot them.

Bask in Ubuntu-ness.


Extras:

% Changing the distribution.

If you want a different Ubuntu Distribution, just add the new iso 
as a pallet. 

Disable the old iso and enable the new one.

Rerun the "run pallet" command and the attributes and such will
be reset.

Reset your machines:

stack disable pallet Ubuntu-Server box=ubuntu-box
stack enable pallet Ubuntu-Server release=Wily box=ubuntu-box
stack run pallet ubuntu-bridge | bash
stack set host installaction backend action=ubuntu.wily
stack set host boot backend action=install

Then reboot.

If you want to have multiple distributions on different machines, 
change the Ubuntu attrs at the host level. To see what you have to 
do:

# stack list attr | grep -i ubuntu

And set those for the hosts you want.
You'll have to set the installaction too.

The Future:

A bunch of stuff should be done to make Ubuntu install with all 
the perks and superdoublechocolateawesomeness we use when 
installing RHEL/CentOS.

Here is the Phase 3 list in no particular order:

- do we do pressed+kickstart or stick with preseed?
- parallel formatting
- using the tracker
- putting in https!
- more partitioning, drop in an expert partition, 
- don’t overwrite data disks 
- convert database partition setting to ubuntu partition
- move partitioning to kickstart.
- what’s the kickstart preseed interplay
- ordering of debian installer commands?
- preseed to properly do the number of cpus
- Oh and some other stuff.
- We could integrate this will salt, shouldn't be hard.
