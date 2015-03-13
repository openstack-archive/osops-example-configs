# MIT CSAIL OpenStack Configurations

Our cloud is running a fairly simple non-HA configuration over approx
75 hypervisor nodes.

This is primarily a private research cloud for
<http://www.csail.mit.edu>, though it does hold web and other
'production' services.

We initially installed Essex on Ubuntu 12.04 and have progressively
updated.  As of this writing all nodes are Ubuntu 14.04 running Juno.

There is a single controller node which also serves as Network node,
MySQL DB server and Cinder volume server (actual volumes are provided
by a mix of EqualLogic SAN and Ceph RBD drivers).

# Caveat Hackor

This is *as running* config that have evolved over six OpenStack
releases. It is not claimed to be clean or necessarily 100% best
practice. In fact it is nearly guaranteed that there are options in
the config files that are deprecated and possibly removed in current
release or otherwise irrelevant to the actual functioning of the
system.

Read at your own risk.

# Directory Layout

There's a first level directory for each node type. Currently just
controller and compute, but we're hoping to break services out and
move to an HA controller setup probably in the Kilo time frame.

Below that directory structure mimics layout from the root directory
of that type node for example nova.conf on the compute node will be
`compute/etc/nova/nova.conf`

# Notes on OpenStack Projects Used

## Keystone

Uses UUID tokens with MySQL identity backend and memcached token
backend.

This is run through Apache mod_wsgi

Primary access via https on 5001 and 35358 though still listening via
http on standard ports this is still buried in some internal URLs.

## Glance

APIs run via eventlet server

Some historical images use file backend, currently defaults to
Ceph RBD

## Nova

Libvirt KVM using Ceph RBD for ephemeral storage

## Cinder

Single controller fronting both EqualLogic SAN storage and Ceph RBD
storage.

## Neutron

ML2/OVS with shared VLAN based provider network(s) using public ipv4
addressing. Projects may create private GRE based overlay networks

No L3 agent -- routing provided by core, non-openstack, infrastructure

No Floating IP -- fixed IPs are public & we provide the ability to
assign specific IPs at boot, IPAM and DNS are handled with legacy
tools outside OpenStack for more on this see our user facing
documentation <http://tig.csail.mit.edu/wiki/TIG/OpenStack#Network>

## Horizon

Mostly stock with a small extension to allow specifying fixed IP on
system start up.  This is a bit of a hack and only for when launching a
single instance with a single vNIC, but it does cover our needs.

## Heat

Added to our world during Icehouse time frame, it's there, it mostly
works but is not yet much used.
 
