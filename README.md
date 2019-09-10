# parse_sudoers
A tool to parse sudoers and dump out ansible tasks (and possibly other formats)

### usage:
`parse_sudoers -f [sudoers file] [-s | -a]`

with the -a option the output will be presented as standard ansible tasks suitable for running against an existing IdM (or FreeIPA) server.

with the -s option it will produce a set of highly simplified sudoers file, with all aliases expanded, multiple users, hosts, and commands split into seperate lines etc. This is designed to be helpful for auditing existing sudo rules. 


### examples:
Output sudo rules:
```
[chrisp@host parse_sudoers]$ ./parse_sudoers.py -f simple_sudoers -s
 Host_Alias      HACLUSTER = cluster1,cluster2,cluster3
 
 root    ALL = ( ALL )  ALL
 %wheel  ALL = ( ALL )  ALL
 fencer  cluster1,cluster2,cluster3 = ( root ) NOPASSWD: /usr/bin/virsh
``` 

The same file output as ansible tasks
``` 
 [chrisp@host parse_sudoers]$ ./parse_sudoers.py -f simple_sudoers -a
 - ipa_sudocmd:
     ipa_host: '{{ idm_master_hostname }}'
     ipa_pass: '{{ idm_admin_password }}'
     ipa_user: '{{ idm_admin_user }}'
     name: /usr/bin/virsh
   name: /usr/bin/virsh
 
 - ipa_sudorule:
     cmdcategory: all
     hostcategory: all
     ipa_host: '{{ idm_master_hostname }}'
     ipa_pass: '{{ idm_admin_password }}'
     ipa_user: '{{ idm_admin_user }}'
     name: simple_sudoers.77-1.1
     user:
     - root
   name: simple_sudoers.77-1.1
 - ipa_sudorule:
     cmdcategory: all
     hostcategory: all
     ipa_host: '{{ idm_master_hostname }}'
     ipa_pass: '{{ idm_admin_password }}'
     ipa_user: '{{ idm_admin_user }}'
     name: simple_sudoers.84-1.1
     usergroup:
     - wheel
   name: simple_sudoers.84-1.1
 - ipa_sudorule:
     cmd:
     - /usr/bin/virsh
     host:
     - cluster1
     - cluster2
     - cluster3
     ipa_host: '{{ idm_master_hostname }}'
     ipa_pass: '{{ idm_admin_password }}'
     ipa_user: '{{ idm_admin_user }}'
     name: simple_sudoers.100-1.1
     sudoopt:
     - '!authenticate'
     user:
     - fencer
   name: simple_sudoers.100-1.1
``` 
