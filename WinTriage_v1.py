from optparse import OptionParser
from os import mkdir, path, getcwd
from platform import uname
from time import strftime, asctime
import subprocess
from sys import exit

__author__ = 'karolpivo'

parser = OptionParser()
parser.add_option('-d', '--date', help='Specify date in dd/mm/yyyy or mm/dd/yyyy format based on computer settings', dest='modified_after')

(options, args) = parser.parse_args()


def create_output_dir(computername):
    """
    create output directory to save files in
    :param computername: type string, hostname retrived from uname()[1]
    :return: none
    """
    try:
        mkdir(computername)
        print "\nCreated collection directory - {0}\n".format(computername)
    except:
        print "Unable to create output directory"
        print "Please ensure the script is run with admin rights using run as administrator due to UAC"
        exit(1)


# get computer name to use as the name of the collection output directory
# platform.uname() returns OS detail in the following format:
# ('Windows', 'TESTVM1', '7', '6.1.7601', 'AMD64', 'Intel64 Family 6 Model 60 Stepping 3, GenuineIntel')
try:
    computer_name = uname()[1]
except:
    computer_name = 'outputdir'

# check if the collection directory already exists, if it does, create new one and append current time - TESTVM1-12-51-17
# this can happen if wintriage is run multiple times (we may want to compare multiple outputs)
if path.exists(computer_name):
    #computer_name = computer_name + '-' + strftime("%H-%M-%S")
    computer_name = '%s%s%s' % (computer_name, '-', strftime("%H-%M-%S"))


# if -d or --date option was specified, collect recently created / modified file paths
if options.modified_after:
    modified_after = options.modified_after
    cmd = 'forfiles /P c:\ /S /D +' + modified_after + ' /C "cmd /c echo @path"'
    print '\nGathering Information on recently created and modified files...'
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    stdout = p.stdout.readlines()
    if 'Invalid date specified' in stdout[0]:
        print("""\nIncorrect date format. Date must match local computer date format settings\n
        dd/mm/yyyy or mm/dd/yyyy""")
        exit(1)
    else:
        create_output_dir(computer_name)
        outputfile = open(path.join(computer_name, 'recentfiles.txt'), 'a')
        for line in stdout:
            outputfile.write("\t"+line)
        outputfile.close()
else:
    print "\nDate not specified - recent files will not be collected"
    create_output_dir(computer_name)

outputfile = open(path.join(computer_name, 'systeminfo.txt'), 'a')

######################
#       Reporting
######################


# Timestamp Function - Provide a timestamp when necessary
def timestamp():
    now = "["+strftime("%H:%M:%S")+"]"
    return now


# Process Commands Function - Execute given commands and write the results to the user specified outfile
def run_cmds(list_cmds):
    for cmd in list_cmds:
            split_cmd = cmd.split("::")
            outputfile.write("\n")
            outputfile.write(timestamp()+"\t"+split_cmd[0]+":\n")
            outputfile.write("===========================================================\n\n")
            p = subprocess.Popen(split_cmd[1], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
            for line in p.stdout.readlines():
                    outputfile.write("\t"+line)


def run_backup_event_log_cmds(cmds):
    """
    Execute commands to backup Event logs. Event log cannot be copied, we are using WMIC to back them up.
    :param cmds: type list, list of commands to execute
    :return: None
    """
    for cmd in cmds:
        split_cmd = cmd.split("::")
        p = subprocess.Popen(split_cmd[1], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        print "   - " + split_cmd[0]
        stdout = p.stdout.read()
        if 'successful' not in stdout:
            print stdout


#######################
# Collection Engine
#######################

# Collect general system information based on identified operating system type
print "\nGathering General System Information..."
outputfile.write("""
##############################################
#
#       General System Information
#
##############################################
""")

outputfile.write("\n")
outputfile.write("\tSystem Time:\t"+asctime()+"\n")

# Below are the specific operating system commands to be run for each OS type
# The format is <Description::Commnand> and both are required. Note the double colon "::" is the separator.
cmds = [
    'System Name::hostname',
    'Effective User::whoami',
    'System Type::for /F "delims== tokens=1-2" %a in (\'wmic os get Caption /format:list^|find "Caption"\') do @echo %b'
]

# Though we have a definition to execute the given commands, the format for the results in the "General System Information"
# are different from the other sections and thus required the execution for the above commands to be done here.
for cmd in cmds:
    split_cmd = cmd.split("::")
    outputfile.write("\t"+split_cmd[0]+":\t")
    p = subprocess.Popen(split_cmd[1], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    outputfile.write(p.stdout.read())
outputfile.write("\n")

# This list can easily be modified to include additional commands. Use the "<description>::<command>" format.

cmds = [
    'Filesystem Disk Space Usage::wmic logicaldisk get caption, size, freespace',
    'Memory Usage::wmic os get totalvisiblememorysize, freephysicalmemory,totalvirtualmemorysize, freevirtualmemory/format:list',
    'Environment Variables::set'
]

# Again the format for the results of these commands are different than the rest of the program. This requires the execution of the commands here.
for cmd in cmds:
    split_cmd = cmd.split("::")
    outputfile.write("\t"+split_cmd[0]+":\n")
    outputfile.write("\t=========================\n\n")
    p = subprocess.Popen(split_cmd[1], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    for line in p.stdout.readlines():
        outputfile.write("\t"+line)
    outputfile.write("\n")
outputfile.write("\n")


print "Gathering Network Information..."
outputfile.write("""
##############################################
#
#       Network Information
#
##############################################
""")

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

run_cmds(cmds)
outputfile.write("\n")

print "Gathering Process and Service Information..."
outputfile.write("""
##############################################
#
# Process, Service, Patches and Installed software
#
##############################################
""")

cmds = [
    'Running Processes::tasklist',
    'Process - Full Information::wmic process get name, description, commandline, executablepath, workingsetsize',
    'Services and Their State::sc query',
    'PIDs mapped to Services::tasklist /svc',
    'Intsalled Patches and Service Packs::wmic qfe',
    'Installed Software::wmic product get name, vendor, version, installdate'
]

run_cmds(cmds)
outputfile.write("\n")

print "Gathering Information on Registry keys..."
outputfile.write("""
##############################################
#
#       Registry Keys and Startup Items Information
#
##############################################
""")

cmds = [
    'hklm\software\microsoft\windows\currentversion\\run::reg query hklm\software\microsoft\windows\currentversion\\run',
    'hklm\software\microsoft\windows\currentversion\\runonce::reg query hklm\software\microsoft\windows\currentversion\\runonce',
    'hklm\software\microsoft\windows\currentversion\\runonceex::reg query hklm\software\microsoft\windows\currentversion\\runonceex',
    'hkcu\software\microsoft\windows\currentversion\\run::reg query hkcu\software\microsoft\windows\currentversion\\run',
    'hkcu\software\microsoft\windows\currentversion\\runonce::reg query hkcu\software\microsoft\windows\currentversion\\runonce',
    'hkcu\software\microsoft\windows\currentversion\\runonceex::reg query hkcu\software\microsoft\windows\currentversion\\runonceex',
    'Startup Items::wmic startup list full'
]

run_cmds(cmds)
outputfile.write("\n")


print "Gathering Account and User Information..."
outputfile.write("""
##############################################
#
#       Account and User Information
#
##############################################
""")

cmds = [
    'Local Accounts and Security Settings::wmic useraccount where localaccount=TRUE get name, caption, description, disabled, lockout, sid',
    'Accounts in the Local Administrators Group::net localgroup administrators'
]

print "Gathering Scheduled Task Information..."
outputfile.write("""
##############################################
#
#       Scheduled Tasks
#
##############################################
""")

cmds = [
    'Scheduled Tasks::schtasks'
]

run_cmds(cmds)
outputfile.write("\n")

print "Gathering Information on Unusual Files..."
outputfile.write("""
##############################################
#
#       Unusual files and folders
#
##############################################
""")

cmds = [
    'Large Files >50M::for /R c:\ %i in (*) do @if %~zi gtr 50000000 echo %i %~zi',
]

run_cmds(cmds)
outputfile.write("\n")

outputfile.close()


# Backup event logs
print "Backing up event logs..."

cmds = [
    'System log::wmic nteventlog where "logfilename="system"" call backupeventlog "{0}"'.format(path.join(getcwd(), computer_name, 'system.evtx')),
    'Application log::wmic nteventlog where "logfilename="application"" call backupeventlog "{0}"'.format(path.join(getcwd(), computer_name, 'application.evtx')),
    'Security log::wmic nteventlog where "logfilename="security"" call backupeventlog "{0}"'.format(path.join(getcwd(), computer_name, 'security.evtx')),
]

run_backup_event_log_cmds(cmds)

print "\nCollection completed, thanks :)\n"

raw_input("Press enter to exit")