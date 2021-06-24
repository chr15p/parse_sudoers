# represents a sngle decomposed rule within a suders file
# Author: Chris Procter <cprocter@redhat.com> 16-08-2019
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


class SudoRule:
    def __init__(self, rulename):
        self.rulename = rulename

        self.users = []
        self.hosts = []
        self.runas_user = []
        self.runas_group = []
        self.options = []
        self.command = []
        self.command_expanded = []

        self.cmdgroup = []

        self._setupusers = False
        self.deniedgroups = []
        self.allowedgroups = []
        self.deniedusers = []
        self.allowedusers = []

        self._setupcommands = False
        self.deniedcommand = []
        self.allowedcommand = []

        self._setupcmdgroups = False
        self.allowedcmdgroup = []
        self.deniedcmdgroup = []

    def get_allowed_users(self):
        if self._setupusers == False:
            self._setusersgroups()
        return self.allowedusers 

    def get_denied_users(self):
        if self._setupusers == False:
            self._setusersgroups()
        return self.deniedusers 

    def get_allowed_groups(self):
        if self._setupusers == False:
            self._setusersgroups()
        return self.allowedgroups

    def get_denied_groups(self):
        if self._setupusers == False:
            self._setusersgroups()
        return self.deniedgroups 

    def get_allowed_commands(self):
        if self._setupcommands == False:
            self._setup_commands()
        return self.allowedcommand

    def get_denied_commands(self):
        if self._setupcommands == False:
            self._setup_commands()
        return self.deniedcommand

    def get_allowed_cmdgroups(self):
        if self._setupcmdgroups == False:
            self._setup_cmdgroups()
        return self.allowedcmdgroup

    def get_denied_cmdgroups(self):
        if self._setupcmdgroups == False:
            self._setup_cmdgroups()
        return self.deniedcmdgroup

    def get_allowed_hosts(self):
        return self._get_allowed(True, self.hosts)

    def get_denied_hosts(self):
        return self._get_allowed(False, self.hosts)

    def get_allowed_runas_users(self):
        return self._get_allowed(True, self.runas_user)

    def get_denied_runas_users(self):
        return self._get_allowed(False, self.runas_user)

    def get_allowed_runas_groups(self):
        return self._get_allowed(True, self.runas_group)

    def get_denied_runas_groups(self):
        return self._get_allowed(False, self.runas_group)

    def get_options(self):
        return self.options

    def get_command(self):
        return self.command

    def get_command_expanded(self):
        return self.command_expanded

    def get_raw_command(self):
        output = []
        for obj in self.command:
            if obj[0] == '!':
                output.append(obj[1:])
            else:
                output.append(obj)

        return output

    def get_raw_command_expanded(self):
        output = []
        for obj in self.command_expanded:
            if obj[0] == '!':
                output.append(obj[1:])
            else:
                output.append(obj)

        return output

    def _setusersgroups(self):
        for obj in self.users:
            if obj[:2] == '!%':
                self.deniedgroups.append(obj[2:]) 
            elif obj[:1] == '%':
                self.allowedgroups.append(obj[1:]) 
            elif obj[:1] == '!':
                self.deniedusers.append(obj[1:]) 
            else:
                self.allowedusers.append(obj) 

        self._setupusers = True

    def _setup_commands(self):
        for obj in self.command:
            if obj[:1] == '!':
                self.deniedcommand.append(obj[1:]) 
            else:
                self.allowedcommand.append(obj) 
        self._setupcommands = True

    def _setup_cmdgroups(self):
        for obj in self.cmdgroup:
            if obj[:1] == '!':
                self.deniedcmdgroup.append(obj[1:]) 
            else:
                self.allowedcmdgroup.append(obj) 
        self._setupcmdgroups = True


    def _get_allowed(self, allowed, object_array):
        output = []
        if object_array is None:
            return []

        for obj in object_array:
            if obj[0] == '!':
                if allowed == False:
                    output.append(obj[1:])
            else:
                if allowed == True:
                    output.append(obj)
        return output
    
    def get_sudo_options(self):
        sudoopt = []
        for o in self.options:
            if o == "NOPASSWD":
                sudoopt.append('!authenticate')

        return sudoopt

    def dump(self):
        """
            debugging method
        """
        print
        print("name={}".format(self.rulename))
        print("allowed_users={}".format(self.get_allowed_users()))
        print("denied_users={}".format(self.get_denied_users()))
        print("allowed_groups={}".format(self.get_allowed_groups()))
        print("denied_groups={}".format(self.get_denied_groups()))
        print("allowed_hosts={}".format(self.get_allowed_hosts()))
        print("denied_hosts={}".format(self.get_denied_hosts()))
        print("allowed_runas_user={}".format(self.get_allowed_runas_users()))
        print("denied_runas_user={}".format(self.get_denied_runas_users()))
        print("allowed_runas_group={}".format(self.get_allowed_runas_groups()))
        print("denied_runas_group={}".format(self.get_denied_runas_groups()))
        print("options={}".format(self.get_sudo_options()))
        print("command={}".format(self.get_command()))
        print("command_expanded={}".format(self.get_command_expanded()))
        print("allowed_command={}".format(self.get_allowed_commands()))
        print("denied_command={}".format(self.get_denied_commands()))
        print("allowed_cmdgroups={}".format(self.get_allowed_cmdgroups()))
        print("denied_cmdgroups={}".format(self.get_denied_cmdgroups()))
        print("+++")

