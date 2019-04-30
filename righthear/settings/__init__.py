"""
The correct settings file (production.py, development.py, etc.) is chosen at runtime according to the
system's hostname.

=====================
 Local customization
=====================

In order to create a non-revisioned custom settings file,
create a file named 'settings/custom.py' and it will be loaded instead of the per-hostname files.
This is useful if you want to make machine-specific changes without involving the mercurial.

custom.py examples:

1) override DB name on a development server:

    from development import *
    DATABASES['default']['NAME'] = 'shmulik'

2) force production settings on any server with debug on:

    from production import *
    DEBUG = True

===========================
 Settings inheritance flow
===========================

 common.py --> development.py
                           \--> factory.py
           --> production.py
                           \--> utest.py
"""

import socket
import sys

PRODUCTION_HOSTNAME = 'devamir'
CURRENT_HOSTNAME = socket.gethostname()

try:
    if CURRENT_HOSTNAME == PRODUCTION_HOSTNAME:
        print ('loading production settings file')
        from righthear.settings.production import *
    else:
        print ('loading dev settings file')
        from righthear.settings.base import *
except ImportError as e:
    sys.stderr.write("Error: There was an error importing the correct settings file.\nError message: %s" % e.message)
    sys.exit(1)

sys.path.append(os.path.join(PROJECT_DIR, '..'))  # ignore this error, PROJECT_DIR is always defined
