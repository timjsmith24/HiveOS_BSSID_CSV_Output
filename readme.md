# HiveOS SSH BSSID CSV
## hiveOS_bssid_csv.py
### Purpose
This script will open a SSH session with mulitple APs, and run the command 'show interface' on each AP. The output is then parsed using a textfsm template. From this parsed data a CSV is created with the AP, interface, bssid, and ssid information. 

## User Input Data
#### SSH Login info
The username and passowrd for the SSH sessions will need to be entered 
###### lines 20-21
```
username = 'admin'
password = 'Extreme123!'
```
#### AP info
The ip addresses and ports of the APs to be connected to will need to be put in the ip_list.csv 
```
192.168.1.118,22
192.168.1.117,22
192.168.1.117,20248
```
>###### NOTE:
>SSH sessions will be done in batches. This batch size can be adjusted on line 96. 

## Script Outputs
#### Terminal Window
The terminal window will show when the scripts is establishing a connection to one of the devices as well as if there are any errors while connecting. Once the list of Devices is complete the terminal will provide a message to look at the saved csv file.

#### CSV file
A CSV file named AP_bssid.csv will be created by the script with the information that the script was able to collect. If this file already exists it will be overwritten by the script. The name of the file can be changed on line 23

## Requirements
This script was written for Python3.6 or higher. The Paramiko and textfsm modules will need to be installed in order for the script to function. This modules are listed in the requirements.txt file. 