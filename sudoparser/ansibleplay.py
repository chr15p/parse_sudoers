import sys
import re
import yaml
from collections import OrderedDict


class AnsiblePlaybook:
    def __init__(self, sudoparser, description=None):
        self.parser = sudoparser
        self.outputfile = sys.stdout
        self.use_groups = False
        self.description = description

    def dump(self):
#        print(self.parser.aliases['host'])
#        print(self.parser.aliases['runas'])
#        print(self.parser.aliases['user'])
#        print(self.parser.aliases['cmnd'])
#        
#        cmds = set()
#        for i in self.parser.rules:
#            cmds = cmds.union(i.get_raw_command_expanded())
#        cmds.remove('ALL')
#        #print(cmds)
#        for c in cmds:
#            #print(c)
#            self.dump_command(c)
#
#        for group,commands in self.parser.aliases['cmnd'].items():
#            print(self.dump_cmdgroup(group, commands))
#                
#
#        return

        noalias_dumper = yaml.dumper.SafeDumper
        noalias_dumper.ignore_aliases = lambda self, data: True

        commands = []
        cmdgroup = []
        #print(self.parser.aliases['cmnd'])
        for group,cmds in self.parser.aliases['cmnd'].items():
            cmdgroup.append(self.dump_cmdgroup(group, cmds))
            if cmds[0] != "!":
                commands.extend(cmds)

        allrules = []
        for rule in self.parser.rules:
            ansiblerule = self.dump_sudorule(rule) 
            if ansiblerule != None:
                allrules.append(ansiblerule)
            if self.use_groups == False:
                commands.extend(rule.get_command_expanded())
            else:
                commands.extend(rule.get_commands())
        
        cmndtasks = [ self.dump_command(c) for c in set(commands) if c != "ALL" ]
        if cmndtasks != []:
            print(yaml.dump(cmndtasks, sort_keys=False, default_flow_style=False, Dumper=noalias_dumper))
        if cmdgroup != []:
            print(yaml.dump(cmdgroup, sort_keys=False, default_flow_style=False, Dumper=noalias_dumper))
        if allrules != []:
            print(yaml.dump(allrules, sort_keys=False, default_flow_style=False, Dumper=noalias_dumper))


    def dump_command(self, cmd):
        cmd = {
            "name": cmd,
            "ipasudocmd": {
                "ipaadmin_principal": "{{ ipa_user }}",
                "ipaadmin_password": "{{ ipa_pass }}",
                "name": cmd,
                "state": "present" }}
        if self.description != None:
            cmd["ipasudocmd"]["description"] = self.description
        
        return cmd
 

    def dump_cmdgroup(self, group, cmnds):
        cmdgroup = {
            "name": group,
            "ipasudocmdgroup": {
                "ipaadmin_principal": "{{ ipa_user }}",
                "ipaadmin_password": "{{ ipa_pass }}",
                "name": group,
                "sudocmd": cmnds,
                "state": "present",
            }}
        if self.description != None:
            cmdgroup["ipasudocmdgroup"]["description"] = self.description

        return cmdgroup
 

    def dump_sudorule(self, rule):
        hostRE = re.compile('^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$', re.IGNORECASE)
        validhosts = [ h for h in rule.get_allowed_hosts() if hostRE.match(h)]
        if validhosts == []:
            return None

        sudorule = {
            "name":  rule.rulename,
            "ipasudorule": {
                "ipaadmin_principal": "{{ ipa_user }}",
                "ipaadmin_password": "{{ ipa_pass }}",
                "state": "present",
                "name": rule.rulename,
            }}

        if self.description != None:
            sudorule["ipasudorule"]["description"] = self.description

        opts = rule.get_sudo_options()
        if opts:
            sudorule["ipasudorule"]["sudooption"] = opts

        self.dump_ansible_type(sudorule["ipasudorule"], "cmd", "", rule.get_command_expanded())
        self.dump_ansible_type(sudorule["ipasudorule"], "host", '+', validhosts)
        self.dump_ansible_type(sudorule["ipasudorule"], "user", '%+', rule.get_allowed_users())

        return sudorule


    def dump_ansible_type(self, taskdict, objtype, groupchar, object_array):
        for obj in object_array:
            if str(obj) == "ALL":
                taskdict[objtype + "category"] = "all"
                return
            if obj[0] in groupchar:
                if objtype =="host":
                    param = "hostgroup"
                elif objtype == "user":
                    param = "group"
                else:
                    param = objtype
                if taskdict.get(param) == None:
                    taskdict[param] = []

                taskdict[param].append(str(obj[1:]))
            else:
                if taskdict.get(objtype) == None:
                    taskdict[objtype] = []
                taskdict[objtype].append(str(obj))

