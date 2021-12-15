#!/usr/bin/env python

try:
	import cv2
	import subprocess
	from nudenet import NudeClassifierLite
except:
	print("You have to install openCv subprocess nudenet - pip3 install opencv-python nudenet ")
	exit()


class Video2Frames:
	# Linux Command to Find the total number of frames in the video
	command = "ffmpeg -i {path} -vcodec copy -f rawvideo -y /dev/null 2>&1 | tr ^M '\n' | awk '/^frame=/ {print $2}'|tail -n 1"
	
	def __init__(self, videoPath=None) -> None:
		self.videoPath = videoPath

	def findFramesNumber(self):
		numberOfFrames = subprocess.run(self.command.format(path=self.videoPath),capture_output=True,shell=True).stdout.decode("utf-8").strip()
		return numberOfFrames

	def extractFrames(self):
		# Opens the Video file
		videoFile = cv2.VideoCapture(self.videoPath)
		counter=0
        
		while(videoFile.isOpened()):
			ret, frame = videoFile.read()
			if ret == False:
				break
			cv2.imwrite('Frames/Frame-'+str(counter)+'.jpg',frame)
			counter+=1
		videoFile.release()



class FamilyFriendly():
	
	def __init__(self, videoPath=None) -> None:
		self.BadFrames = []
		self.VideoPath = videoPath
		self._name = 'FamilyFriendly-{x}'.format(x=self.VideoPath.replace("/",''))
		self._fourcc = cv2.VideoWriter_fourcc(*'MP4V')
		self._out = cv2.VideoWriter(self._name, self._fourcc, 30.0, (1920,1080))
		self.classifier_lite = NudeClassifierLite()


	def writeFrame(self,frame):
		self._out.write(frame)
		
	def vision(self,frame):
		cv2.imwrite('Frame.jpg',frame)
		result = self.classifier_lite.classify('Frame.jpg')
		return result.get(list(result.keys())[0])


	def Good(self, frame):
		VisonResult = self.vision(frame)
		#print(VisonResult["safe"],VisonResult["unsafe"])
		if VisonResult["safe"] > 0.5 :
			return True

	def processFrame(self,frame,counter):
		if self.Good(frame):
			self.writeFrame(frame)
			print(counter)
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



'''

# initialize classifier (downloads the checkpoint file automatically the first time)
classifier_lite = NudeClassifierLite()

# Classify video
# Returns {"metadata": {"fps": FPS, "video_length": TOTAL_N_FRAMES, "video_path": 'path_to_video'},
#          "preds": {frame_i: {'safe': PROBABILITY, 'unsafe': PROBABILITY}, ....}}




# Classify single image
classifier_lite.classify('path_to_image_1')
# Returns {'path_to_image_1': {'safe': PROBABILITY, 'unsafe': PROBABILITY}}
# Classify multiple images (batch prediction)
# batch_size is optional; defaults to 4
classifier_lite.classify(['path_to_image_1', 'path_to_image_2'])
# Returns {'path_to_image_1': {'safe': PROBABILITY, 'unsafe': PROBABILITY},
#          'path_to_image_2': {'safe': PROBABILITY, 'unsafe': PROBABILITY}}


print(result)


'''
