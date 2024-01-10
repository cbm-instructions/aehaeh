document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port)

    var dataBaseEntries;


    socket.on('connect', function () {
        console.log('Connected to server');
        socket.emit('read_rfid', 'read');
        socket.emit('request_database_values', 'receive');
    });

    updateTime();
    setInterval(updateTime, 1000);
    var tableview = 1;
    function handleButtonClick(direction) {
        if (direction === 'ok') {
            window.location.href = "/reservation_page";
        }
        else if(direction === 'left'){
            if(tableview >= 1 && tableview < 8){
                tableview+=1;
                resetTableColors();
                displayReservationForTable();
                displayHighlightedTable();
            }

        }
        else if(direction === 'right'){
            if(tableview > 1 && tableview <=8){
                tableview-=1;
                resetTableColors();
                displayReservationForTable();
                displayHighlightedTable();
            }
        }

    }
    function resetTableColors(){
        var table = document.getElementById("myTable");
        for (var i = 0; i < table.rows.length; i++) {
        // Iterate through all cells in each row
            for (var j = 0; j < table.rows[i].cells.length; j++) {
            // Set the background color of each cell to white
            table.rows[i].cells[j].style.backgroundColor = "white";
            }
        }
    }


    function displayHighlightedTable(){
        var cell = document.getElementById("tischnr_cell");
        var tischnr = cell.children;
        for(var i = 0; i < tischnr.length; i++){
            if(i == tableview-1){
                tischnr[i].style.backgroundColor= "rgba(236, 167, 118, 1)";
            }
            else {
                tischnr[i].style.backgroundColor= "white";
            }
        }
    }

    function updateTime() {
    var currentTime = new Date();
    var hours = currentTime.getHours();
    var minutes = currentTime.getMinutes();

    // Add leading zero if needed
    hours = (hours < 10) ? "0" + hours : hours;
    minutes = (minutes < 10) ? "0" + minutes : minutes;

    // Format the time as HH:MM:SS
    var formattedTime = hours + ":" + minutes;

    // Update the content of the div
    document.getElementById("time").textContent =  formattedTime;
  }
    function displayReservationForTable(){
           var today_day = 10;
           for(let reservation of dataBaseEntries){
               console.log(reservation);
                let reservation_table = reservation[1];
                let reservation_day =reservation[2];
                let reservation_hour = reservation[3];
                let reservation_duration = reservation[4];
                let reservation_code = reservation[5];
                if(reservation_table != tableview) continue;
                let day = parseInt(reservation_day.split(' ')[0],10);
                for(let i = 0; i < 7; i++){
                   if(today_day + i === day) {

                       function getIndexFromTime(time) {
                           let hour = parseInt(time.split(':')[0]);
                           let minute = parseInt(time.split(':')[1]);
                           let index = 1;
                           index += minute / 15;
                           index += (hour - 7) * 4;
                           return index;
                       }

                       let hours = getIndexFromTime(reservation_hour);
                       let weekDay = i+1;
                       if(i > 4) weekDay -=2;
                       console.log(i);
                       let row = document.getElementsByTagName("tr")[weekDay];
                       for(let j = 0; j < reservation_duration/15; j++){
                           console.log(hours+j);
                           let table_cell = row.getElementsByTagName("td")[hours+j];

                           if(hours+j > 52) break
                           if(reservation_code === "-1") {
                               table_cell.style.backgroundColor = "red";
                           }
                           else {
                            table_cell.style.backgroundColor = "grey";
                           }
                       }
                   }
                }
          }
    }


   // document.getElementById("button-go-to-reservation").addEventListener("click", function () {
   //     socket.emit('button', 'ok');
   // });

    socket.on('new_value', function (data) {
        if (data['left']){
            handleButtonClick('left')
        }
        else if (data['right']){
            handleButtonClick('right')
        }
        //else if(data['ok']) {
        //    handleButtonClick('ok')
        //}
    });
    
    socket.on('rfid_id', function (data) {
        if (data['id']){
            handleButtonClick('ok')
        }
    });

    socket.on('data_base_entries', function (data){
       if(data["value"]){
           dataBaseEntries = data["value"];
           console.log(dataBaseEntries);
           displayHighlightedTable();
           displayReservationForTable();
       }
    });
})

