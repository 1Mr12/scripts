#!/usr/bin/env python

from uuid import uuid4
from sys import argv
import subprocess

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
	# refactor this to multi function validate
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
			command = self.cutCommand.format(inputVideoName=self.inputVideoName, startCutting=self.startCutting, endCutting=self.endCutting, outVideoName=str(uuid4().hex[:4])+"."+self.outVideoName)
			try:
				cutOutput = subprocess.run(command,capture_output=True,shell=True)
				if not cutOutput.returncode:
					return True
				else:
					return False
			except:
				print("Error while Cutting Video") # error during running the command

	# create file contains file 'firstCut.mp4'\nfile 'secondCut.mp4'
	def createInputVideosNames(self):
		InputVideosNames = subprocess.run("ls -t *out.???",capture_output=True,shell=True)
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
				print(MergOutput.returncode)
				print(MergOutput.stdout.decode("utf-8"))
				if not MergOutput.returncode:
					return True
				else:
					return False
			except:
				print("Error while Cutting Video") # error during running the command
		else:
			print("No Input File")

	def endDuraction(self):
		EndOfVideo = subprocess.run(self.DuractionCommand.format(inputVideoName=self.inputVideoName),capture_output=True,shell=True).stdout.decode("utf-8").strip()
		EndOfVideo = EndOfVideo[:EndOfVideo.rfind(".")]
		return EndOfVideo

	# Generate Parst withou Bad ones
	def cutPart(self):
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

	def cutParts(self, ListOfBadParts ):
		firstMinute = "00:00:00"
		for (index, (start, end)) in enumerate(ListOfBadParts):
			if index+1 < len(ListOfBadParts):
				print(firstMinute, start)
				self.startCutting , self.endCutting = firstMinute, start
				r = self.trimVideo()
				print(r)
				print(end,"To",ListOfBadParts[index+1][0])
				self.startCutting , self.endCutting = end, ListOfBadParts[index+1][0]
				r = self.trimVideo()
				print(r)
				firstMinute = end
			else:
				endTime = self.endDuraction()
				print(firstMinute,"To", endTime)
				self.startCutting , self.endCutting = firstMinute, endTime
				self.trimVideo()
		else:
			return True
			

	def deletePart(self):
		r = self.cutPart()
		self.createInputVideosNames()
		x = self.mergeAll()
	
	def deleteParts(self, ListOfBadParts):
		GoodParts = self.cutParts(ListOfBadParts)
		if GoodParts:
			self.createInputVideosNames()
			merged = self.mergeAll()
			return merged


	def clean(self):
		cleaningResult = subprocess.run("rm input.txt *out.??? ",capture_output=True,shell=True)

if __name__ == '__main__':
	help = "\n-i [ input File Name ]\n-start [ Houar:Minute:Second ]\n-end [ Houar:Minute:Second ]\n-o [ output File Name ]"
	if len(argv) == 1 :
		print(help)
	else:
		#videoName, start ,end = argv[1], argv[2], argv[3]
		videoName = argv[1]
		BadParts = [["00:00:05","00:00:15"],["00:00:30","00:00:60"]]
		newVideo = Video(inputVideoName=videoName)
		result = newVideo.deleteParts(ListOfBadParts=BadParts)
		print("Deleting Temp Files")
		newVideo.clean()