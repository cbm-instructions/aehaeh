document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port)

    socket.on('connect', function () {
        console.log('Connected to server');
        socket.emit('read_rfid', 'read');
        socket.emit('request_database_values', 'receive');
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

    socket.on('data_base_entries', function (data){
       if(data["value"]){
           const dataBaseEntries = data["value"];
           console.log(dataBaseEntries);
          for(let reservation in dataBaseEntries){
              let reservation_table = reservation[1];
              let reservation_day = Date.parse(reservation[2]);
              let reservation_hour = reservation[3];
              let reservation_duration = reservation[4];

          }
       }
    });

})

