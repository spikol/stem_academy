"""
Reference for PythonAnywhere's WSGI configuration file.

PythonAnywhere does not read a .env file automatically — its own WSGI
config file (Web tab → "WSGI configuration file" link) is the place to set
environment variables for a free-tier account. Paid accounts can instead
use the "Environment variables" section on the Web tab, which is simpler
and keeps the secret out of any file entirely.

Copy the relevant lines below into the WSGI file PythonAnywhere generates
for you (it lives at something like
/var/www/<your_username>_pythonanywhere_com_wsgi.py) — do NOT copy this
file itself, and never commit your real key anywhere in this repo.
"""
import os
import sys

# Set the real values directly on the PythonAnywhere server — do not put
# real secrets in any file that gets committed to git.
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-REPLACE-ME"
os.environ["BRIDGE_SHARED_SECRET"] = "REPLACE-ME"
os.environ["ALLOWED_ORIGIN"] = "*"

path = "/home/<your_username>/stem_academy/backend"
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application  # noqa: E402
