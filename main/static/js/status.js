socket.addEventListener('open', function(event) {
    // Now it's safe to send a message
    updateStatus(docStatus);
});


function calculateTimeLeft(endsAt) {
    const now = new Date();
    const endTime = new Date(endsAt);
    const difference = endTime - now;

    if (difference <= 0) {
        return null;  // Past the end time
    }

    const hours = Math.floor((difference / (1000 * 60 * 60)) % 24);
    const minutes = Math.floor((difference / 1000 / 60) % 60);
    const seconds = Math.floor((difference / 1000) % 60);

    return `${hours}h ${minutes}m ${seconds}s`;
}

function updateTimer() {
    const timerElement = document.getElementById(`timer-${docAssignmentId}`);
    const endsAt = timerElement.getAttribute('data-ends-at');

    const timeLeft = calculateTimeLeft(endsAt);
    if (timeLeft) {
        timerElement.innerHTML = `<small class="text-muted">Time left: ${timeLeft}</small>`;
    } else {
        timerElement.innerHTML = `<small class="text-muted">Ended at: ${endsAt}</small>`;
    }
}


socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(data);
    console.log(data.status);

    if (data.message_type === 'update_status' && data.document_id === docId) {
        docStatus = data.status;

        if (data.status === 'locked') {
            console.log("carrying out locked")
            $('#OCRModal').modal('hide');
            //$('#latexModal').modal('hide');
            $('#ResultsModal').modal('hide');
            $('#Test1Modal').modal('hide'); 
            $('#Test2Modal').modal('hide'); 
            $('#submittedModal').modal('hide');
            if (document.fullscreenElement) {
                exitFullscreen();
            }        
            $('#lockScreenModal').modal('show');

            removeEventListeners();
        } else if (data.status === 'pending') {
            console.log("carrying out pending")
            $('#OCRModal').modal('hide');
            //$('#latexModal').modal('hide');
            $('#ResultsModal').modal('hide');
            $('#lockScreenModal').modal('hide'); 
            $('#submittedModal').modal('hide');
            if (document.fullscreenElement) {
                exitFullscreen();
            }
            
            var modal;
            if (assignmentStrict === 'False') {
                modal = document.getElementById('Test1Modal');
            } else if (assignmentStrict === 'True') {
                modal = document.getElementById('Test2Modal');
            }
            if (modal) {
                $(modal).modal('show');
            }
            removeEventListeners();

        } else if (data.status === 'submitted') {
            $('#OCRModal').modal('hide');
            $('#latexModal').modal('hide');
            $('#ResultsModal').modal('hide');
            $('#Test1Modal').modal('hide'); 
            $('#Test2Modal').modal('hide'); 
            $('#lockScreenModal').modal('hide');
            if (document.fullscreenElement) {
                exitFullscreen();
            }     
            $('#submittedModal').modal('show');
            removeEventListeners();

        } else if (data.status === 'started') {
            if (assignmentStrict === "True") {

                window.addEventListener('blur', handleBlur);
                document.addEventListener('copy', handleCopy);
                document.addEventListener('paste', handlePaste);
            }
        }
    }
};

function removeEventListeners() {
    window.removeEventListener('blur', handleBlur);
    document.removeEventListener('copy', handleCopy);
    document.removeEventListener('paste', handlePaste);
}

function handleBlur() {
    $('#OCRModal').modal('hide');
    //$('#latexModal').modal('hide');
    $('#ResultsModal').modal('hide');
    if (document.fullscreenElement) {
        exitFullscreen();
    }
    $('#lockScreenModal').modal('show');
    updateStatus("locked");
    console.log('Tab/window has lost focus');
}

function handleCopy(e) {
    console.log('Copy operation detected');
    e.preventDefault();
}

function handlePaste(e) {
    console.log('Paste operation detected');
    e.preventDefault();
}

function updateStatus(status) {

    var message = {
        message_type: 'update_status',
        document_id: docId,
        status: status,
        assignment_id: docAssignmentId,
    }
    docStatus = status;
    socket.send(JSON.stringify(message));
};

if (assignmentStatus === 1) {
    setInterval(updateTimer, 1000);
}

document.getElementById('StartTest2Btn').addEventListener('click', function() {
    $('#Test2Modal').modal('hide');
    updateStatus("started");


    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    }
});

function submitDoc() {
    console.log('Submit button clicked');

    
    $('#OCRModal').modal('hide');
    $('#latexModal').modal('hide');
    $('#ResultsModal').modal('hide');
    $('#Test1Modal').modal('hide'); 
    $('#Test2Modal').modal('hide'); 
    $('#lockScreenModal').modal('hide');

    if (document.fullscreenElement) {
        exitFullscreen();
    }        
    
    $('#submittedModal').modal('show');
    updateStatus("submitted")
    
}



// Select all elements with the class 'submit-btn'
const submitButtons = document.querySelectorAll('.submit-btn');

// Attach the event listener to each button
submitButtons.forEach(button => {
    button.addEventListener('click', submitDoc);
});

function exitFullscreen() {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.webkitExitFullscreen) { /* Safari */
        document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) { /* IE11 */
        document.msExitFullscreen();
    }
}



document.addEventListener('fullscreenchange', (event) => {
    const elementsToHide = document.querySelectorAll('.hide-in-fullscreen');

    if (document.fullscreenElement) {
        elementsToHide.forEach(element => {
            element.style.display = 'none';
        });
    } else {
        elementsToHide.forEach(element => {
            element.style.display = '';
        });

        if (docStatus === "started") {
            $('#OCRModal').modal('hide');
            //$('#latexModal').modal('hide');
            $('#ResultsModal').modal('hide');
            $('#lockScreenModal').modal('show');
            updateStatus("locked");
            console.log('Exited fullscreen mode');
        }
    }
});

document.getElementById('StartTest1Btn').addEventListener('click', function() {
    $('#Test1Modal').modal('hide');
    updateStatus("started");
});

window.addEventListener('load', function() {

    if (docStatus === "locked") {
        
        $('#lockScreenModal').modal('show');
    } else if (docStatus === "pending") {
        var modal;
        if (assignmentStrict === "False") {
            modal = document.getElementById("Test1Modal");
        } else if (assignmentStrict === "True") {
            modal = document.getElementById("Test2Modal");
        }
        if (modal) {
            $(modal).modal('show');
        }
    } else if (docStatus === "submitted"){
        $('#submittedModal').modal('show');
    }
});
