__author__ = 'soroush'

import sys
import setup
import main


if __name__ == '__main__':
    if sys.argv[1] == 'setup':
        setup.setup()
    elif sys.argv[1] == 'start':
        main.run_bot()
