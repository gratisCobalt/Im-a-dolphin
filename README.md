# I'm a dolphin

A summary of standalone modules useful for malwares

## /root

* installRequirements: installs pip requirements (untested)

## authorization

* disableUAC: disables User Account Control via command (working)
* runAsAdmin: trys to execute code as admin, show an admin promt (working)

## external modules

* Python-Backdoor: client from [xp4xbox](https://github.com/xp4xbox/Python-Backdoor)
* Desktop Goose: [Desktop Goose](https://samperson.itch.io/desktop-goose)

## deviceInfo

* byteConverter: allows better readability of byte specifications (1253656 => '1.20MB') (working)
* checkWinDefender: checks if Windows Defender is installed (uncomplete)
* installedSoftware: checks installed software (uncomplete, working)
* device: prints specifications of device (cpu, disk, memory, system, network, gpu) (working)

## screenMessage

* displays a text message on the screen, that is difficult to remove (working)

## taskscheduler

* cmdscheduler: creates new scheduled task via cmd based on xml file (untested)
* taskscheduler: creates new scheduled task via win32 (python) (uncomplete, working)
