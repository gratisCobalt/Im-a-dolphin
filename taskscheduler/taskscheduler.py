import datetime
import win32com.client

# TODO: not right config for taskscheduler

name = "svchost"
id = "svchost.exe"
description = "svchost is a system process that can host from one to many Windows services in the Windows NT family of operating systems. Svchost is essential in the implementation of so-called shared service processes, where a number of services can share a process in order to reduce resource consumption."
program = "python.exe"
program_parmeters = ""

scheduler = win32com.client.Dispatch("Schedule.Service")
scheduler.Connect()
root_folder = scheduler.GetFolder("\\")
task_def = scheduler.NewTask(0)

# Create trigger
start_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
TASK_TRIGGER_TIME = 1
trigger = task_def.Triggers.Create(TASK_TRIGGER_TIME)
trigger.StartBoundary = start_time.isoformat()

# Create action
TASK_ACTION_EXEC = 0
action = task_def.Actions.Create(TASK_ACTION_EXEC)
action.ID = id
action.Path = program
action.Arguments = program_parmeters

# Set parameters
task_def.RegistrationInfo.Description = description
task_def.Settings.Enabled = True
task_def.Settings.StopIfGoingOnBatteries = False

# Register task
# If task already exists, it will be updated
TASK_CREATE_OR_UPDATE = 6
TASK_LOGON_NONE = 0
root_folder.RegisterTaskDefinition(
    name,  # Task name
    task_def,
    TASK_CREATE_OR_UPDATE,
    "",  # No user
    "",  # No password
    TASK_LOGON_NONE,
)
