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
        noalias_dumper = yaml.dumper.SafeDumper
        noalias_dumper.ignore_aliases = lambda self, data: True


        #for i in self.parser.rules:
        #    print(i.dump())
        #return

        # parse commands out of serialised rules

        # turn the command aliases into gmdgroups
        commands = []
        cmdgroup = []

        for rule in self.parser.rules:
            commands += rule.get_raw_command_expanded()
        cmndtasks = [ self.dump_command(c) for c in set(commands) if c != "ALL" ]

        #print(self.parser.aliases['cmnd'])
        for group,cmds in self.parser.aliases['cmnd'].items():
            cmdgroup.append(self.dump_cmdgroup(group, cmds))
            #if cmds[0] != "!":
            #    commands.extend(cmds)

        # turn the serialised rules into ansible sudorules
        allrules = []
        for rule in self.parser.rules:
            ansiblerule = self.dump_sudorule(rule) 
            if ansiblerule != None:
                allrules.append(ansiblerule)
            #if self.use_groups == False:
            #    commands.extend(rule.get_command_expanded())
            #else:
            #    commands.extend(rule.get_commands())

        
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

        #print(rule.__dict__)
        #print([f for f in dir(rule) if f.startswith('get_')])
        #if rule.description != None:
        #    sudorule["ipasudorule"]["description"] = rule.description

        if rule.get_allowed_users():
            if "ALL" in rule.get_allowed_users():
                sudorule["ipasudorule"]["usercategory"] = "all"
            else:
                sudorule["ipasudorule"]["user"] = rule.get_allowed_users()

        if rule.get_allowed_groups():
            sudorule["ipasudorule"]["group"] = rule.get_allowed_groups()
            
        if rule.get_allowed_hosts():
            if "ALL" in rule.get_allowed_hosts():
                sudorule["ipasudorule"]["hostcategory"] = "all"
            else:
                sudorule["ipasudorule"]["host"] = rule.get_allowed_hosts()
        #if rule.get_allowed_hostgroups():
        #    sudorule["ipasudorule"]["hostgroups"] = rule.get_allowed_hostgroups()

        if rule.get_allowed_runas_users():
            if "ALL" in rule.get_allowed_runas_users():
                sudorule["ipasudorule"]["runasusercategory"] = "all"
            else:
                sudorule["ipasudorule"]["runasuser"] = rule.get_allowed_runas_users()

        if rule.get_allowed_runas_groups():
            if "ALL" in rule.get_allowed_runas_groups():
                sudorule["ipasudorule"]["runasgroupcategory"] = "all"
            else:
                sudorule["ipasudorule"]["runasgroupcategory"] = rule.get_allowed_runas_groups()

        if rule.get_sudo_options():
            sudorule["ipasudorule"]["sudooption"] = rule.get_sudo_options()

        
        if rule.get_allowed_commands():
            if "ALL" in rule.get_allowed_commands():
                sudorule["ipasudorule"]["cmdcategory"] = "all"
            else:
                if rule.get_allowed_cmdgroups():
                    sudorule["ipasudorule"]["allow_sudocmdgroup"] = rule.get_allowed_cmdgroups()
                sudorule["ipasudorule"]["allow_sudocmd"] = rule.get_allowed_commands()

        if rule.get_denied_commands():
            sudorule["ipasudorule"]["deny_sudocmd"] = rule.get_denied_commands()


        if rule.get_denied_cmdgroups():
            sudorule["ipasudorule"]["deny_sudocmdgroup"] = rule.get_allowed_commands()
        
    
        #self.dump_ansible_type(sudorule["ipasudorule"], "cmd", "", rule.get_command_expanded())
        #self.dump_ansible_type(sudorule["ipasudorule"], "host", '+', validhosts)
        #self.dump_ansible_type(sudorule["ipasudorule"], "user", '%+', rule.get_allowed_users())

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

