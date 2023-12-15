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
            let labelElement = document.getElementById("label");

            if (direction === 'forward') {
                if (isSecondCircle && labelElement.innerText == "Uhrzeit") {
                    moveSecondCircleForward()
                } else {
                    moveForward()
                }
            } else if (direction === 'backward') {
                if (isSecondCircle && labelElement.innerText == "Uhrzeit") {
                    moveSecondCircleBackward()
                } else {
                    moveBackward()
                }
            } else if (direction === 'ok') {
                let label = data[dataTypeIndex].name;
                let selectedValue = "";

                // Eingabe der Stunden bei der Uhrzeit
                if (label == "Uhrzeit" && !isSecondCircle) {
                    const fourthLiElementInFirstCircle = document.querySelector('.circle-container li:nth-child(4)');
                    hour = fourthLiElementInFirstCircle.innerText
                    // Eingabe der Minuten bei der Uhrzeit
                } else if (label == "Uhrzeit" && isSecondCircle) {
                    const fourthLiElementInSecondCircle = document.querySelector('#circle-container2 li:nth-child(4)');
                    minutes = fourthLiElementInSecondCircle.innerText;
                    selectedValue = hour + ":" + minutes;
                    dataTypeIndex = (dataTypeIndex + 1) % data.length;
                    // Jede andere Eingabe
                } else {
                    const fourthLiElement = document.querySelector('.circle-container li:nth-child(4)');
                    selectedValue = fourthLiElement.innerText;
                    dataTypeIndex = (dataTypeIndex + 1) % data.length;
                }
                if (label != "Uhrzeit" || (label == "Uhrzeit" && isSecondCircle)) {
                    socket.emit('update_current_user_values', {key: label, value: selectedValue});
                }

                if (label == "Uhrzeit") {
                    isSecondCircle = !isSecondCircle;
                }

                updateDataDisplay();
            } else {
                // Zurück - Button wird geklickt, wenn der Nutzer die Stunden bei der Uhrzeit eingibt
                if (labelElement.innerText != "Tisch Nr.") {
                    if (labelElement.innerText == "Dauer") {
                        dataTypeIndex = (dataTypeIndex - 1 + data.length) % data.length;
                        isSecondCircle = true;
                        //alert(data[dataTypeIndex].name);
                        // Zurück- Button wird geklickt, wenn der Nutzer die Minuten bei der Uhrzeit eingibt
                    } else if (labelElement.innerText == "Uhrzeit" && isSecondCircle) {
                        isSecondCircle = false;
                        // Zurück- Button wird geklickt, wenn der Nutzer sich nicht bei der Uhrzeit befindet
                    } else {
                        dataTypeIndex = (dataTypeIndex - 1 + data.length) % data.length;
                    }
                    updateDataDisplay();
                }
            }
        }

        document.getElementById("button-turn-backward").addEventListener("click", function () {
            //handleButtonClick('backward');
            socket.emit('button', 'back');
        });

        document.getElementById("button-turn-forward").addEventListener("click", function () {
            //handleButtonClick('forward');
            socket.emit('button', 'forward');
        });

        document.getElementById("button-left").addEventListener("click", function () {
            handleButtonClick('back');
            updateDataDisplay();
        });

        document.getElementById("button-right").addEventListener("click", function () {
            handleButtonClick('ok');
            updateDataDisplay();
        });

        function moveBackward() {
            let lastElement = document.querySelector('#circle-container li:last-child');
            console.log(lastElement.innerText)
            let container = document.querySelector('.circle-container');
            container.prepend(lastElement);
            lastElement = container.querySelector('li:last-child');
            console.log(lastElement.innerText)
        }

        function moveForward() {
            let firstElement = document.querySelector('#circle-container li');
            console.log(firstElement.innerText)
            let container = document.querySelector('.circle-container');
            container.appendChild(firstElement);
            firstElement = container.querySelector('li');
            console.log(firstElement.innerText)
        }

        function moveSecondCircleForward() {
            let firstElement = document.querySelector('#circle-container2 li');
            console.log(firstElement.innerText)
            let container = document.querySelector('#circle-container');
            container.appendChild(firstElement);
            firstElement = container.querySelector('#circle-container2 li');
            console.log(firstElement.innerText)
        }

        function moveSecondCircleBackward() {
            let lastElement = document.querySelector('#circle-container2 li:last-child');
            console.log(lastElement.innerText)
            let container = document.querySelector('#circle-container2');
            container.prepend(lastElement);
            lastElement = container.querySelector('li:last-child');
            console.log(lastElement.innerText)
        }

        socket.on('new_value', function (data) {
            if (data.ok) {
                handleButtonClick('ok')
                updateDataDisplay();
            }

            // Wenn das Ereignis 'back' empfangen wird
            if (data.back) {
                handleButtonClick('back')
                updateDataDisplay();
            }

            // Wenn das Ereignis 'right' empfangen wird
            if (data.right) {
                handleButtonClick('forward');
                updateDataDisplay();
            }

            // Wenn das Ereignis 'left' empfangen wird
            if (data.left) {
                handleButtonClick('backward');
                updateDataDisplay();
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

            if (labelElement.innerText != "Uhrzeit") {
                for (let i = 0; i < firstValues.length; i++) {
                    let liElement = document.createElement('li');
                    liElement.appendChild(document.createTextNode(firstValues[i]))
                    ulElement.appendChild(liElement)
                }
            } else {
                for (let i = 0; i < firstValues.length; i++) {
                    let liElement = document.createElement('li');
                    liElement.appendChild(document.createTextNode(firstValues[i]))
                    ulElement.appendChild(liElement)
                }

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

