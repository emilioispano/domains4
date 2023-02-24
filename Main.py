#!/usr/bin/python3

import Domains
import Utilities
import sys

if __name__ == '__main__':
    domains = Domains.Domains(sys.argv)
    domains.run_domains()

    Utilities.delete_directory(domains.get_settings().get_work_dir())
