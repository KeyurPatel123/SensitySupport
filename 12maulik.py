from pexpect import pxssh
from apscheduler.scheduler import Scheduler
import re
import datetime
import time
import socket
import logging

# Start the scheduler
sched = Scheduler()
sched.daemonic = False
sched.start()

def job_function():
# Logging Into Machine

    list_for_IO_read = []
    list_for_IO_write =[]
    sum_write= 0.0
    sum_read = 0.0
    s = pxssh.pxssh()
    if not s.login ('127.0.0.3', 'keyur', 'einfochips'):
    		print "SSH session failed on login."
    		print str(s)

    else: 
        print "LOGIN SUCCESSFUL"
	##################
	#Reading the Mem.Information
	s.sendline ("cat /proc/meminfo");
	s.prompt();
	file = open("meminfo.txt","w");
	file.write(s.before);
	file.close();
	##################

	##################
	#Getting CPU Usage
	s.sendline ("top -b -n 1 | grep 'Cpu(s)'");
	s.prompt();
	file = open("top.txt","w");
	file.write(s.before);
	file.close();
	##################
		
	##################
	#Getting disk usage of /usr/lib
	s.sendline ("du -sh /usr/lib");
	s.prompt();
	file = open("space.txt","w");
	file.write(s.before);
	file.close();
	##################

	# Getting CPU Available
	s.sendline ("top -b -n 1 | grep 'Cpu(s)'");
	s.prompt();
	file = open("cpu_available_log.txt","w");
	file.write(s.before);
	file.close();

	##################
	#Getting the Network packet received Information
	s.sendline ("netstat -i | grep 'eth0' | awk '{print $3}'");
	s.prompt();
	file = open("networkReceivedInfo.txt","w");
	file.write(s.before);
	file.close();

	#Getting the I/o Read Information
	s.sendline ("iostat -d -m | awk '{print $3}'");
	s.prompt();
	file = open("IOReadInfo.txt","w");
	file.write(s.before);
	file.close();
		   
	#Getting the I/o Write information
	s.sendline ("iostat -d -m | awk '{print $4}'");
	s.prompt();
	file = open("IOWriteInfo.txt","w");
	file.write(s.before);
	file.close();

	#Getting the Network Transmit
        s.sendline ("netstat -i | grep 'eth0' | awk '{print $7}'");
        s.prompt();
        file = open("networkTransmitInfo.txt","w");
        file.write(s.before);
        file.close();
			

	##################
	#Reading the Free Mem.
	file = open("meminfo.txt","r");
	meminfo = file.readlines();
	logging.basicConfig()

	for line in meminfo:
		if 'MemFree' in line:
			memfree = line.split(" kB")[0];
			memfree = re.sub(' +', ' ', memfree);
			memfree = memfree.split(" ")[1];
			print "Free Mem {0}\n".format(str(memfree))
	###################

	###################
	#Reading the Overall CPUUsage
	file = open("top.txt","r");
	cpuusage = file.readlines();
	logging.basicConfig()
	for line in cpuusage:
		if "us" in line:
			print line
			cpuusage = line.split(":")[1];
			cpuusage = cpuusage.split("us")[0];
			print "CPU Utilization is {0}\n".format(str(cpuusage))

			
	###################
	#Reading the disk space of /usr/lib
	file = open("space.txt","r");
	diskspace = file.readlines();
	logging.basicConfig()
	for line in diskspace:
		if "." in line:
			b = line.split("	/")[0];
				
			if "G" in b:
				b = float(b.split("G")[0]);	
				b = str(b)	
				print "Disk Usage of /usr/lib is " + b + " Gb\n"
	###################

	###################
	#Reading the cpu available
	file = open("cpu_available_log.txt","r");
	cpuavailable = file.readlines();
	logging.basicConfig()
	for line in cpuavailable:
		if "id" in line:
			print line
			cpuavailable = line.split(":")[1];
			cpuavailable = cpuavailable.split("id")[0];
			cpuavailable = cpuavailable.split(",")[3]
			cpuavailable = str(cpuavailable)
			print "CPU Available is " + cpuavailable + " \n"

	#Reading the network packet received information
	file = open("networkReceivedInfo.txt","r");
	networkinfo = file.readlines();
	logging.basicConfig()
	for line in networkinfo:
		netreceived = str(line.strip())
	print 'Number of packet received',netreceived

	#Reading the network packet transmit information
	file = open("networkTransmitInfo.txt","r");
	networkinfo = file.readlines();
	logging.basicConfig()
	for line in networkinfo:
		nettransmit = str(line.strip())
	print 'Number of packet Transmit',nettransmit
			
	#Reading the IO Read information
	file = open("IOReadInfo.txt","r");
	ioreadinfo = file.readlines();
	logging.basicConfig()
	for line in ioreadinfo:
		list_for_IO_read.append(line.strip())
	for l in range(4,len(list_for_IO_read)-1):
		sum_read += float(list_for_IO_read[l])
	IORead = str(sum_read)
	print 'Number of IO read information', IORead

	#Reading the IO Write information
	file = open("IOWriteInfo.txt","r");
	iowriteinfo = file.readlines();
	logging.basicConfig()
	for line in iowriteinfo:
		list_for_IO_write.append(line.strip())
	for l in range(4,len(list_for_IO_write)-1):
		sum_write += float(list_for_IO_write[l])
	IOWrite = str(sum_write)
	print 'Number of IO write operation',IOWrite
		
	###################
	#Sending the data to Graphite UI        
	IP = '127.0.0.1'
	PORT = 2003
	a = datetime.datetime.now();
			
	#MemInfo Data
	MemUsage = 'Centos.MemUsage ' + memfree + ' %d\n ' % int(time.time());
	print MemUsage;
		
	#CPUUsage Data
	print 'cpuusage1 : ', cpuusage
	CPUUsage = 'Centos.CPUUsage ' + cpuusage + ' %d\n ' % int(time.time());
	print CPUUsage;
			
	#DiskSpace Data
	DiskSpace = 'Centos.DiskUsage ' + b + ' %d\n ' % int(time.time());
	print DiskSpace;

	#CPUAvailable Data
	CPUAvailable = 'Centos.CPUAvailable ' + cpuavailable + ' %d\n ' % int(time.time());
	print CPUAvailable

	#NetworkReceived Data
	NetworkReceived = 'Centos.NetworkReceived ' + netreceived + ' %d\n ' % int(time.time());
	print NetworkReceived

	#NetworkTransmit Data
	NetworkTransmit = 'Centos.NetworkTransmit ' + nettransmit + ' %d\n ' % int(time.time());
	print NetworkTransmit	

	#IORead Data
	IORead = 'Centos.IORead ' + IORead  + ' %d\n ' % int(time.time());
	print IORead

	#IOWrite Data
	IOWrite = 'Centos.IOWrite ' + IOWrite  + ' %d\n ' % int(time.time());
	print IOWrite

	try:
			
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((IP,PORT))
		s.send(MemUsage)
		s.send(CPUUsage)
		s.send(DiskSpace)
		s.send(CPUAvailable)
		s.send(NetworkReceived)
		s.send(NetworkTransmit)
		s.send(IORead)
		s.send(IOWrite)
			
	except Exception as e:
		print e;
			
			
				
	s.shutdown(socket.SHUT_WR)
			
	time.sleep(20)

# Schedules job_function to be run once each minute
sched.add_cron_job(job_function,  minute='0-59')
