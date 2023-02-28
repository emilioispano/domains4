#!/usr/bin/python3

import sys
import argparse
import logging
import os


class OptionsParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.parser = argparse.ArgumentParser(description='Description of your program')
        self.parser.add_argument('-i', '--input', help='The output of interproscan (mandatory)')
        self.parser.add_argument('-s', '--setting', help='The settings file (mandatory)')
        self.parser.add_argument('-b', '--blast', help='The output of Blast', nargs='?')
        self.parser.add_argument('-w', '--nwth', help='The score alignment to use as threshold')
        self.parser.add_argument('-o', '--output', help='The output file')
        self.parser.add_argument('-d', '--seedDom', help='The algorithm to use to individuate the seed domains <minfreq (default), maxfreq, all>')
        self.parser.add_argument('-p', '--print', help='Print gml graph', action='store_true')
        self.parser.add_argument('-r', '--rom', help='Use ROM for temporary files instead of RAM', nargs='?')
        self.parser.add_argument('-t', '--threads', help='Number of threads', nargs='?')
        self.args = self.parser.parse_args()

    def parse_options(self, settings):
        if self.args.input:
            settings.set_dom_file(self.args.input)
        else:
            self.logger.error('Input file is missing')
            return False

        if self.args.setting:
            settings.read_settings(self.args.setting)
        else:
            if os.path.exists(settings.FILE):
                settings.read_settings()
            else:
                self.logger.error('Setting file is missing')
                return False

        if self.args.nwth:
            settings.set_nwth(float(self.args.nwth))

        if self.args.output:
            try:
                settings.setOut(open(self.args.output, 'w'))
            except IOError as e:
                self.logger.error('Output file cannot be opened: {}'.format(e))
                self.parser.print_help()
                return False
        else:
            settings.setOut(sys.stdout)

        if self.args.seedDom:
            alg = self.args.seedDom
            if alg in ['minfreq', 'maxfreq', 'all']:
                settings.setSeedDom(alg)
            else:
                self.logger.error('Invalid seed domain algorithm specified')
                self.parser.print_help()
                return False
        else:
            settings.setSeedDom('minfreq')

        if self.args.print:
            settings.setPrintgml(True)

        if self.args.rom:
            settings.useRom()

        if self.args.blast:
            settings.setBlastFile(self.args.blast)

        if self.args.threads:
            settings.setThreads(int(self.args.threads))

        return True

    def print_help(self, parser=None):
        if parser is None:
            print('you need help')
        else:
            print("usage: script.py [options]\n")
            for group in parser._action_groups:
                if group.title == "positional arguments":
                    continue
                print(f"{group.title}:")
                for action in group._group_actions:
                    opt_strings = ", ".join(action.option_strings)
                    help_text = action.help
                    print(f"  {opt_strings}\t{help_text}")
                print()
