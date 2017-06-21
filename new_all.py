from apscheduler.scheduler import Scheduler
from subprocess import PIPE
import re
from datetime import datetime
from time import time
import socket
import subprocess
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
	
	##################
	#Getting the Mem.Information
	meminfo = Popen(["cat /proc/meminfo"], stdout=PIPE, stderr=PIPE,shell=True)
	for line in meminfo.stdout:
		if 'MemFree' in line:
			memfree = line.split(" kB")[0]
			memfree = re.sub(' +', ' ', memfree)
			memfree = memfree.split(" ")[1]
			break
	##################

	##################
	#Getting CPU Usage & CPU Available
	topinfo = Popen(["top -b -n 1 | grep 'Cpu(s)'"], stdout=PIPE, stderr=PIPE,shell=True)
	for line in topinfo.stdout:
		if "us" in line:
			cpuusage = line.split(":")[1]
			cpuusage = cpuusage.split("us")[0]
			cpuusage = cpuusage.split("%")[0]
			cpuusage = str(cpuusage)
			break
			
	for line in topinfo.stdout:
		if "id" in line:
			cpuavailable = line.split(":")[1]
			cpuavailable = cpuavailable.split("id")[0]
			cpuavailable = cpuavailable.split(",")[3]
			cpuavailable = cpuavailable.split("%")[0]
			cpuavailable = str(cpuavailable)
			break
	##################
							

	##################
	#Getting the Network packet received Information
	networkreceiveinfo = subprocess.Popen(["netstat -i | grep 'eth0' | awk '{print $3}'"], stdout=PIPE,stderr=PIPE, shell=True)
	for line in networkreceiveinfo.stdout:
		netreceived = str(line.strip())
	

	#Getting the I/o Read Information
	ioreadinfo = subprocess.Popen(["iostat -d -m | awk '{print $3}'"], stdout=PIPE,stderr=PIPE, shell=True)
	for line in ioreadinfo.stdout:
		list_for_IO_read.append(line.strip())
	for l in range(4,len(list_for_IO_read)-1):
		sum_read += float(list_for_IO_read[l])
	IORead = str(sum_read)
	
		   
	#Getting the I/o Write information
	iowriteinfo = subprocess.Popen(["iostat -d -m | awk '{print $4}'"], stdout=PIPE,stderr=PIPE, shell=True)
	for line in iowriteinfo.stdout:
		list_for_IO_write.append(line.strip())
	for l in range(4,len(list_for_IO_write)-1):
		sum_write += float(list_for_IO_write[l])
	IOWrite = str(sum_write)
	

	#Getting the Network Transmit
	networktransmitinfo = subprocess.Popen(["netstat -i | grep 'eth0' | awk '{print $7}'"], stdout=PIPE,stderr=PIPE, shell=True)
	for line in networktransmitinfo.stdout:
		nettransmit = str(line.strip())

	    
    ###################
	#Sending the data to Graphite UI        
	IP = '127.0.0.1'
	PORT = 2003
	a = datetime.now()
			
	#MemInfo Data
	MemUsage = 'Centos.MemUsage ' + memfree + ' %d\n ' % int(time())
	print MemUsage
		
	#CPUUsage Data
	CPUUsage = 'Centos.CPUUsage ' + cpuusage + ' %d\n ' % int(time())
	print CPUUsage

	#CPUAvailable Data
	CPUAvailable = 'Centos.CPUAvailable ' + cpuavailable + ' %d\n ' % int(time())
	print CPUAvailable

	#NetworkReceived Data
	NetworkReceived = 'Centos.NetworkReceived ' + netreceived + ' %d\n ' % int(time())
	print NetworkReceived

	#NetworkTransmit Data
	NetworkTransmit = 'Centos.NetworkTransmit ' + nettransmit + ' %d\n ' % int(time())
	print NetworkTransmit	

	#IORead Data
	IORead = 'Centos.IORead ' + IORead  + ' %d\n ' % int(time())
	print IORead

	#IOWrite Data
	IOWrite = 'Centos.IOWrite ' + IOWrite  + ' %d\n ' % int(time())
	print IOWrite



	try:
			
		ssh = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ssh.connect((IP,PORT))
		ssh.send(MemUsage)
		ssh.send(CPUUsage)
		ssh.send(CPUAvailable)
		ssh.send(NetworkReceived)
		ssh.send(NetworkTransmit)
		ssh.send(IORead)
		ssh.send(IOWrite)
		
	
	except Exception as e:
		print e;
	ssh.shutdown(socket.SHUT_WR)
			
	time.sleep(20)

# Schedules job_function to be run once each minute
sched.add_cron_job(job_function,  minute='0-59')