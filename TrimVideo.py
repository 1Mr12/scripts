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

    # Trim Video from [x] to [y] Then save the output
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
            MergeCommand = self.mergeCommand.format(inputVideosNames=self.inputVideoFile, outVideoName='FamilyFriendly'+self.extension)
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

    def deletePart(self):
        r = self.cutPart()
        self.createInputVideosNames()
        x = self.mergeAll()

    def clean(self):
        cleaningResult = subprocess.run("rm input.txt *out.??? ",capture_output=True,shell=True)

if __name__ == '__main__':
    help = "\n-i [ input File Name ]\n-start [ Houar:Minute:Second ]\n-end [ Houar:Minute:Second ]\n-o [ output File Name ]"
    if len(argv) < 3:
        print(help)
    else:
        videoName, start ,end = argv[1], argv[2], argv[3]
        newVideo = Video(inputVideoName=videoName, startCutting=start, endCutting=end)
        result = newVideo.deletePart()
        newVideo.clean()