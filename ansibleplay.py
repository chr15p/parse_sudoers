import sys
import re
import yaml


class AnsiblePlaybook:
    def __init__(self, sudoparser):
        self.parser = sudoparser
        self.outputfile = sys.stdout
        self.use_groups = False

    def dump(self):

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
            print(yaml.dump(cmndtasks, default_flow_style=False, Dumper=noalias_dumper))
        if cmdgroup != []:
            print(yaml.dump(cmdgroup, default_flow_style=False, Dumper=noalias_dumper))
        if allrules != []:
            print(yaml.dump(allrules, default_flow_style=False, Dumper=noalias_dumper))


    def dump_command(self, cmd):
        return {
            "name": cmd,
            "ipa_sudocmd": {
                "ipa_host": "{{ ipa_host }}",
                "ipa_user": "{{ ipa_user }}",
                "ipa_pass": "{{ ipa_pass }}",
                "name": cmd,
            }}
 

    def dump_cmdgroup(self, group, cmnds):
        return {
            "name": group,
            "ipa_sudocmdgroup": {
                "ipa_host": "{{ ipa_host }}",
                "ipa_user": "{{ ipa_user }}",
                "ipa_pass": "{{ ipa_pass }}",
                "name": group,
                "sudocmd": cmnds
            }}
 

    def dump_sudorule(self, rule):
        hostRE = re.compile('^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$', re.IGNORECASE)
        validhosts = [ h for h in rule.get_allowed_hosts() if hostRE.match(h)]
        if validhosts == []:
            return None

        sudorule = {
            "name":  rule.rulename,
            "ipa_sudorule": {
                "ipa_host": "{{ ipa_host }}",
                "ipa_user": "{{ ipa_user }}",
                "ipa_pass": "{{ ipa_pass }}",
                "name": rule.rulename,
            }}

        opts = rule.get_sudo_options()
        if opts:
            sudorule["ipa_sudorule"]["sudoopt"] = opts

        self.dump_ansible_type(sudorule["ipa_sudorule"], "cmd", "", rule.get_command_expanded())
        self.dump_ansible_type(sudorule["ipa_sudorule"], "host", '+', validhosts)
        self.dump_ansible_type(sudorule["ipa_sudorule"], "user", '%+', rule.get_allowed_users())
        return sudorule

    def dump_ansible_type(self, taskdict, objtype, groupchar, object_array):
        for obj in object_array:
            if str(obj) == "ALL":
                taskdict[objtype + "category"] = "all"
                return
            if obj[0] in groupchar:
                if taskdict.get(objtype + "group") == None:
                    taskdict[objtype + "group"] = []

                taskdict[objtype + "group"].append(str(obj[1:]))
            else:
                if taskdict.get(objtype) == None:
                    taskdict[objtype] = []
                taskdict[objtype].append(str(obj))

