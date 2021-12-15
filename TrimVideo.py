#!/usr/bin/env python

try:
	from uuid import uuid4
	from sys import argv
	import subprocess
except:
	print("Install these: [sys , subprocess , uuid] , ffmpeg ")

class Video():
	cutCommand = "ffmpeg -i {inputVideoName} -ss {startCutting} -to {endCutting} -map 0 -c copy {outVideoName}"
	mergeCommand = "ffmpeg -f concat -i {inputVideosNames} -map 0 -c copy {outVideoName}"
	DuractionCommand = "ffmpeg -i {inputVideoName} 2>&1 | grep Duration | awk \'{{print $2}}' | tr -d ,"
	
	def __init__(self, inputVideoName, startCutting=None, endCutting=None, outVideoName="out" ) -> None:
		self.inputVideoName = inputVideoName
		self.startCutting = startCutting
		self.endCutting = endCutting
		self.extension = self.inputVideoName[self.inputVideoName.rfind("."):]
		self.outVideoName = outVideoName if outVideoName.endswith((".mp4",".webm",".mkv",".wmv")) else outVideoName + self.extension
		self.inputVideoFile = None

	# check if the time format is like 00:00:00
	# refactor this to multi function validate or Regx 
	def validateTimeFormat(self):
		if (len(self.startCutting),len(self.endCutting)) == (8,8) : # length Must be 8 
			if ( self.startCutting[2], self.endCutting[2] ,self.startCutting[5] , self.endCutting[5] ) == (':',':',':',':') : # Must have : separator 
				allInput = self.startCutting.replace(":","") + self.endCutting.replace(":","") # remove : to check if all is digits
				checkAllisDigit = list(map(lambda x: x.isdigit(), allInput)) # make array T or F for every value
				if False in checkAllisDigit:
					return False
				else:
					return True
			else:
				return False
		else:
			return False
	
	# Trim Video from [x] self.startCutting to [y] self.endCutting Then save the output
	def trimVideo(self):
		if self.inputVideoName and self.startCutting and self.endCutting:
			# check first if start and end is will formated
			if self.validateTimeFormat():
				command = self.cutCommand.format(inputVideoName=self.inputVideoName, startCutting=self.startCutting, endCutting=self.endCutting, outVideoName=str(uuid4().hex[:4])+"."+self.outVideoName)
				try:
					cutOutput = subprocess.run(command,capture_output=True,shell=True)
					if not cutOutput.returncode:
						return True
					else:
						return False
				except:
					print("Error while Cutting Video") # error during running the command
			else:
				print("Bad Time Format [00H:00M:00S]")
				return False
	
	# create file contains file 'firstCut.mp4'\nfile 'secondCut.mp4'
	def createInputVideosNames(self):
		InputVideosNames = subprocess.run("ls -t *out.???",capture_output=True,shell=True) # sort files based on time 
		if InputVideosNames.returncode == 0:
			inputVideoNames = InputVideosNames.stdout.decode("utf-8").strip().split("\n")
			inputVideoNames.reverse()

			outNames = open("input.txt","w") 
			for videoName in inputVideoNames:
				outNames.write("file "+"'{0}'".format(videoName)+'\n')
			else:
				outNames.close()
				self.inputVideoFile = "input.txt" 
				return True
		else:
			return False # No Out*


	# Merge All Good Ones  
	def mergeAll(self):
		if self.inputVideoFile:
			MergeCommand = self.mergeCommand.format(inputVideosNames=self.inputVideoFile, outVideoName='{0}.'.format(self.inputVideoName)+'FamilyFriendly'+self.extension)
			try:
				MergOutput = subprocess.run(MergeCommand,capture_output=True,shell=True)
				if not MergOutput.returncode:
					return True
				else:
					return False
			except:
				print("Error while Cutting Video") # error during running the command
		else:
			print("No Input File")

	# find the full duration of the video - Last second
	def endDuraction(self):
		EndOfVideo = subprocess.run(self.DuractionCommand.format(inputVideoName=self.inputVideoName),capture_output=True,shell=True).stdout.decode("utf-8").strip()
		EndOfVideo = EndOfVideo[:EndOfVideo.rfind(".")]
		return EndOfVideo

	# Generate Parts without Bad ones
	def cutPart(self, ListOfBadParts=None):
		if ListOfBadParts: # if it list of bad parts
			firstMinute = "00:00:00"
			for (index, (start, end)) in enumerate(ListOfBadParts):
				if index+1 < len(ListOfBadParts):
					print(firstMinute,"To", start,end=" > ")
					self.startCutting , self.endCutting = firstMinute, start
					r = self.trimVideo()
					print(r)
					next = ListOfBadParts[index+1][0] # Find the next element startCutting
					print(end,"To",next,end=" > ")
					self.startCutting , self.endCutting = end, next
					r = self.trimVideo()
					print(r)
					firstMinute = next
				else:
					endTime = self.endDuraction() # find the the last minute
					next = ListOfBadParts[-1][1] # last cut 
					print(next,"To", endTime, end=" > ")
					self.startCutting , self.endCutting = next, endTime
					r = self.trimVideo()
					print(r)
			else:
				return True # after finish the loop
		else: # single part to cut
			BadParts = [self.startCutting , self.endCutting]
			try:
				self.startCutting, self.endCutting = '00:00:00', BadParts[0]
				r1 = self.trimVideo()
				self.startCutting, self.endCutting = BadParts[1], self.endDuraction()
				r2 = self.trimVideo()
				return True
			except:
				print("Exception")
				return False
			

	def deletePart(self, ListOfBadParts ):
		if ListOfBadParts: # list of bad to cut
			GoodParts = self.cutPart(ListOfBadParts=ListOfBadParts) # generate good parts
			if GoodParts:
				self.createInputVideosNames()
				merged = self.mergeAll() # merge all good
				return merged
		else: # if single cut 
			r = self.cutPart()
			self.createInputVideosNames()
			x = self.mergeAll()
		

	def clean(self):
		cleaningResult = subprocess.run("rm input.txt *out.??? ",capture_output=True,shell=True)
		return cleaningResult

if __name__ == '__main__':
	help = "\n-i [ input File Name ]\n-start [ Houar:Minute:Second ]\n-end [ Houar:Minute:Second ]\n-o [ output File Name ]"
	if len(argv) == 1 :
		print(help)
	else:
		#videoName, start ,end = argv[1], argv[2], argv[3]
		videoName = argv[1]
		BadParts = [["00:04:00","00:06:00"],["00:15:00","00:18:00"]]
		newVideo = Video(inputVideoName=videoName)
		result = newVideo.deletePart(ListOfBadParts=BadParts)
		print("Deleting Temp Files")
		newVideo.clean()
		# we will edit this to make a nudity algoritm detections