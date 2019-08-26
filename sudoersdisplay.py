
class SudoersDisplay:
    def __init__(self, sudoparser, use_groups = False):
        self.parser = sudoparser
        self.use_groups = use_groups 

    def dump(self):
        for a in ["user", "host", "cmnd", "runas"]:
            name = a.capitalize() + "_Alias"
            if self.parser.aliases[a].keys() == []:
                continue
            for obj in self.parser.aliases[a].keys():
                print "{}\t{} = {}".format(name, obj, ",".join(self.parser.aliases[a][obj]) )

            print("")

        
        for rule in self.parser.rules:
            users = ",".join(rule.users)
            hosts = ",".join(rule.hosts)

            runas = ""
            if rule.runas_user != None:
                runas = ",".join(rule.runas_user)
                
            if rule.runas_group != None:
                runas += ": {}".format(",".join(rule.runas_group))

            if runas != "":
                runas= "( {} )".format(runas)

            if rule.options != None:
                options = ",".join([o + ":" for o in rule.options])
            else:
                options = ""

            if self.use_groups == True:
                command = ",".join(rule.command)
            else:
                command = ",".join(rule.command_expanded)
    
            
            print "{}\t{} = {} {} {}".format(users, hosts, runas, options, command)
