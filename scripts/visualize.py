import os
import sys
import datetime


expType = ['round_trip_latency', 'available_bandwidth', 'throughput']


def parseRawPingData(inputFile, outputFile):

	tokens = inputFile.split('/')
	tokens1 = tokens[len(tokens)-1].split('-')
	date = tokens1[0].split(':')
	time = tokens1[1].split(':')

	startDateTime = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(time[0]),int(time[1]),int(time[2]))
	
	inp = open(inputFile, 'r')
	out = open(outputFile, 'a')

	count = 0
	delta = 0
	for line in inp:
		latency = ""
		line = line.strip()
		if(count==0):
			count=count+1
			continue
		elif(line==""):
			continue
		elif(line.find("statistics") != -1):
			break

		if(line.find("Request timeout") != -1):
			latency = "0"

		elif(line.find("Destination Host Unreachable") != -1):
			latency = "0"

		else:
			tokens1 = line.split()
			tokens2 = tokens1[len(tokens1)-2].split("=")
			if(tokens2[0]=="time"):
				latency = tokens2[1]
			else:
				continue


		out.write((startDateTime+datetime.timedelta(seconds=delta)).strftime("%Y:%m:%d-%H:%M:%S"))
		out.write(",")

		out.write(latency)
		out.write("\n")

		delta=delta+1

	inp.close()
	out.close()


def parseRawTcpstatData(inputFile, outputFile):

	tokens = inputFile.split('/')
	tokens1 = tokens[len(tokens)-1].split('-')
	date = tokens1[0].split(':')
	time = tokens1[1].split(':')

	startDateTime = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(time[0]),int(time[1]),int(time[2]))

	inp = open(inputFile, 'r')
	out = open(outputFile, 'a')

	delta = 0
	for line in inp:
		line = line.strip()
		
		out.write((startDateTime+datetime.timedelta(seconds=delta)).strftime("%Y:%m:%d-%H:%M:%S"))
		out.write(",")

		tokens1 = line.split()
		tokens2 = tokens1[len(tokens1)-1].split("=")
		val = float(tokens2[1])/1e9
		out.write(str(val))
		out.write("\n")

		delta=delta+1

	inp.close()
	out.close()


def plotGraph(inputFile, outputFile, experimentType):

	configParams = 'set datafile separator ",";'
	configParams = configParams + 'set terminal png size 900,400;'

	if(experimentType=='round_trip_latency'):
		configParams = configParams + 'set ylabel "Round Trip Latency in milli-sec";'
	elif(experimentType=='available_bandwidth'):
		configParams = configParams + 'set ylabel "Bandwidth in Gbps";'
	elif(experimentType=='throughput'):
		configParams = configParams + 'set ylabel "Throughput in Gbps";'
	else:
		print "Error.. Exiting.."
		sys.exit(-1)

	configParams = configParams + 'set xlabel "Time month/day";'
	configParams = configParams + 'set xdata time;'
	configParams = configParams + 'set timefmt "%Y:%m:%d-%H:%M:%S";'
	configParams = configParams + 'set format x "%m/%d";'
	configParams = configParams + 'set grid;'
	configParams = configParams + 'set output "' + outputFile + '";'
	configParams = configParams + 'plot "' + inputFile + '" using 1:2 with lines lw 2 lt 3 title "";'

	plotcmd = 'echo \''+configParams+'\' | gnuplot'

	os.system(plotcmd)


def formatRawData(experimentType, experimentDir):

	inputParentDir = experimentDir
	outputParentDir = experimentDir+"_graphs"

	if(not os.path.isdir(inputParentDir)):
		print "Error: '" + inputParentDir + "' No such file or directory"
		sys.exit(-1)

	if(not os.path.isdir(outputParentDir)):
		os.mkdir(outputParentDir)

	dirList = os.listdir(inputParentDir)
	if(len(dirList)==0):
		print "Error: '" + inputParentDir + "' is empty"
		sys.exit(-1)

	inputParentDir_prev = inputParentDir
	outputParentDir_prev = outputParentDir

	for dirname in dirList:
		inputParentDir = inputParentDir_prev+"/"+dirname

		if(os.path.isdir(inputParentDir)):
			outputParentDir = outputParentDir_prev+"/"+dirname

			if(not os.path.isdir(outputParentDir)):
				os.mkdir(outputParentDir)

			fileList = os.listdir(inputParentDir)
			if(len(fileList)==0):
				"Error: '" + inputParentDir + "' is empty"
				sys.exit(-1)

			fileList.sort()

			outFilename = ""
			if(len(fileList)>0):
				outFilename = fileList[0]+"--"+fileList[len(fileList)-1]
			else:
				return

			if(os.path.isfile(outputParentDir+"/"+outFilename+".dat")):
				continue

			for filename in fileList:
				if(experimentType=='round_trip_latency'):
					if(dirname=='ping'):
						parseRawPingData(inputParentDir+"/"+filename, outputParentDir+"/"+outFilename+".dat")

				elif(experimentType=='available_bandwidth' or experimentType=='throughput'):
					parseRawTcpstatData(inputParentDir+"/"+filename, outputParentDir+"/"+outFilename+".dat")
		
			inputFile = outputParentDir+"/"+outFilename+".dat"
			outputFile = outputParentDir+"/"+outFilename+".png"

			plotGraph(inputFile, outputFile, experimentType)



def main():

	# install dependencies
	os.system("sudo apt-get install gnuplot -y > /dev/null")

	formatRawData(expType[0], 'round_trip_latency')
	print "Round Trip Latency graphs plotted.."

	formatRawData(expType[1], 'available_bandwidth')
	print "Bandwidth graphs plotted.."

	formatRawData(expType[2], 'throughput')
	print "Throughput graphs plotted.."


if __name__ == '__main__': main()


