document.addEventListener('DOMContentLoaded', function () {
    let socket = io.connect('http://' + document.domain + ':' + location.port)

    socket.on('connect', function () {
        console.log('Connected to server');
        socket.emit("request_current_user_values", {'request': 'true'})
    });

    function handleButtonClick(direction) {
        if (direction === 'ok') {
            socket.emit('finish_reservation', 'finish')
        }
        window.location.href = "/";
    }

    document.getElementById("button-back-to-reservation").addEventListener("click", function () {
        socket.emit('button', 'back');
    });

    document.getElementById("button-finish-reservation").addEventListener("click", function () {
        socket.emit('button', 'ok');
    });

    socket.on('new_value', function (data) {
        if (data['ok']) {
            handleButtonClick('ok')
        }
        if (data['back']) {
            handleButtonClick('back')
        }
    });

    socket.on('display_current_user_values', function (data) {
        document.getElementById("ID").innerText = data["ID"];
        document.getElementById("Tischnummer").innerText = data["Tisch Nr."];
        document.getElementById("Datum").innerText = data["Datum"];
        document.getElementById("Uhrzeit").innerText = data["Uhrzeit"];
        document.getElementById("Dauer").innerText = data["Dauer"];
    });
})

