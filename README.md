# parse_sudoers
A tool to parse existing sudoers files and write them out as ansible tasks suitable for feeding into IdM or FreeIPA (and possibly other formats)

### usage:
`parse_sudoers -f [sudoers file] [-s | -a]`

with the -a option the output will be presented as standard ansible tasks suitable for running against an existing IdM (or FreeIPA) server.

with the -s option it will produce a set of highly simplified sudoers file, with all aliases expanded, multiple users, hosts, and commands split into seperate lines etc. This is designed to be helpful for auditing existing sudo rules. 

## tests:
A simple set of tests can be run using
```
[chrisp@host parse_sudoers]$ ./runtests.sh
```
That simply runs through the sudoers files in the tests/ directory and diffs the parse_sudoers.py output against the expected output.

A more substantive test can be run by setting up the inventory file to point to a freeipa server, and then running 
```
[chrisp@host parse_sudoers]$ ./run_ansible_tests.sh
```
which will generate playbooks for every test in the tests/ directory and then run those playbooks against the ipa server. If the rules set up load successfully and run then teh test is passed.


### examples:
There are two sudoers files included as test cases test_simple_sudoers ( a simple setup with a user "fencer" given permissions to fence VMs in a pacemaker HA cluster) and test_complicated_sudoers (a pathologically insane file that tries to do every trick in the sudoers book to test the parser to its limits)


Output sudo rules:
```
[chrisp@host parse_sudoers]$ ./parse_sudoers.py -f test_simple_sudoers -s
 Host_Alias      HACLUSTER = cluster1,cluster2,cluster3
 
 root    ALL = ( ALL )  ALL
 %wheel  ALL = ( ALL )  ALL
 fencer  cluster1,cluster2,cluster3 = ( root ) NOPASSWD: /usr/bin/virsh
``` 

The same file output as ansible tasks
``` 
 [chrisp@host parse_sudoers]$ ./parse_sudoers.py -f test_simple_sudoers -a
- name: add commands
  ipasudocmd:
    ipaadmin_principal: '{{ ipa_user }}'
    ipaadmin_password: '{{ ipa_pass }}'
    name:
    - /usr/bin/virsh
    state: present
    description: generated from test_simple_sudoers

- name: test_simple_sudoers.77-1.1
  ipasudorule:
    ipaadmin_principal: '{{ ipa_user }}'
    ipaadmin_password: '{{ ipa_pass }}'
    state: present
    name: test_simple_sudoers.77-1.1
    user:
    - root
    hostcategory: all
    runasusercategory: all
    cmdcategory: all
- name: test_simple_sudoers.84-1.1
  ipasudorule:
    ipaadmin_principal: '{{ ipa_user }}'
    ipaadmin_password: '{{ ipa_pass }}'
    state: present
    name: test_simple_sudoers.84-1.1
    group:
    - wheel
    hostcategory: all
    runasusercategory: all
    cmdcategory: all
- name: test_simple_sudoers.100-1.1
  ipasudorule:
    ipaadmin_principal: '{{ ipa_user }}'
    ipaadmin_password: '{{ ipa_pass }}'
    state: present
    name: test_simple_sudoers.100-1.1
    user:
    - fencer
    host:
    - cluster1
    - cluster2
    - cluster3
    runasuser:
    - root
    sudooption:
    - '!authenticate'
    allow_sudocmd:
    - /usr/bin/virsh
``` 
