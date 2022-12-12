const room_id = document.getElementById("room_id").getAttribute("content");


function loadNewData() {
    $.ajax({
        url: "/api/room/" + room_id + "/updates",
        type: "GET",
        dataType: "json",
        success: function(data){
            console.log(data["payload"]);
            for (const [public_id, sensor_data] of Object.entries(data["payload"])) {
                if (sensor_data["last_update"]) {
                    document.getElementById(public_id+"_lastUpdate").innerText = "last update: " + getTimeFromNow(sensor_data["last_update"]);
                }
                for (const [key, value] of Object.entries(data["payload"][public_id]["values"])) {
                    document.getElementById(public_id+"_"+key).innerText = key + ": " + value.toString() + data["payload"][public_id]["value_map"][key]["unit"];
                }
            }
            
        },
    });
}


loadNewData();
window.setInterval(function() {
    loadNewData();
}, 20000);