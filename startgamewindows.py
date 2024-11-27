import subprocess
import sys

# Start all needed scripts
scripts = ['server.py', 'viewer.py', 'student.py']#'client.py', 'student.py']

python_executable = sys.executable

# Start each script in a new terminal window
for script in scripts:
    subprocess.Popen(['start', 'cmd', '/k', python_executable, script], shell=True)