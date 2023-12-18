let isSecondCircle = false;

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function () {
    console.log('Connected to server');
});

fetch('../static/JSON/data.json')
    .then(response => response.json())
    .then(data => {
        let ulElement = document.getElementById("circle-container");
        let ulElement2 = document.getElementById("circle-container2");
        let labelElement = document.getElementById("label");
        let dataTypeIndex = 0;
        let hour = "";
        let minutes = "";

        function handleButtonClick(direction) {
            // Der Knob wurde nach vorne gedreht
            if (direction === 'right') {
                if (isSecondCircle && labelElement.innerText == "Uhrzeit") {
                    moveSecondCircleForward()
                } else {
                    moveForward()
                }
                // Der Knob wurde nach hinten gedreht
            } else if (direction === 'left') {
                if (isSecondCircle && labelElement.innerText == "Uhrzeit") {
                    moveSecondCircleBackward()
                } else {
                    moveBackward()
                }
                // Der "Weiter" Button wurde gedrückt
            } else if (direction === 'ok') {
                let selectedValue = "";
                // Wenn der Nutzer sich bei der Eingabe der Stunde bei der Uhrzeitansicht befindet
                if (labelElement.innerText == "Uhrzeit" && !isSecondCircle) {
                    const fourthLiElementInFirstCircle = document.querySelector('.circle-container li:nth-child(4)');
                    hour = fourthLiElementInFirstCircle.innerText
                    // Wenn der Nutzer sich bei der Eingabe der Minuten bei der Uhrzeitansicht befindet
                } else if (labelElement.innerText == "Uhrzeit" && isSecondCircle) {
                    const fourthLiElementInSecondCircle = document.querySelector('#circle-container2 li:nth-child(4)');
                    minutes = fourthLiElementInSecondCircle.innerText;
                    selectedValue = hour + ":" + minutes;
                    dataTypeIndex = (dataTypeIndex + 1) % data.length;
                    // Wenn der Nutzer sich bei jeder anderen Ansicht befindet
                } else {
                    const fourthLiElement = document.querySelector('.circle-container li:nth-child(4)');
                    selectedValue = fourthLiElement.innerText;
                    dataTypeIndex = (dataTypeIndex + 1) % data.length;
                }

                // Sendet die Nutzerdaten an das Backend
                // Die Eingabe der Uhrzeit soll erst nach Angabe der Minuten an das Backend gesendet werden
                if (labelElement.innerText != "Uhrzeit" || (labelElement.innerText == "Uhrzeit" && isSecondCircle)) {
                    socket.emit('update_current_user_values', {key: labelElement.innerText, value: selectedValue});
                    // Wenn der "Weiter" Button bei der Dauer-Ansicht geklickt wurde, dann soll die Ansicht zur Bestätigung der Reservierung geöffnet werden
                    if (labelElement.innerText == "Dauer") {
                        location.href = "/reservation_completed";
                    } else {
                        document.getElementById("button-right").removeAttribute("href");
                    }
                }

                if (labelElement.innerText == "Uhrzeit") {
                    isSecondCircle = !isSecondCircle;
                }
                updateDataDisplay();
                // "Zurück" Button wird geklickt
            } else {
                if (labelElement.innerText == "Tisch Nr."){
                    location.href = "/";
                }    
                // Wenn der Nutzer sich bei der Ansicht der "Dauer" befindet, dann soll beim "Zurück" klicken die Uhrzeit-Ansicht geöffnet werden und der Nutzer
                // kann die Minuten der Uhrzeit bearbeiten
                if (labelElement.innerText == "Dauer") {
                    dataTypeIndex = (dataTypeIndex - 1 + data.length) % data.length;
                    isSecondCircle = true;
                // Wenn der Nutzer sich bei der Ansicht der "Uhrzeit-Minuten" befindet, dann sollen beim "Zurück" klicken die Stunden gehighlighted werden und der Nutzer
                // kann die Stunden der Uhrzeit bearbeiten.
                } else if (labelElement.innerText == "Uhrzeit" && isSecondCircle) {
                    isSecondCircle = false;
                // Wenn der Nutzer sich bei jeder anderen Ansicht befindet
                } else {
                    dataTypeIndex = (dataTypeIndex - 1 + data.length) % data.length;
                }
                updateDataDisplay();
            }
        }


        document.getElementById("button-turn-backward").addEventListener("click", function () {
            socket.emit('button', 'right');
        });

        document.getElementById("button-turn-forward").addEventListener("click", function () {
            socket.emit('button', 'left');
        });

        document.getElementById("button-left").addEventListener("click", function () {
            document.getElementById("button-right").removeAttribute("href");
            socket.emit('button', 'back');
        });

        document.getElementById("button-right").addEventListener("click", function () {
            socket.emit('button', 'ok');
        });

        function moveBackward() {
            let lastElement = document.querySelector('#circle-container li:last-child');
            let container = document.querySelector('.circle-container');
            container.prepend(lastElement);
        }

        function moveForward() {
            let firstElement = document.querySelector('#circle-container li');
            let container = document.querySelector('.circle-container');
            container.appendChild(firstElement);
        }

        function moveSecondCircleForward() {
            let firstElement = document.querySelector('#circle-container2 li');
            let container = document.querySelector('#circle-container');
            container.appendChild(firstElement);
        }

        function moveSecondCircleBackward() {
            let lastElement = document.querySelector('#circle-container2 li:last-child');
            let container = document.querySelector('#circle-container2');
            container.prepend(lastElement);
        }

        socket.on('new_value', function (data) {
            if (data.ok) {
                handleButtonClick('ok')
            }

            // Wenn das Ereignis 'back' empfangen wird
            if (data.back) {
                handleButtonClick('back')
            }

            // Wenn das Ereignis 'right' empfangen wird
            if (data.right) {
                handleButtonClick('right');
            }

            // Wenn das Ereignis 'left' empfangen wird
            if (data.left) {
                handleButtonClick('left');
            }
        });

        function updateDataDisplay() {
            let selectedData = data[dataTypeIndex];
            labelElement.innerText = selectedData["name"]
            updateButtonDisplay();
            setBackground();
            let firstValues = selectedData.firstValues;
            let secondValues = selectedData.secondValues;
            ulElement.innerHTML = '';

            for (let i = 0; i < firstValues.length; i++) {
                let liElement = document.createElement('li');
                liElement.appendChild(document.createTextNode(firstValues[i]))
                ulElement.appendChild(liElement)
            }
            if (labelElement.innerText == "Uhrzeit") {
                for (let i = 0; i < secondValues.length; i++) {
                    let liElement = document.createElement('li');
                    liElement.appendChild(document.createTextNode(secondValues[i]))
                    ulElement2.appendChild(liElement)
                }
            }
        }

        function updateButtonDisplay() {
            const buttonLeft = document.getElementById("button-left");
            buttonLeft.style.display = (labelElement.innerText != "Tisch Nr.") ? "block" : "none";
        }

        function setBackground() {
            if (labelElement.innerText != "Uhrzeit") {
                ulElement.style.backgroundColor = 'rgba(236,167,118,255)';
                ulElement2.style.display = "none";
            } else if (labelElement.innerText == "Uhrzeit" && !isSecondCircle) {
                ulElement2.style.display = "block";
                ulElement.style.backgroundColor = 'rgba(236,167,118,255)';
                ulElement2.style.backgroundColor = 'rgb(217,217,217)';
            } else if (labelElement.innerText == "Uhrzeit" && isSecondCircle) {
                ulElement2.style.display = "block";
                ulElement.style.backgroundColor = 'rgb(217,217,217)';
                ulElement2.style.backgroundColor = 'rgba(236,167,118,255)';
            }
        }

        setBackground();
        updateDataDisplay(); // Initialanzeige
    })

