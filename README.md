# example-configs
Example configurations, sanitized from real environments

Please see the wiki page at https://wiki.openstack.org/wiki/Osops for other osops tools & repos.

How to use:

1) Create directory

2) Add a README.md in that directory describing your environment

3) SANITIZE YOUR CONFIGS BEFORE FIRST COMMIT

4) Add configs, CM descriptions, etc. that make sense from your environment in a logical way

5) Create a Gerrit review of your changes (see http://docs.openstack.org/infra/manual/developers.html for how to.)

# External Example Repositories

Some sites have open versions of their configs and/or config
management systems online in other places.  Here's a list of the ones
we know about:

* https://github.com/bloomberg/chef-bcpc/tree/master/cookbooks/bcpc/templates/default
  Bloomberg's configs are open source (apart from things like ips,
  tokens and such) and in chef templates. Thats what we run in
  production on several clusters at the moment.
  
* https://github.com/blueboxgroup/ursula
  Blue Box has the same, but in Ansible roles. The secret stuff is in
  an internal repo that provides variables to fill in content.
  
* https://github.com/NeCTAR-RC
  NeCTAR uses puppet templates, mainly based on upstream pupet-openstack for a
  multi-site production cloud, and several test clusters. Configs for multiple
  versions are available. Search for puppet-{nova,designate...} repositories.

* https://github.com/jetstream-cloud/Jetstream-Salt-States
  Jetstream-Cloud.org salt states, IU_production branch is used to deploy various
  services

* https://github.com/gfa/os-sample-configs
  Default configs for nova, keystone, cinder, ceilometer and heat.
  For Debian and Ubuntu versions of Havana, Icehouse and Juno.
