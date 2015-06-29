import os
import sys
import subprocess


runningExp=None


def ping(srcIP, dstIP, targetFile, fileChangeInterval):
	global runningExp
	runningExp = subprocess.Popen("ping -c " + fileChangeInterval + " -I " + srcIP + " " + dstIP + " >> " + targetFile, shell=True)
	runningExp.wait()


def iperf_client(srcIP, dstIP):
	global runningExp
	runningExp = subprocess.Popen("iperf -c " + dstIP + " -B " + srcIP + " -P 5 > /dev/null 2>&1", shell=True)
	runningExp.wait()


def iperf_server(srcIP):
	global runningExp
	runningExp = subprocess.Popen("iperf -s " + " -B " + srcIP, shell=True)
	runningExp.wait()


def netperf(srcIP, dstIP):
	global runningExp
	runningExp = subprocess.Popen("netperf -t TCP_STREAM -H " + dstIP + " -i 10 -P 0 > /dev/null", shell=True)
	runningExp.wait()


def scp(filename, srcIP, dstIP, dstUser, dstPath):
	global runningExp
	
	if(os.path.isdir(dstPath)):
		
		dstPath_list = list(dstPath)
		if(dstPath_list[len(dstPath_list)-1]!='/'):
			dstPath = dstPath + "/"
	
	if(os.path.isdir(filename)):

		filename_list = list(filename)
		if(filename_list[len(filename_list)-1]!='/'):
			filename = filename + "/"

		runningExp = subprocess.Popen("scp -r -oBindAddress=" + srcIP + " " + filename + " " + dstUser + "@" + dstIP + ":" + dstPath, shell=True)
	
	else:
		
		runningExp = subprocess.Popen("scp -oBindAddress=" + srcIP + " " + filename + " " + dstUser + "@" + dstIP + ":" + dstPath, shell=True)
	
	runningExp.wait()


def rsync(filename, srcIP, dstIP, dstUser, dstPath):
	global runningExp
	
	if(os.path.isdir(dstPath)):
		
		dstPath_list = list(dstPath)
		if(dstPath_list[len(dstPath_list)-1]!='/'):
			dstPath = dstPath + "/"
	
	if(os.path.isdir(filename)):

		filename_list = list(filename)
		if(filename_list[len(filename_list)-1]!='/'):
			filename = filename + "/"

		runningExp = subprocess.Popen("rsync -av -P -r " + filename + " " + dstUser + "@" + dstIP + ":" + dstPath + " --address=" + srcIP, shell=True)
	
	else:

		runningExp = subprocess.Popen("rsync -av -P " + filename + " " + dstUser + "@" + dstIP + ":" + dstPath + " --address=" + srcIP, shell=True)
	
	runningExp.wait()


def gridFTP(filename, dstIP, dstPath):
	global runningExp

	if(os.path.isdir(dstPath)):
		
		dstPath_list = list(dstPath)
		if(dstPath_list[len(dstPath_list)-1]!='/'):
			dstPath = dstPath + "/"
	
	if(os.path.isdir(filename)):

		filename_list = list(filename)
		if(filename_list[len(filename_list)-1]!='/'):
			filename = filename + "/"

		runningExp = subprocess.Popen("globus-url-copy -tcp-bs 2097152 -p 4 -vb -r -cd file://" + filename + " sshftp://" + dstIP + dstPath, shell=True)
	
	else:

		runningExp = subprocess.Popen("globus-url-copy -tcp-bs 2097152 -p 4 -vb file://" + filename + " sshftp://" + dstIP + dstPath, shell=True)
	
	runningExp.wait()



