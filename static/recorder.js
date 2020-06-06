var buttonRecord = document.getElementById("start_rec");
var buttonStop = document.getElementById("stop_rec");

buttonStop.disabled = true;
var myfunc; 
buttonRecord.onclick = function() {
    $('#container-recorder').loader('show','<i class="fa fa-2x fa-spinner fa-pulse"></i>');
    buttonRecord.disabled = true;
    buttonStop.disabled = false;
    
    // disable download link
    var downloadLink = document.getElementById("download");
    downloadLink.text = "";
    downloadLink.href = "";

    // XMLHttpRequest
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        console.log(xhr);
        $('#container-recorder').loader('hide');
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log(xhr);

            var countdownDate = new Date()
            myfunc = setInterval(function(){
                var now = new Date().getTime();
                var timeleft = now - countdownDate;
                var days = Math.floor(timeleft/(1000*60*60*24))
                var hours = Math.floor((timeleft%(1000*60*60*24))/(1000*60*60));
                var minutes = Math.floor((timeleft%(1000*60*60))/(1000*60));
                var seconds = Math.floor((timeleft%(1000*60))/1000);
                document.getElementById('days').innerHTML = days + 'd '
                document.getElementById('hours').innerHTML = hours + 'h '
                document.getElementById('mins').innerHTML = minutes + 'm '
                document.getElementById('secs').innerHTML = seconds + 's '
            },1000);

        }
    }
    xhr.open("POST", "/record_status");
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ status: "true" }));
};

buttonStop.onclick = function() {
    clearInterval(myfunc)
    buttonRecord.disabled = false;
    buttonStop.disabled = true;  
    var downloadLink = document.getElementById("download");
    downloadLink.text = "Wait preparing video and Please donot refersh this page......";
    downloadLink.href = "#";  
    $('#container-recorder').loader('show','<i class="fa fa-2x fa-spinner fa-pulse"></i>');
    // XMLHttpRequest
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        $('#container-recorder').loader('hide');
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log(xhr.responseText);
            var data = JSON.parse(xhr.responseText);
            // enable download link
            console.log(data.msg)
            downloadLink = document.getElementById("download");
            downloadLink.text = "Download Video";
            downloadLink.href = data.msg +"/main_video.avi?v="+new Date()/1000;


        }
    }
    xhr.open("POST", "/record_status");
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ status: "false" }));
};

