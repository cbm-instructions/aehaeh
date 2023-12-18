document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port)

    socket.on('connect', function () {
        console.log('Connected to server');
    });

    function handleButtonClick(direction) {
        if (direction === 'ok') {
            window.location.href = "/reservation_page";
        }
    }

    document.getElementById("button-go-to-reservation").addEventListener("click", function () {
        console.log("beeb")
        socket.emit('button', 'ok');
    });

    socket.on('new_value', function (data) {
        if (data['ok']) {
            handleButtonClick('ok')
        }
    });
})

