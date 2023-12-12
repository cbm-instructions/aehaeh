let isSecondCircle = false;

fetch('../static/JSON/data.json')
    .then(response => response.json())
    .then(data => {
        let ulElement = document.getElementById("circle-container");
        let ulElement2 = document.getElementById("circle-container2");
        let labelElement = document.getElementById("label");
        let dataTypeIndex = 0;
        let hour = "";
        let minutes = "";


        function updateDataDisplay() {
            setBackground();
            if (!isSecondCircle) {
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

                if (secondValues.length != 0) {
                    ulElement2.style.display = "block";
                    for (let i = 0; i < secondValues.length; i++) {
                        let liElement = document.createElement('li');
                        liElement.appendChild(document.createTextNode(secondValues[i]))
                        ulElement2.appendChild(liElement)
                    }
                } else {
                    ulElement2.style.display = "none";
                }
            }
        }

        function updateButtonDisplay() {
            const buttonLeft = document.getElementById("button-left");
            buttonLeft.style.display = (labelElement.innerText != "Tisch Nr.") ? "block" : "none";
        }


        function setBackground() {
            if (labelElement.innerText != "Uhrzeit"){
                ulElement.style.backgroundColor = 'rgba(236,167,118,255)';
                ulElement2.style.display = "none";
            }
            else if (labelElement.innerText == "Uhrzeit" && !isSecondCircle) {
                ulElement2.style.display = "block";
                ulElement.style.backgroundColor = 'rgba(236,167,118,255)';
                ulElement2.style.backgroundColor = 'rgb(217,217,217)';
            } else if(labelElement.innerText == "Uhrzeit" && isSecondCircle) {
                ulElement2.style.display = "block";
                ulElement.style.backgroundColor = 'rgb(217,217,217)';
                ulElement2.style.backgroundColor = 'rgba(236,167,118,255)';
            }
        }

        updateDataDisplay(); // Initialanzeige
        document.getElementById("button-left").addEventListener("click", function () {
            if (labelElement.innerText == "Uhrzeit" && !isSecondCircle) {
                dataTypeIndex = (dataTypeIndex - 1 + data.length) % data.length;
                isSecondCircle = !isSecondCircle;
            } else if (labelElement.innerText == "Uhrzeit" && isSecondCircle) {
                isSecondCircle = !isSecondCircle;
            } else {
                dataTypeIndex = (dataTypeIndex - 1 + data.length) % data.length;
            }
            updateDataDisplay();
        });

        document.getElementById("button-right").addEventListener("click", function () {
            let label = data[dataTypeIndex].name;
            let selectedValue = "";

            if (label == "Uhrzeit" && !isSecondCircle) {
                const fourthLiElementInFirstCircle = document.querySelector('.circle-container li:nth-child(4)');
                hour = fourthLiElementInFirstCircle.innerText
            } else if (label == "Uhrzeit" && isSecondCircle) {
                const fourthLiElementInSecondCircle = document.querySelector('#circle-container2 li:nth-child(4)');
                minutes = fourthLiElementInSecondCircle.innerText;
                selectedValue = hour + ":" + minutes;
                dataTypeIndex = (dataTypeIndex + 1) % data.length;
            } else {
                const fourthLiElement = document.querySelector('.circle-container li:nth-child(4)');
                selectedValue = fourthLiElement.innerText;
                dataTypeIndex = (dataTypeIndex + 1) % data.length;
            }
            if (label != "Uhrzeit" || isSecondCircle){
                socket.emit('update_current_user_values', {key: label, value: selectedValue});
            }

            if (label == "Uhrzeit") {
                isSecondCircle = !isSecondCircle;
            }

            updateDataDisplay();
        });
    })


function handleButtonClick(direction) {
    let labelElement = document.getElementById("label");

    if (direction === 'forward') {
        if (isSecondCircle && labelElement.innerText == "Uhrzeit") {
            moveSecondCircleForward()
        } else {
            moveForward()
        }
    } else {
        if (isSecondCircle && labelElement.innerText == "Uhrzeit") {
            moveSecondCircleBackward()
        } else {
            moveBackward()
        }
    }
}

function moveBackward() {
    const firstElement = document.querySelector('.circle-container li');
    //const lastElement = document.querySelector('.circle-container li:last-child');
    //firstElement.style.transform = `rotate(${parseInt(firstElement.style.transform.split('(')[1]) + 45}deg) translate(10em) rotate(-${parseInt(firstElement.style.transform.split('(')[1]) + 45}deg)`;
    document.querySelector('.circle-container').appendChild(firstElement);
}

function moveForward() {
    //const firstElement = document.querySelector('.circle-container li');
    const lastElement = document.querySelector('.circle-container li:last-child');
    //lastElement.style.transform = `rotate(${parseInt(lastElement.style.transform.split('(')[1]) - 45}deg) translate(10em) rotate(-${parseInt(lastElement.style.transform.split('(')[1]) - 45}deg)`;
    document.querySelector('.circle-container').prepend(lastElement);
}


function moveSecondCircleForward() {
    const firstElement = document.querySelector('#circle-container2 li');
    document.querySelector('#circle-container').appendChild(firstElement);
}

function moveSecondCircleBackward() {
    const lastElement = document.querySelector('#circle-container2 li:last-child');
    document.querySelector('#circle-container2').prepend(lastElement);
}

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function () {
    console.log('Connected to server');
});

socket.on('new_value', function (data) {
    if (data.ok) {
        alert("weiter");
    }

    // Wenn das Ereignis 'back' empfangen wird
    if (data.back) {
        alert("zurück");
    }

    // Wenn das Ereignis 'right' empfangen wird
    if (data.right) {
        handleButtonClick('forward');
    }

    // Wenn das Ereignis 'left' empfangen wird
    if (data.left) {
        handleButtonClick('backward');
    }
});