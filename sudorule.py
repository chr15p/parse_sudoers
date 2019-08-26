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


    def get_allowed_users(self):
        return self._get_allowed(True, self.users)

    def get_denied_users(self):
        return self._get_allowed(False, self.users)

    def get_allowed_hosts(self):
        return self._get_allowed(True, self.hosts)

    def get_denied_hosts(self):
        return self._get_allowed(False, self.hosts)

    def get_allowed_runas_user(self):
        return self._get_allowed(True, self.runas_user)

    def get_denied_runas_user(self):
        return self._get_allowed(False, self.runas_user)

    def get_allowed_runas_group(self):
        return self._get_allowed(True, self.runas_group)

    def get_denied_runas_group(self):
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


    def _get_allowed(self, allowed, object_array):
        output = []
        if object_array is None:
            return None

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
        print("allowed_hosts={}".format(self.get_allowed_hosts()))
        print("denied_hosts={}".format(self.get_denied_hosts()))
        print("allowed_runas_user={}".format(self.get_allowed_runas_user()))
        print("denied_runas_user={}".format(self.get_denied_runas_user()))
        print("allowed_runas_group={}".format(self.get_allowed_runas_group()))
        print("denied_runas_group={}".format(self.get_denied_runas_group()))
        print("options={}".format(self.get_sudo_options()))
        print("command={}".format(self.get_command()))
        print("command_expanded={}".format(self.get_command_expanded()))

