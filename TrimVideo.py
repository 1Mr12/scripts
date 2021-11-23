#!/usr/bin/env python

from sys import argv
import subprocess

class Video():
    cutCommand = "ffmpeg -i {inputVideoName} -ss {startCutting} -to {endCutting} -map 0 -c copy {outVideoName}"
    mergeCommand = "ffmpeg -f concat -i inputVideosNames.txt -map 0 -c copy {outVideoName}"
    def __init__(self, inputVideoName, startCutting, endCutting, outVideoName="out" ) -> None:
        self.inputVideoName = inputVideoName
        self.startCutting = startCutting
        self.endCutting = endCutting
        self.extension = self.inputVideoName[self.inputVideoName.rfind("."):]
        self.outVideoName = outVideoName if outVideoName.endwith((".mp4",".webm",".mkv",".wmv")) else outVideoName + self.extension

    # Trim Video from [x] to [y] Then save the output
    def trimVideo(self):
        if self.inputVideoName and self.startcutting and self.endCutting:
            command = self.cutCommand.format(inputVideoName=self.inputVideoName, startCutting=self.startCutting, endCutting=self.endCutting, outVideoName=self.outVideoName)
            try:
                cutOutput = subprocess.run(command,capture_output=True,shell=True)
                return True
            except:
                return False # error during running the command

    # Delete Part From a video        
    def trimPartFromVideo(self):
        pass


if __name__ == '__main__':
    help = "\n-i [ input File Name ]\n-start [ Houar:Minute:Second ]\n-end [ Houar:Minute:Second ]\n-o [ output File Name ]"
    if len(argv) < 3:
        print(help)
    else:
        pass