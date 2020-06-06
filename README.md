# Youtube-Uploader
Hi,
  This web application is an example for uploading video in Youtube through file upload or after recording through web cam.
 
 Libraries
 -----------------
 1. google-api-python-client :- used for access google api
 2. OpenCV :- Record Video from Webcam and edit for face-detection (Check example online somewhere)
 3. PyAudio :- Record Audio (because opencv supports raw image recording)
 4. Numpy
 5. Werkzeug 
 6. Flask :- For web application

Step1. Download repo
Step2. Unzip it
Step3. Open cmd in youtube_uploader folder
Step4. run "pip install -r requirements.txt" (pip3 for python3)
Step5. run app.py "python app.py"
Step6. open browser with localhost:5000 and use
-------------
 1. You may face installing PyAudio--search in youtube
 2. setup youtube api and oauth credential from your google account -- use console.developer.google.com.. you will find help there

-------------------
 Probelm in this app :
 Running on thread may stuck your performance...........
