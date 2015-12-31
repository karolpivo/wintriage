# Introduction

WinTriage quickly collects critical information from key areas of the operating system to assist information security incident handlers in 
determining whether or not there has been compromise. WinTriage automates execution of multiple built-in Windows commands.

WinTriage may be deployed to many systems and the results analyzed relative to each other to help the incident handler prioritize 
where to focus their containment efforts. Frequently, the incident handler does not have immediate access or authorization to the systems 
in question and getting it setup can be time consuming. WinTriag can be quickly provided to authorized system administrators to collect the critical information 
many times used to help identify a compromise. Beside speed to deploy and overcoming access barriers, the other major benefits of using WinTriage include:

- Ability to add/modify collection commands or event sources as necessary
- Consistent results and output format
- Simplicity (optional -d flag)
- Single collection script to maintain for all Windows versions 
- Purpose built and tailored for Windows
- Collect info you may need to determine if the system is compromised with single command

## WinTriage does the following

- Executes number of OS commands (netstat, wmic, reg query, tasklist, etc)
- Creates copy of Event logs in native format (.evtx)
- Lists full paths of recently created or modified files (with -d option)
- Creates a directory  and saves output

## Origin 

WinTriage was inspired by RapidTriage project and it uses parts of the original code. Even though RapidTriage required only two command line 
flags to execute, I found that it still required some education and explanation for it to be run by our Analysts. 

WinTriage does not require any flags. It can be run by simple right click run as administrator. Additionally, further Windows specific
functionality will be implemented in the future. 

# Details

```
Usage: WinTriage.exe [options]

Options:
  -h, --help            show this help message and exit
  -d MODIFIED_AFTER, --date=MODIFIED_AFTER
                        Specify date in dd/mm/yyyy or mm/dd/yyyy format based on computer settings
```

Optional -d flag can be used to list files that were created or modified after the specific date. This is info is collected using forfiles command.  

Date must be specified in the format matching computer date format settings dd/mm/yyyy or mm/dd/yyyy.

###Supported Python Version: 

- 2.7

###Supported Operating Systems

- Windows 7 / 2008 and newer

# Creating Windows executable

Python is not usually on Windows. Installing any software as part of Incident Response is not ideal first step!

The best option is to covert the python script to Windows EXE using py2exe - http://www.py2exe.org/
py2exe is a Python Distutils extension which converts Python scripts into executable Windows programs, able to run without requiring a Python installation.

1. Download and install py2exe - http://sourceforge.net/projects/py2exe/files/py2exe/ 
2. Clone WinTriage git repo or download as zip
3. Open command prompt and CD into the wintriage directory 
4. Run python setup.py py2exe

This will create a "dist" directory and that will contain the executable and additional reuqired files (dlls and some additional libraries)

# Changing what is collected

Many sections of the script include lists of commands and a description. To add or modify the commands that are used to collect information simply use the following format:

    <description>::<command>

Make sure to modify the list corresponding to the appropriate operating system type. For example, to modify the network information collected find and change the network "cmds" list using the above syntax:

```
##############################################
#
#       Network Information
#
##############################################


cmds = [
    'Network Interface Configuration::ipconfig /all',
    'Route Table::route print',
    'ARP Table::arp -a',
    'Listening Ports::netstat -ano |find /i "listening"',
    'Established Connections::netstat -ano |find /i "established"',
    'Established/Listening Connections and Associated Command::netstat -anob',
    'Count of Half Open Connections::netstat -ano |find /i /c "syn_received"',
    'Count of Open Connections::netstat -ano |find /i /c "established"',
    'Hosts file contents::type %SystemRoot%\System32\Drivers\etc\hosts',
    'Sessions Open to Other Systems::net use',
    'Local File Shares::net view \\\\127.0.0.1',
    'Available Local Shares::net share',
    'Open Sessions with Local Machine::net session'
]
```