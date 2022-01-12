import subprocess


def execute(path):
    try:
        subprocess.Popen(path)
    except Exception:
        return False
    return True


def runScreenMessage():
    execute("C:\\Users\\Dominik\\Desktop\\service.exe")
