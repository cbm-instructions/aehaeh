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
            if (direction === 'finish') {

            } else if (direction === 'back') {

            }
        }

        document.getElementById("button-back-to-reservation").addEventListener("click", function () {
            socket.emit('button', 'back-to-reservation');
        });

        document.getElementById("button-finish-reservation").addEventListener("click", function () {
            socket.emit('button', 'finish');
        });


        socket.on('new_value', function (data) {
            if (data.finish) {
                handleButtonClick('ok')
            }

            // Wenn das Ereignis 'back' empfangen wird
            if (data.back) {
                handleButtonClick('back')
            }

            // Wenn das Ereignis 'right' empfangen wird
            if (data.forward) {
                console.log("right")
                handleButtonClick('forward');
            }

            // Wenn das Ereignis 'left' empfangen wird
            if (data.backward) {
                console.log("left")
                handleButtonClick('backward');
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

