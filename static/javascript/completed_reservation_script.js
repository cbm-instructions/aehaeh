let isSecondCircle = false;

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function () {
    console.log('Connected to server');
});

fetch('../static/JSON/data.json')
    .then(response => response.json())
    .then(data => {
        function handleButtonClick(direction) {
            if (direction === 'finish') {
                //TODO
            } else if (direction === 'back_to_reservation') {
                //TODO
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






    })

