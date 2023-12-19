document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port)

    socket.on('connect', function () {
        console.log('Connected to server');
        socket.emit('read_rfid', 'read');
    });

    function handleButtonClick(direction) {
        if (direction === 'ok') {
            window.location.href = "/reservation_page";
        }
    }

    document.getElementById("button-go-to-reservation").addEventListener("click", function () {
        socket.emit('button', 'ok');
    });

    socket.on('new_value', function (data) {
        if (data['ok']) {
            handleButtonClick('ok')
        }
    });
    
    socket.on('rfid_id', function (data) {
        if (data['id']){
            handleButtonClick('ok')
        }
    });    
    
})

