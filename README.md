# Yes! Ubuntu!

You asked, we listened, and now we're releasing Stacki Ubuntu into the open source Stacki tree. You can now automatically install Ubuntu via a preseed network install to backend machines from a Stacki frontend. The only thing you have to do is prep your frontend.

It's not as full-featured as what we do with CentOS/RHEL variants, but we will be building on what we have done with Ubuntu to be commensurate with CentOS and SLES in the coming weeks. Stay tuned.

In the meantime, to get you started:

# Requirements
- A Stacki frontend with Stacki 4.0. It likely won't work on anything less than 4.0.
- stacki-ubuntu-frontend pallet
- stacki-ubuntu-backend pallet
- Ubuntu-Server iso from Trusty, Wily, Xenial, or Yakkety (e.g., ubuntu-16.04-server-amd64.iso) (you can do multiple versions)

## Setup
Download stacki-ubuntu-pallets

```
wget https://s3.amazonaws.com/stacki/public/pallets/4.0/open-source/stacki-ubuntu-frontend-4.0_20170414_c4aff2a-7.x.x86_64.disk1.iso 
wget https://s3.amazonaws.com/stacki/public/pallets/4.0/open-source/stacki-ubuntu-backend-4.0_20170414_c4aff2a-7.x.x86_64.disk1.iso
```

You have to add and run the stacki-ubuntu-frontend pallet before adding the stacki-ubuntu-backend pallet or the Ubunto-Server iso. 
So let's do that:

Add stacki-ubuntu frontend pallet:

	# stack add pallet stacki-ubuntu-frontend-4.0_20170414_c4aff2a-7.x.x86_64.disk1.iso
	# stack enable pallet stacki-ubuntu-frontend
	# stack run pallet stacki-ubuntu-frontend | bash

Now we can safely add the stacki-ubuntu-backend pallet:

	# stack add pallet stacki-ubuntu-backend-4.0_20170414_c4aff2a-7.x.x86_64.disk1.iso

Add an Ubuntu iso. You can find the downloads page for version 16.04.2 which I am using, here: http://releases.ubuntu.com/16.04.2/ubuntu-16.04.2-server-amd64.iso

	#  stack add pallet ubuntu-16.04.2-server-amd64.iso

Add an Ubuntu box (can be named anything but the "os=ubuntu" must be given)

	# stack add box ubuntu-xenial os=ubuntu

Add the Ubuntu pallets to the ubuntu box.

	# stack enable pallet stacki-ubuntu-backend Ubuntu-Server box=ubuntu-xenial


Run the frontend pallet again. (Trust me on this.)

	# stack run pallet stacki-ubuntu-frontend | bash

Assign nodes to the ubuntu box

	# stack set host box backend box=ubuntu-xenial

Set the installaction

	# stack list bootaction | grep ubuntu
	# stack set host installaction backend action=ubuntu.xenial

Install

	# stack set host boot backend action=install

Reboot the backend nodes

## What you get

Right now all you get is a machine with one iterface plumbed and default partitions of /, /var, swap, and /state/partition1. To get a different partitioning scheme, you'll have to use a cart and use a replace-ubuntu-partman.xml and put your own partitioning in. The "nukedisks" flag is recognized for the default partitions.

The next release will do partitioning and plumb all networks if set up correctly in the database. Let us know what else you would like to see. 

## Changing the distribution.

If you want a different Ubuntu Distribution, just add the new iso 
as a pallet. 

Disable the old iso and enable the new one.

Rerun the "run pallet" command and the attributes and such will
be reset.

Reset your machines:

	# stack disable pallet Ubuntu-Server box=ubuntu-box
	# stack enable pallet Ubuntu-Server release=Wily box=ubuntu-box
	# stack run pallet stacki-ubuntu-frontend | bash
	# stack set host installaction backend action=ubuntu.wily
	# stack set host boot backend action=install

Then reboot.

If you want to have multiple distributions on different machines, 
change the Ubuntu attrs at the host level. To see what you have to 
do:

	# stack list attr | grep -i ubuntu

And set those for the hosts you want.
You'll have to set the installaction too.

## The Future

A bunch of stuff should be done to make Ubuntu install with all 
the perks and superdoublechocolateawesomeness we use when 
installing RHEL/CentOS.

Here is the Phase 3 list in no particular order:

- Parallel formatting of disk.
- Partitioning out of the database.
- Using the tracker
- Putting in https!
- Controller configuration.
- Don’t overwrite data disks (lazyformat)
- convert database partition setting to ubuntu partition
- Preseed to properly do the number of cpus
- Discovery mode.
- XML file fixes to obviate preseed issues.

### Questions you're going to ask that I have no idea about:
You: Does this work with Ubuntu Desktop? 
Me: I have no idea. Try it. See what happens.

You: Does this work with Debian?
Me: Not yet. Shouldn't be hard. Maybe soon. Maybe not.

You: Does this work on my Raspberry Pi?
Me: Really? We just released this. Mabye soon. Maybe not.

You: Can I mirror the entire Ubuntu repo?
Me: Yes. It's a horror and you have to have a big disk. If you read this far, ask on the Stacki Slack channel, and I'll give you an answer/rant. You don't get one without the other.

You: Can you add X so I can do Y because it would be awesome to show my Zs? 
Me: Can/do you pay us for professional services? Then, no. 
