#!/usr/bin/env python
#
#
# This program parses a sudoers file 
# Author: Chris Procter <cprocter@redhat.com> 16-08-2019
#
# with some parts based on work by Joel Heenan 30/09/2008
# https://github.com/blentz/scripts/blob/master/ldap/parse_sudoers.py
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import sys
import yaml
from optparse import OptionParser
from sudoparser import SudoParser

def create_option_parser():
    parser = OptionParser(usage="%prog [options] -u user")
    parser.add_option("-f", "--file", dest="sudoFile", metavar="FILE",
                      help="sudoers file to parser (default /etc/sudoers)", default="/etc/sudoers")
    parser.add_option("-a", "--ansible", dest="ansible", action="store_true",
                      help="output as a set of ansible tasks")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="Increase verbosity. Provides debugging output")
    return parser


def ansible_commands(parser):
    sudocmd = dict()
    for rule in parser.rules:
        for cmd in rule.get_raw_command_expanded():
            if cmd == "ALL": continue
            sudocmd[cmd] = {
                "name": cmd,
                "ipa_sudocmd": {
                    "ipa_host": "{{ ipa_host }}",
                    "ipa_user": "{{ ipa_user }}",
                    "ipa_pass": "{{ ipa_pass }}",
                    "name": cmd,
                }}
    for v in parser.aliases['cmnd'].values():
        for cmd in v: 
            if cmd == "ALL": continue
            sudocmd[cmd] = {
                "name": cmd,
                "ipa_sudocmd": {
                    "ipa_host": "{{ ipa_host }}",
                    "ipa_user": "{{ ipa_user }}",
                    "ipa_pass": "{{ ipa_pass }}",
                    "name": cmd,
                }}
    return sudocmd.values()


def ansible_aliases(parser):
    sudocmdgroup = dict()
    for group in parser.aliases['cmnd'].keys():
        sudocmdgroup[group] = {
            "name": group,
            "ipa_sudocmdgroup": {
                "ipa_host": "{{ ipa_host }}",
                "ipa_user": "{{ ipa_user }}",
                "ipa_pass": "{{ ipa_pass }}",
                "name": group,
                "sudocmd": parser.aliases['cmnd'][group]
            }}
    return sudocmdgroup.values()


def ansible_sudorules(parser):
    allrules = []
    for rule in parser.rules:
        allrules.append(rule.dump_ansible())
    return allrules


def main():
    parser = create_option_parser()
    (options, args) = parser.parse_args()
    if not options.sudoFile:
        parser.print_help()
        sys.exit(1)

    sudo_parse = SudoParser()

    sudo_parse.parseFile(options.sudoFile)
    if options.verbose:
        print(sudo_parse.aliases["user"])
        print(sudo_parse.aliases["host"])
        print(sudo_parse.aliases["cmnd"])
        print(sudo_parse.aliases["runas"])
        for rule in sudo_parse.rules:
            rule.dump()

    if options.ansible:
        noalias_dumper = yaml.dumper.SafeDumper
        noalias_dumper.ignore_aliases = lambda self, data: True

        allcmds = ansible_commands(sudo_parse)
        if allcmds:
            print(yaml.dump(allcmds, default_flow_style=False, Dumper=noalias_dumper))

        allaliases = ansible_aliases(sudo_parse)
        if allaliases:
            print(yaml.dump(allaliases, default_flow_style=False, Dumper=noalias_dumper))

        allrules = ansible_sudorules(sudo_parse)
        if allrules:
            print(yaml.dump(allrules, default_flow_style=False, Dumper=noalias_dumper))



if __name__ == "__main__":
    main()


