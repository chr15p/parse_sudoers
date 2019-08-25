import os
import re

from sudorule import SudoRule

class SudoParser:
    def __init__(self):
        self.filename = ""
        self.aliases = dict()
        self.aliases['host'] = dict()
        self.aliases['user'] = dict()
        self.aliases['cmnd'] = dict()
        self.aliases['runas'] = dict()

        self.rules = []

    def _readfile(self, filename):
        fh = open(filename, "r")
        return fh.readlines()


    def parseFile(self, filename):
        self.filename = os.path.basename(filename)
        lines = self._readfile(filename)
        lines = self._collapse_lines(lines)

        defaultsRE = re.compile(r"^\s*Defaults")
        runasAliasRE = re.compile(r"^\s*Runas_Alias")
        hostAliasRE = re.compile(r"^\s*Host_Alias")
        userAliasRE = re.compile(r"^\s*User_Alias")
        cmndAliasRE = re.compile(r"^\s*Cmnd_Alias")
        lineno = 0
        for l in lines:
            lineno += 1
            ## strip out comments
            try:
                line = l[:l.index('#')].strip()
            except:
                line = l.strip()
            ## if the line is blank move on
            if line == '':
                continue

            ## ignore defaults then parse any Alias lines we find
            if defaultsRE.search(line):
                # don't currently do anything with these
                continue
            if hostAliasRE.search(line):
                self.aliases['host'].update(self._parse_alias(line, "Host_Alias"))
                continue
            if runasAliasRE.search(line):
                self.aliases['runas'].update(self._parse_alias(line, "Runas_Alias"))
                continue
            if userAliasRE.search(line):
                self.aliases['user'].update(self._parse_alias(line, "User_Alias"))
                continue
            if cmndAliasRE.search(line):
                self.aliases['cmnd'].update(self._parse_alias(line, "Cmnd_Alias"))
                continue

            ## if its not a comment, a default, or an alias, its probably a rule
            rule = self.parse_rule(lineno, line)


    def parse_rule(self, lineno, line):

        #blankRE = re.compile(r"^s*$")
        userRE = re.compile(r"(?<!,)+\s+")
        cmdRE = re.compile(r" : \s*(?![^()]*\))")
        listRE = re.compile(r"\s*,\s*")

        #print("++++++++++++++++")
        #print(line)
        user_spec = userRE.split(line,1)
        user_list = user_spec[0]
        users = listRE.split(user_list)
        rest = user_spec[1]

        ## a rule could be multiple host=commands sections seperated by colons
        ## e.g. "users host=commands:host=commands:host=commands"
        ## so split on colon and parse each as a seperate rule
        commands = cmdRE.split(rest)
        command_no = 0
        for c in commands:
            command_no += 1
            host_list, cmnd_spec_list = self.parse_host_list(c)
            hosts = listRE.split(host_list)
            prev_runas_spec = "root"
            prev_tag_spec = []

            cmd_spec_no = 0
            while cmnd_spec_list is not None:
                cmd_spec_no += 1
                ## a command_spec_list is a comma seperated list of command_specs
                ## a command_spec is  Runas_Spec? Option_Spec* Tag_Spec* Cmnd
                #print("cmnd_spec_list={}".format(cmnd_spec_list))
                cmnd_spec, cmnd_spec_list = self.parse_cmnd_spec_list(cmnd_spec_list)
                #print("cmnd_spec={}".format(cmnd_spec))
                runas_spec, tag_spec, cmnds = self.parse_cmnd_spec(cmnd_spec)
                ## runas_specs and tags like NOEXEC effect all the command_spec's that come after them in the rule
                ## so if its not set then use the previous ones
                if runas_spec == None:
                    runas_spec = prev_runas_spec
                else:
                    prev_runas_spec = runas_spec

                if tag_spec == []:
                    tag_spec = prev_tag_spec
                else:
                    prev_tag_spec = tag_spec

                ## the runas_spec can be user_list : group_list  where lists are comma sperated
                runas_users, runas_groups = self.parse_runas_list(runas_spec)

                rule = SudoRule("{}.{}-{}.{}".format(self.filename, lineno, command_no, cmd_spec_no))
                self.rules.append(rule)
                rule.users = self.expand_aliases("user",users) #users
                rule.hosts = self.expand_aliases("host",hosts) #hosts
                rule.runas_user = self.expand_aliases("runas",runas_users) #runas_users
                rule.runas_group =self.expand_aliases("runas",runas_groups)  #runas_groups
                rule.options = tag_spec
                rule.command = [cmnds] # self.expand_aliases("cmnd",[cmnds])
                rule.command_expanded = self.expand_aliases("cmnd",[cmnds])
                
                ## sort into allowed and denied
                #users_allowed, users_denied = self.split_allowed(users)
                #hosts_allowed, hosts_denied = self.split_allowed(hosts)
                ## expand aliases
                #users_exp = self.expand_aliases('user', users)
                #hosts_exp = self.expand_aliases('host', hosts)
                ## sort into things and groups
                #print("{}++{}++{}++{}++{}++{}++{}++{}".format(users_allowed, users_denied, hosts_allowed, hosts_denied, runas_users, runas_groups, tag_spec, cmnds))
                #print("users_allowed={}".format(users_allowed))
                #print("users_denied={}".format(users_denied))
                #print("hosts_allowed={}".format(hosts_allowed))
                #print("hosts_denied={}".format(hosts_denied))
                #print("runas_users={}".format(runas_users))
                #print("runas_groups={}".format(runas_groups))
                #print("tag_spec={}".format(tag_spec))
                #print("cmnds={}".format(cmnds))


    def split_allowed(self, object_array):
        denied = [] 
        allowed = []
        for obj in object_array:
            if obj[0] == '!':
                denied.append(obj[1:])
            else:
                allowed.append(obj)
        return allowed,denied

    def expand_aliases(self, alias, object_array):
        expanded = []
        denied = 0
        if object_array == None:
            return None
        for obj in object_array:
            if obj[0] == "!":
                obj = obj[1:]
                denied = 1
            if self.aliases[alias].get(obj):
                if denied == 0:
                    expanded.extend(self.aliases[alias][obj])
                else:
                    for obj in self.aliases[alias][obj]:
                        expanded.append("!" + obj)
            else:
                expanded.append(obj)
        return expanded


    def _parse_alias(self, line, marker):
        res = {}
        aliasnameRE = re.compile(r"\s*%s\s*(.*)" % marker)
        m = aliasnameRE.search(line)
        aliases = m.group(1)
        aliasRE = re.compile(r"(\S+)\s*=\s*((\S+,?\s*)+)")
        for i in aliases.split(":"):
            m = aliasRE.search(i)
            if m:
                alias = str(m.group(1))
                nodes = str(m.group(2)).split(",")
                nodes = [node.strip() for node in nodes]
                res[alias] = nodes

        return res


    def _collapse_lines(self, lines):
        """
            merge lines that are continued by a \ character
            input:
                lines: an array of strings
            output:
                [line1, line2, line3 ...]
        """
        res = []
        currentline = ""

        for line in lines:
            if line.rstrip()[-1:] == "\\":
                currentline += line.rstrip()[:-1]
            else:
                currentline += line
                res.append(currentline)
                currentline = ""

        return res


    def parse_host_list(self, command):
        """
        chop the host list from the rule:
        accepts:
            command: string "hosts = commands"
        returns:
            [hosts, commands]
        """
        hostRE = re.compile(r"(?<!,)+[\s=]+\s*")
        hosts = hostRE.split(command, 1)
        return hosts


    def parse_cmnd_spec_list(self, cmnd_spec_list):
        """
        chop the first command from the string based on commas not within the runas field
        accepts:
            cmnd_spec_list: string "command, command, command"
        returns:
            [command, rest_of_string or None]
        """
        #### TODO: make this work with regexp, it gets messed up by escaped commas in commands
        #cmnd_specRE = re.compile(r"(?!\\),\s*(?![^()]*\))")
        #cmnd_specs = cmnd_specRE.split(cmnd_spec_list,1)
        flag = 0
        escape = 0
        i = -1
        #print("++cmnd_spec_list={}".format(cmnd_spec_list))
        for c in cmnd_spec_list:
            i += 1
            #print("{}={} {}".format(i,c, cmnd_spec_list[i]))
            if c == "(":
                flag = 1
            elif c == ")":
                flag = 0
            elif c == '\\':
                escape = 1
            elif c == "," and escape == 0 and flag == 0:
                i -= 1
                break
            else:
                escape = 0

        i += 1
        #print("i={}".format(i))
        cmnd_specs = cmnd_spec_list[:i]
        #print("cmnd_spec_list[0:{}]={}".format(i,cmnd_spec_list[0:i]))
        #print("cmnd_spec_list[{}:]={}".format(i,cmnd_spec_list[i:]))
        #print("{} < {}".format(i, len(cmnd_spec_list)))
        if i < len(cmnd_spec_list):
            return cmnd_spec_list[:i], cmnd_spec_list[i+1:]
        else:
            return cmnd_spec_list[:i], None
        #if len(cmnd_specs) > 1:
        #    return cmnd_specs
        #else:
        #    return [cmnd_specs[0], None]


    def parse_cmnd_spec(self, cmnd_spec):
        runas_spec, cmnd_spec = self.parse_runas_spec(cmnd_spec)

        tag_spec, cmnds = self.parse_tag_spec(cmnd_spec)
        return runas_spec, tag_spec, cmnds


    def parse_runas_spec(self, cmnd_spec):
        cmnd_spec = cmnd_spec.strip()
        runas_specRE = re.compile(r"\w*\((.*)\)\w*")
        runas_spec_matches = runas_specRE.match(cmnd_spec)
        if runas_spec_matches:
            runas_spec = runas_spec_matches.group(1)
            end = runas_spec_matches.end()
        else:
            runas_spec = None
            end = 0
        return runas_spec, cmnd_spec[end:]


    def parse_runas_list(self, runas_spec):
        listRE = re.compile(r"\s*,\s*")

        r = runas_spec.split(":", 1)
        runas_users = listRE.split(r[0].strip())
        runas_groups = None
        if len(r) > 1:
            runas_groups = listRE.split(r[1].strip())
        return runas_users, runas_groups


    def parse_tag_spec(self, cmnd_spec):
        tags = []
        cmnd_spec = cmnd_spec.strip()
        tag_specRE = re.compile(r"(\w+):\s*")
        tags_iterator = tag_specRE.finditer(cmnd_spec)
        end = 0
        for t in tags_iterator:
            tags.append(t.group(1))
            end = t.end()

        return tags, cmnd_spec[end:]


