document.addEventListener('DOMContentLoaded', function () {
    let socket = io.connect('http://' + document.domain + ':' + location.port)

    let id = document.getElementById("ID");
    let tischnummer = document.getElementById("Tischnummer");
    let datum = document.getElementById("Datum");
    let uhrzeit = document.getElementById("Uhrzeit");
    let dauer = document.getElementById("Dauer");

    console.log(id.innerText + " " + tischnummer.innerText + " " + datum.innerText + " " + uhrzeit.innerText + " " + dauer.innerText);

    socket.on('connect', function () {
        console.log('Connected to server');
    });

    function handleButtonClick(direction) {
        if (direction === 'finish') {
            socket.emit('update_current_user_values', 'finish')
        } else if (direction === 'back_to_reservation') {
            socket.emit('update_current_user_values', 'back-to-reservation')
        }
    }

    document.getElementById("button-back-to-reservation").addEventListener("click", function () {
        socket.emit('button', 'back-to-reservation');
    });

    document.getElementById("button-finish-reservation").addEventListener("click", function () {
        socket.emit('button', 'finish');
    });

    socket.on('new_value', function (data) {
        if (data['finish']) {
            handleButtonClick('finish')
        }
        if (data['back_to_reservation']) {
            handleButtonClick('back_to_reservation')
        }
    });

    socket.on('reservation_user_values', function (data) {
        id = data["ID"]
        tischnummer = data["Tisch Nr."];
        datum = data["Datum"];
        uhrzeit = data["Uhrzeit"];
        dauer = data["Dauer"];
    })
})

