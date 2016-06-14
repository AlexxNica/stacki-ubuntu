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
