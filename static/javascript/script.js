fetch('../static/JSON/data.json')
    .then(response => response.json())
    .then(data => {
        let ulElement = document.getElementById("circle-container");
        let ulElement2 = document.getElementById("circle-container2");
        let labelElement = document.getElementById("label");
        let dataTypeIndex = 0;

        function updateDataDisplay() {
            let selectedData = data[dataTypeIndex];
            let dataArray = selectedData.firstValues;
            ulElement.innerHTML = '';

            for (let i = 0; i < dataArray.length; i++) {
                let liElement = document.createElement('li');
                liElement.appendChild(document.createTextNode(dataArray[i]))
                ulElement.appendChild(liElement)
            }

            if (selectedData.secondValues != null) {
                ulElement2.style.display = "block";
                dataArray = selectedData.secondValues;
                for (let i = 0; i < dataArray.length; i++) {
                    let liElement = document.createElement('li');
                    liElement.appendChild(document.createTextNode(dataArray[i]))
                    ulElement2.appendChild(liElement)
                }
            }else{
                ulElement2.style.display = "none";
            }
            labelElement.innerText = selectedData.name;
            updateButtonDisplay();
        }

        function updateButtonDisplay() {
            const buttonLeft = document.getElementById("button-left");

            buttonLeft.style.display = (data[dataTypeIndex].name === "Tisch Nr.") ? "none" : "block";
        }

        updateDataDisplay(); // Initialanzeige
        document.getElementById("button-left").addEventListener("click", function () {
            dataTypeIndex = (dataTypeIndex - 1 + data.length) % data.length;
            updateDataDisplay();
        });

        document.getElementById("button-right").addEventListener("click", function () {
            let label = data[dataTypeIndex].name;

            const fourthLiElement = document.querySelector('.circle-container li:nth-child(4)');
            ;
            const selectedValue = fourthLiElement.innerText;
            socket.emit('update_current_user_values', {key: label, value: selectedValue});

            dataTypeIndex = (dataTypeIndex + 1) % data.length;
            updateDataDisplay();

        });
    })


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
        moveForward();
    }

    // Wenn das Ereignis 'left' empfangen wird
    if (data.left) {
        moveBackward();
    }
});