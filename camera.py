import cv2
import threading
import os 
import datetime
from flask import request
import pyaudio
import wave
import subprocess
import time

class RecordingThread (threading.Thread):

    def __init__(self, name, camera, file, flag):
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True
        self.flag = flag
        self.file = file

        if self.flag == True:
            self.cap = camera
            self.frame_counts = 1
            self.start_time = time.time()
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            self.out = cv2.VideoWriter(self.file, fourcc, 20.0, (640,480))
        else:
            self.open = True
            self.rate = 44100
            self.frames_per_buffer = 1024
            self.channels = 2
            self.format = pyaudio.paInt16
            self.audio_filepath = file
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(format=self.format,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer = self.frames_per_buffer)
            self.audio_frames = []

    def run(self):
        if self.flag == True:
            while self.isRunning:
                ret, frame = self.cap.read()
                if ret:
                    self.frame_counts += 1
                    self.out.write(frame)

            self.out.release()
        else:
            self.stream.start_stream()
            while(self.open == True):
                data = self.stream.read(self.frames_per_buffer) 
                self.audio_frames.append(data)
                if self.open==False:
                    break

    def stop(self):
        self.isRunning = False
        if self.flag == False:
            if self.open==True:
                self.open = False
                self.stream.stop_stream()
                self.stream.close()
                self.audio.terminate()
                
                waveFile = wave.open(self.audio_filepath, 'wb')
                waveFile.setnchannels(self.channels)
                waveFile.setsampwidth(self.audio.get_sample_size(self.format))
                waveFile.setframerate(self.rate)
                waveFile.writeframes(b''.join(self.audio_frames))
                waveFile.close()
            pass
        else: 
            self.out.release()
            self.cap.release()

    def __del__(self):
        if self.flag == False:
            self.stop()
        else:
            self.cap.release()
            self.out.release()

class VideoCamera(object):
    def __init__(self):
        # Open a camera
        self.cap = cv2.VideoCapture(0)
      
        # Initialize video recording environment
        self.is_record = False
        self.out = None

        # Thread for recording
        self.recordingThread = None
        self.audioThread = None
    
    def __del__(self):
        self.cap.release()
    
    def get_frame(self):
        ret, frame = self.cap.read()

        if ret:
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        else:
            return None

    # Required and wanted processing of final files
    def file_manager(self, maindir):
        print(maindir)
        if os.path.exists(str(maindir) + "/temp_audio.wav"):
            os.remove(str(maindir) + "/temp_audio.wav")
        
        if os.path.exists(str(maindir) + "/temp_video.avi"):
            try:
                os.remove(str(maindir) + "/temp_video.avi")
            except:
                with open(str(maindir) + "/temp_video.avi", "rb") as f:
                    f.close()
                    os.remove(str(maindir) + "/temp_video.avi")

        if os.path.exists(str(maindir) + "/temp_video2.avi"):
            os.remove(str(maindir) + "/temp_video2.avi")

        if os.path.exists(str(maindir) + "/main_video.avi"):
            os.remove(str(maindir) + "/main_video.avi")

        if os.path.isdir(maindir):
            os.rmdir(maindir)

    def start_record(self):
        print('====Recording Started=========')
        self.is_record = True
        
        #create subfolder in upload directory
        innerdir = request.remote_addr.replace('.','-') #datetime.datetime.now()
        maindir = './uploads/'+innerdir
        self.file_manager(maindir)
        if os.path.isdir(maindir) == False:
            os.makedirs(maindir)
        vfilename  = 'temp_video.avi'
        vfilepath = os.path.join(maindir, vfilename)
        afilename = 'temp_audio.wav'
        afilepath = os.path.join(maindir, afilename)

        self.out = vfilepath
        self.recordingThread = RecordingThread("Video Recording Thread", self.cap, self.out, True)
        self.recordingThread.setDaemon = True
        self.recordingThread.start()
        self.audioThread = RecordingThread("Audio Recording Thread", None, afilepath, False)
        self.audioThread.setDaemon = True
        self.audioThread.start()
        return maindir

    def stop_record(self):
        print('====Recording Stopped=========')
        self.is_record = False
        self.cap.release()
        innerdir = request.remote_addr.replace('.','-')
        maindir = './uploads/'+innerdir
        self.stop_AVrecording(maindir)

        return maindir

    def stop_AVrecording(self, maindir):

        if self.recordingThread != None and self.audioThread !=None:
            self.audioThread.stop()
            frame_counts = self.recordingThread.frame_counts
            elapsed_time = time.time() - self.recordingThread.start_time
            recorded_fps = frame_counts / elapsed_time
            print("total frames " + str(frame_counts))
            print("elapsed time " + str(elapsed_time))
            print("recorded fps " + str(recorded_fps))
            self.recordingThread.stop() 

            # Makes sure the threads have finished
            print(threading.active_count())
            while threading.active_count() > 8:
                print(threading.active_count())
                time.sleep(0.1)

            
            print(threading.active_count())

            #	 Merging audio and video signal
            if abs(recorded_fps - 6) >= 0.01:    
                # If the fps rate was higher/lower than expected, re-encode it to the expected          
                print("Re-encoding")
                cmd = "ffmpeg -r " + str(recorded_fps) + " -i "+ maindir +"/temp_video.avi -pix_fmt yuv420p -r 6 "+ maindir +"/temp_video2.avi"
                subprocess.call(cmd, shell=True)
            
                print("Muxing")
                cmd = "ffmpeg -ac 2 -channel_layout stereo -i "+ maindir +"/temp_audio.wav -i "+ maindir +"/temp_video2.avi -pix_fmt yuv420p "+ maindir +"/main_video.avi"
                subprocess.call(cmd, shell=True)
            else:
                print("Normal recording\nMuxing")
                cmd = "ffmpeg -ac 2 -channel_layout stereo -i "+ maindir +"/temp_audio.wav -i "+ maindir +"/temp_video.avi -pix_fmt yuv420p "+ maindir +"/main_video.avi"
                subprocess.call(cmd, shell=True)
                print("..")



            