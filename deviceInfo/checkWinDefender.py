import subprocess

out = subprocess.run(
    ['powershell', '-command', 'Get-MpComputerStatus'],
    stdout = subprocess.PIPE
    )

print(out.stdout)
