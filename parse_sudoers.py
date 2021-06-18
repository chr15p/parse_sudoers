#!/usr/bin/env python
#
# This program parses a sudoers file and reports the rules as either text, or ansible tasks
# Author: Chris Procter <cprocter@redhat.com> 16-08-2019
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
from sudoparser.sudoparser import SudoParser
from sudoparser.ansibleplay import AnsiblePlaybook
from sudoparser.sudoersdisplay import SudoersDisplay

def create_option_parser():
    parser = OptionParser(usage="%prog [options] -u user")
    parser.add_option("-f", "--file", dest="sudoFile", metavar="FILE",
                      help="sudoers file to parser (default /etc/sudoers)", default="/etc/sudoers")
    parser.add_option("-a", "--ansible", dest="ansible", action="store_true",
                      help="output as a set of ansible tasks")
    parser.add_option("-s", "--sudoers", dest="sudoers", action="store_true",
                      help="output as a sudoers file")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="Increase verbosity. Provides debugging output")
    return parser


def main():
    parser = create_option_parser()
    (options, args) = parser.parse_args()
    if not options.sudoFile:
        parser.print_help()
        sys.exit(1)

    sudo_parse = SudoParser()

    sudo_parse.parseFile(options.sudoFile)
    if options.verbose:
        #print(sudo_parse.aliases["user"])
        #print(sudo_parse.aliases["host"])
        #print(sudo_parse.aliases["cmnd"])
        #print(sudo_parse.aliases["runas"])
        for rule in sudo_parse.rules:
            print("")
            rule.dump()
        exit(0)

    if options.sudoers:
        display = SudoersDisplay(sudo_parse, False)
        display.dump()

    #if options.ansible:
    else:
        play = AnsiblePlaybook(sudo_parse, description="generated from %s"% options.sudoFile)
        play.dump()


if __name__ == "__main__":
    main()


