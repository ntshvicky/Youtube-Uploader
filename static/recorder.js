$("#vid2").hide();
$("#msg").hide();
let btndownload = document.getElementById('btnDownload');
let btnstart = document.getElementById('btnStart');
let btnstop = document.getElementById('btnStop');
let vidSave = document.getElementById('vid2');
btnstart.disabled = false;
btnstop.disabled = true;  
btndownload.disabled = true;
let constraintObj = { 
    audio: true, 
    video: { 
        facingMode: "user", 
        width: 640,
        height: 480
    } 
}; 
// width: 1280, height: 720  -- preference only
// facingMode: {exact: "user"}
// facingMode: "environment"

//handle older browsers that might implement getUserMedia in some way
if (navigator.mediaDevices === undefined) {
    navigator.mediaDevices = {};
    navigator.mediaDevices.getUserMedia = function(constraintObj) {
        let getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
        if (!getUserMedia) {
            return Promise.reject(new Error('getUserMedia is not implemented in this browser'));
        }
        return new Promise(function(resolve, reject) {
            getUserMedia.call(navigator, constraintObj, resolve, reject);
        });
    }
}else{
    navigator.mediaDevices.enumerateDevices()
    .then(devices => {
        devices.forEach(device=>{
            console.log(device.kind.toUpperCase(), device.label);
            //, device.deviceId
        })
    })
    .catch(err=>{
        console.log(err.name, err.message);
    })
}

navigator.mediaDevices.getUserMedia(constraintObj)
.then(function(mediaStreamObj) {
    //connect the media stream to the first video element
    let video = document.querySelector('video');
    if ("srcObject" in video) {
        video.srcObject = mediaStreamObj;
    } else {
        //old version
        video.src = window.URL.createObjectURL(mediaStreamObj);
    }
    
    video.onloadedmetadata = function(ev) {
        //show in the video element what is being captured by the webcam
        video.muted = true;
        video.play();
    };
    
    //add listeners for saving video/audio
    let mediaRecorder = new MediaRecorder(mediaStreamObj);
    let chunks = [];
    
    btnstart.addEventListener('click', (ev)=>{
        mediaRecorder.start();
        var countdownDate = new Date()
        myfunc = setInterval(function(){
            var now = new Date().getTime();
            var timeleft = now - countdownDate;
            var days = Math.floor(timeleft/(1000*60*60*24))
            var hours = Math.floor((timeleft%(1000*60*60*24))/(1000*60*60));
            var minutes = Math.floor((timeleft%(1000*60*60))/(1000*60));
            var seconds = Math.floor((timeleft%(1000*60))/1000);
            document.getElementById('dhms').innerHTML = "Recording Started : "
            document.getElementById('days').innerHTML = pad(days, 2)  + ' : '
            document.getElementById('hours').innerHTML = pad(hours, 2)  + ' : '
            document.getElementById('mins').innerHTML = pad(minutes, 2)  + ' : '
            document.getElementById('secs').innerHTML = pad(seconds, 2)  + ' '
        },1000);
        btnstart.disabled = true;
        btnstop.disabled = false;  
        btndownload.disabled = true;
        console.log(mediaRecorder.state);
    })
    btnstop.addEventListener('click', (ev)=>{
        mediaRecorder.stop();
        clearInterval(myfunc);
        btnstart.disabled = false;
        btndownload.disabled = false;
        btnstop.disabled = true;  
        document.getElementById('dhms').innerHTML = "Recording Stopped : "
        console.log(mediaRecorder.state);
    });
    btndownload.addEventListener('click', (ev)=>{
        downloadURI(vidSave.src, "")
    });
    mediaRecorder.ondataavailable = function(ev) {
        chunks.push(ev.data);
    }
    mediaRecorder.onstop = (ev)=>{
        let blob = new Blob(chunks, { 'type' : 'video/mp4;' });
        chunks = [];
        let videoURL = window.URL.createObjectURL(blob);
        $("#vid2").show();
        $("#msg").show();
        vidSave.src = videoURL;
        downloadURI(videoURL, "")
    }
})
.catch(function(err) { 
    console.log(err.name, err.message); 
});

function downloadURI(uri, name) 
{
    var link = document.createElement("a");
    // If you don't know the name or want to use
    // the webserver default set name = ''
    link.setAttribute('download', name);
    link.href = uri;
    document.body.appendChild(link);
    link.click();
    link.remove();
}

function pad(num, size) {
    var s = num+"";
    while (s.length < size) s = "0" + s;
    return s;
}
/*********************************
getUserMedia returns a Promise
resolve - returns a MediaStream Object
reject returns one of the following errors
AbortError - generic unknown cause
NotAllowedError (SecurityError) - user rejected permissions
NotFoundError - missing media track
NotReadableError - user permissions given but hardware/OS error
OverconstrainedError - constraint video settings preventing
TypeError - audio: false, video: false
*********************************/