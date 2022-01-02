#!/usr/bin/env python

try:
	import cv2
	import subprocess
	from nudenet import NudeClassifierLite
	import argparse

except:
	print("You have to install openCv subprocess nudenet - pip3 install opencv-python nudenet argparse ")
	exit()


class Video2Frames:
	# Linux Command to Find the total number of frames in the video
	command = "ffmpeg -i {path} -vcodec copy -f rawvideo -y /dev/null 2>&1 | tr ^M '\n' | awk '/^frame=/ {print $2}'|tail -n 1"
	
	def __init__(self, videoPath=None) -> None:
		self.VideoPath = videoPath

	def findFramesNumber(self):
		numberOfFrames = subprocess.run(self.command.format(path=self.videoPath),capture_output=True,shell=True).stdout.decode("utf-8").strip()
		return numberOfFrames

	def extractFrames(self):
		# Opens the Video file
		videoFile = cv2.VideoCapture(self.VideoPath)
		print("Done Reading ",self.VideoPath)
		counter=0
		try:
			subprocess.run("mkdir Frames")
		except:
			print("Found Frames Foldar")

		while(videoFile.isOpened()):
			ret, frame = videoFile.read()
			if ret == False:
				break
			cv2.imwrite('Frames/Frame-'+str(counter)+'.jpg',frame)
			print("\b"*2,end=' ')
			print(counter)
			counter+=1
		videoFile.release()
		print("Done")


class FamilyFriendly(Video2Frames):
	
	def __init__(self, videoPath=None, accurity=.75) -> None:
		self.BadFrames = []
		self.VideoPath = videoPath
		self._name = 'FamilyFriendly-{x}'.format(x=self.VideoPath.replace("/",''))
		self._fourcc = cv2.VideoWriter_fourcc(*'MP4V')
		self._out = cv2.VideoWriter(self._name, self._fourcc, 30.0, (1920,1080))
		self.classifier_lite = NudeClassifierLite()
		self.accurity=accurity


	def writeFrame(self,frame):
		self._out.write(frame)
		
	def vision(self,frame):
		cv2.imwrite('Frame.jpg',frame)
		result = self.classifier_lite.classify('Frame.jpg')
		return result.get(list(result.keys())[0])


	def Good(self, frame):
		VisonResult = self.vision(frame)
		if VisonResult["unsafe"] > self.accurity :
			print(VisonResult["unsafe"], "UnSafe")
			return False
		else:
			print(VisonResult["safe"] , "Safe")
			return True

	def processFrame(self,frame,counter):
		if self.Good(frame):
			self.writeFrame(frame)
			print("Writing Frame Number: ",counter)
		else:
			print("Delete Frame number",counter)
			cv2.imwrite('tmp/Frame-'+str(counter)+'.jpg',frame)

	def deleteBadFrames(self):
		videoFile = cv2.VideoCapture(self.VideoPath)
		counter=0
        
		while(videoFile.isOpened()):
			ret, frame = videoFile.read()
			if ret == False:
				break
			else:
				self.processFrame(frame,counter)
			counter+=1
		
		videoFile.release()
	
	def clean(self):
		self._out.release()





if __name__=='__main__':
	parser = argparse.ArgumentParser(description="argument")
	parser.add_argument('-i','--input',help="input video name",type=str)
	parser.add_argument('-t','--type',help="low, medium, high",type=str)
	parser.add_argument('-a','--accurity',help="number from .1 to .9",type=float)

	parser.add_argument('-v','--v',help="print help",type=str)

	args = parser.parse_args()
	if args.v:
		print("-i input video name\n-t type of algorithm low, medium, high\n-h print help")
		exit()
	else:
		print(args.input,args.type,args.accurity)
		if args.type == "high":
			video = FamilyFriendly(videoPath=args.input, accurity=args.accurity)
			video.deleteBadFrames()







'''
if path and option == "1" :
		video = FamilyFriendly(videoPath=path)
		video.deleteBadFrames()
	elif path and option == "2":
		video = FamilyFriendly(videoPath=path)
		video.extractFrames()
		x = subprocess.run("find Frames/*",capture_output=True,shell=True).stdout.decode("utf-8").strip()
		x = x.split()
		classifier_lite = NudeClassifierLite()
		xresult = classifier_lite.classify(x)
		print(xresult)
'''