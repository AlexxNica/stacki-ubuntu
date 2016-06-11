<?xml version="1.0" standalone="no"?>
<graph>

	<description>
	Backend appliance graph for Stacki.
	</description>

	<order head="ubuntu-base">
		<tail>ubuntu-netcfg</tail>
	</order>

	<order head="ubuntu-netcfg">
		<tail>ubuntu-mirror</tail>
	</order>

        <order head="ubuntu-mirror">
                <tail>ubuntu-aptsetup</tail>
        </order>

        <order head="ubuntu-aptsetup">
                <tail>ubuntu-clock-setup</tail>
        </order>

	<order head="ubuntu-clock-setup">
		<tail>ubuntu-partman</tail>
	</order>

	<order head="ubuntu-partman">
		<tail>ubuntu-user-setup</tail>
	</order>

	<order head="ubuntu-user-setup">
                <tail>ubuntu-passwd</tail>
        </order>

	<order head="ubuntu-passwd">
		<tail>ubuntu-tasksel</tail>
	</order>

	<order head="ubuntu-tasksel">
                <tail>ubuntu-pkgsel</tail>
        </order>

	<order head="ubuntu-pkgsel">
		<tail>ubuntu-late-command</tail>
	</order>

	<order head="ubuntu-late-command">
                <tail>ubuntu-serial-console</tail>
        </order>

	<order head="ubuntu-late-command">
                <tail>ubuntu-grub-installer</tail>
        </order>

	<order head="ubuntu-grub-installer">
		<tail>ubuntu-finish-install</tail>
	</order>

	<edge from="stacki-pro-client" os="ubuntu">
		<to>ubuntu-base</to>
		<to>ubuntu-netcfg</to>
		<to>ubuntu-mirror</to>
		<to>ubuntu-apt-setup</to>
		<to>ubuntu-clock-setup</to>
		<to>ubuntu-user-setup</to>
		<to>ubuntu-passwd</to>
		<to>ubuntu-partman</to>
		<to>ubuntu-tasksel</to>
		<to>ubuntu-pkgsel</to>
		<to>ubuntu-late-command</to>
		<to>ubuntu-serial-console</to>
		<to>ubuntu-grub-installer</to>
		<to>ubuntu-finish-install</to>
	</edge>
	<edge head="ubuntu-late-command">
		<to>ubuntu-serial-console</to>
	</edge>
	<order head="stacki-pro-server">
		<to>ubuntu-server</to>
	</order>

	<edge from="stacki-pro-server">
		<to>ubuntu-server</to>
	</edge>

</graph>
