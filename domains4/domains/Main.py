from domains.Domains import Domains
from utils import Utilities
import sys

if __name__ == '__main__':
    domains = Domains(sys.argv)
    domains.run_domains()

    Utilities.delete_directory(domains.get_settings().get_work_dir())
