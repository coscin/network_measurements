import os
import sys
import time
import signal
import multiprocessing
import subprocess

from experiments import *


targetFile=""
tcpstatProc=None
fileChangeInterval="86400"   # start writing to a new file after every 86400 sec (24 hrs)


############################################################
############## List of available experiments ###############
############## Add the name of a new exp here ##############
############################################################

latencyExpList = ['ping']
bandwidthExpList = ['iperf', 'netperf']
tputExpList = ['scp', 'rsync', 'gridFTP']


############################################################
##################### Helper Functions #####################
############################################################

def parseCmdLineArgs(arguments):
	
	if(len(arguments) < 10):
		print "usage: python <script.py> [--sender/--receiver] -i <interface> -s <src IP> -d <remote IP> --experiment [RTlatency/available_bandwidth/throughput]"
		sys.exit(-1)

	script = arguments[0]
	option1 = arguments[1]
	option2 = arguments[2]
	option3 = arguments[4]
	option4 = arguments[6]
	option5 = arguments[8]

	if(not((option1=='--sender' or option1=='--receiver') and option2=='-i' and option3=='-s' and option4=='-d' and option5=='--experiment')):
		print "usage: python <script.py> [--sender/--receiver] -i <interface> -s <src IP> -d <remote IP> --experiment [RTlatency/available_bandwidth/throughput]"
		sys.exit(-1)

	else:
		interface = arguments[3]
		srcIP = arguments[5]
		dstIP = arguments[7]
		experiment = arguments[9]

		if(not(experiment=='RTlatency' or experiment=='available_bandwidth' or experiment=='throughput')):
			print "Error: wrong experiment name [RTlatency/available_bandwidth/throughput]"
			sys.exit(-1)

		else:
			return (option1, interface, srcIP, dstIP, experiment)


def displayOptions(expList):
	
	if(len(expList)==0):
		print "Error: No available experiment"
		sys.exit(-1)

	elif(len(expList)==1):
		return expList[0]

	elif(len(expList)>1):
		count=1
		print "List of available experiments:"

		for exp in expList:
			print "  "+str(count)+" "+exp
			count = count + 1

		optNum = raw_input("Choose the option number: ")
		if(int(optNum) >= 1 and int(optNum) < count):
			return expList[int(optNum)-1]
		else:
			print "Error: Wrong option selected"
			sys.exit(-1)


def isNetworkUp(srcIP, dstIP):
	
	response = os.system("ping -c 1 -I " + srcIP + " " + dstIP + " > /dev/null")
	if(response == 0):
		return True
	else:
		return False


def sighandler1(signum, frame):
	
	if(tcpstatProc!=None):
		if(os.path.isfile(targetFile)):
			os.system("cp "+targetFile+" "+targetFile+"-v1")
			os.system("rm "+targetFile)

		tcpstatProc.terminate()


def sighandler2(signum, frame):
	
	cleanup()
	sys.exit(-1)


def cleanup():
	
	if(runningExp!=None):
		runningExp.terminate()

	if(tcpstatProc!=None):
		if(os.path.isfile(targetFile)):
			os.system("cp "+targetFile+" "+targetFile+"-v1")
			os.system("rm "+targetFile)

		tcpstatProc.terminate()
	
	print "Clean-up done.. Exiting.."



############################################################
####################### Experiments ########################
############################################################

def roundTripLatency(srcIP, dstIP, chosenOption):
	
	signal.signal(signal.SIGINT, sighandler2)

	if(not os.path.isdir("round_trip_latency")):
		os.mkdir("round_trip_latency")
	if(not os.path.isdir("round_trip_latency/"+chosenOption)):
		os.mkdir("round_trip_latency/"+chosenOption)

	targetDir = "round_trip_latency/"+chosenOption

	print "Running " + chosenOption + ".."

	while(True):

		startTime = time.strftime("%Y:%m:%d-%H:%M:%S", time.gmtime())
		targetFile = targetDir+"/"+startTime
		
		if(chosenOption == 'ping'):
			ping(srcIP, dstIP, targetFile, fileChangeInterval)

		time.sleep(2)


def availBandwidth(srcIP, dstIP, chosenOption):
	
	signal.signal(signal.SIGINT, sighandler2)

	print "Running " + chosenOption + ".."

	while(True):

		if(chosenOption=='iperf'):
			iperf_client(srcIP, dstIP)

		elif(chosenOption=='netperf'):
			netperf(srcIP, dstIP)

		time.sleep(2)


def throughput(filename, srcIP, dstIP, dstUser, dstPath, pid, chosenOption):
	
	signal.signal(signal.SIGINT, sighandler2)

	print "Running " + chosenOption + ".."

	if(chosenOption=='scp'):
		scp(filename, srcIP, dstIP, dstUser, dstPath)

	elif(chosenOption=='rsync'):
		rsync(filename, srcIP, dstIP, dstUser, dstPath)

	elif(chosenOption=='gridFTP'):
		gridFTP(filename, dstIP, dstPath)

	try:
		os.kill(int(pid), signal.SIGINT)
	except:
		return



##############################################################
##################### Stats Collection #######################
##############################################################

def fileChange(pid):
	
	signal.signal(signal.SIGINT, sighandler2)

	while(True):
		time.sleep(int(fileChangeInterval))

		try:
			os.kill(int(pid), signal.SIGUSR1)
		except:
			return


def tcpstatCollector(interface, experiment, chosenOption):
	
	signal.signal(signal.SIGUSR1, sighandler1)
	signal.signal(signal.SIGINT, sighandler2)

	targetDir = ""

	if(experiment=='throughput'):
		if(not os.path.isdir("throughput")):
			os.mkdir("throughput")
		if(not os.path.isdir("throughput/"+chosenOption)):
			os.mkdir("throughput/"+chosenOption)
		targetDir = "throughput/"+chosenOption

	elif(experiment=='available_bandwidth'):
		if(not os.path.isdir("available_bandwidth")):
			os.mkdir("available_bandwidth")
		if(not os.path.isdir("available_bandwidth/"+chosenOption)):
			os.mkdir("available_bandwidth/"+chosenOption)
		targetDir = "available_bandwidth/"+chosenOption

	print "Starting tcpstat.."

	while(True):
		startTime = time.strftime("%Y:%m:%d-%H:%M:%S", time.gmtime())
		global targetFile
		targetFile = targetDir+"/"+startTime

		global tcpstatProc
		tcpstatProc = subprocess.Popen("sudo tcpstat -s " + fileChangeInterval + " -i " + interface + " 1 >> " + targetFile, shell=True)
		tcpstatProc.wait()

		time.sleep(2)
		


###########################################################
##################### Main Function #######################
###########################################################

def main():
	
	# install dependencies
	os.system("sudo apt-get install openssh-server -y > /dev/null")
	os.system("sudo apt-get install openssh-client -y > /dev/null")
	os.system("sudo apt-get install traceroute -y > /dev/null")
	os.system("sudo apt-get install iperf -y > /dev/null")
	os.system("sudo apt-get install netperf -y > /dev/null")
	os.system("sudo apt-get install tcpstat -y > /dev/null")

	signal.signal(signal.SIGINT, sighandler2)

	processType, interface, srcIP, dstIP, experiment = parseCmdLineArgs(sys.argv)

	netStatus = isNetworkUp(srcIP, dstIP)

	if(netStatus):
		print "\n------------------------------------------"
		print "Network is UP!!!"
		os.system("traceroute -s " + srcIP + " " + dstIP)
		print "------------------------------------------\n"
	else:
		print "\n------------------------------------------"
		print "Network is DOWN!!!"
		print "Exiting..."
		print "------------------------------------------\n"
		sys.exit(-1)


	if(processType=='--sender'):

		if(experiment=='RTlatency'):

			chosenOption = displayOptions(latencyExpList)
			roundTripLatency(srcIP, dstIP, chosenOption)

		elif(experiment=='throughput' or experiment=='available_bandwidth'):

			if(experiment=='throughput'):

				chosenOption = displayOptions(tputExpList)

				if(chosenOption=='gridFTP'):
					filename = raw_input("Enter the absolute path of file on host machine to transfer: ")
					dstPath = raw_input("Enter the absolute destination path for the file on remote machine: ")
					dstUser = ""

				else:
					filename = raw_input("Enter the path of file on host machine to transfer: ")
					dstUser = raw_input("Enter remote username: ")
					dstPath = raw_input("Enter the destination path for the file on remote machine: ")

				p1 = multiprocessing.Process(target=tcpstatCollector, args=(interface, experiment, chosenOption,))
				p1.start()
			
				p2 = multiprocessing.Process(target=throughput, args=(filename, srcIP, dstIP, dstUser, dstPath, p1.pid, chosenOption,))
				p2.start()

				p3 = multiprocessing.Process(target=fileChange, args=(p1.pid,))
				p3.start()

				p1.join()
				p2.join()
				p3.join()

			elif(experiment=='available_bandwidth'):

				chosenOption = displayOptions(bandwidthExpList)

				p1 = multiprocessing.Process(target=tcpstatCollector, args=(interface, experiment, chosenOption,))
				p1.start()

				p2 = multiprocessing.Process(target=availBandwidth, args=(srcIP, dstIP, chosenOption,))
				p2.start()

				p3 = multiprocessing.Process(target=fileChange, args=(p1.pid,))
				p3.start()

				p1.join()
				p2.join()
				p3.join()

	elif(processType=='--receiver'):

		if(experiment=='RTlatency'):
			#chosenOption = displayOptions(latencyExpList)
			# do nothing
			pass

		elif(experiment=='throughput' or experiment=='available_bandwidth'):

			if(experiment=='throughput'):
				#chosenOption = displayOptions(tputExpList)
				# do nothing
				pass

			if(experiment=='available_bandwidth'):
				chosenOption = displayOptions(bandwidthExpList)

				if(chosenOption=='iperf'):
					iperf_server(srcIP)



if __name__ == '__main__': main()



