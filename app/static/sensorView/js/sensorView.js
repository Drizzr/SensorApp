const room_view_url = document.getElementById("back_button").getAttribute("href");
const delete_button = document.getElementById("delete_button");
const sensor_id = document.getElementById("sensor_id").getAttribute("content");

function deleteSensor () {
    $.ajax({
        url: "/api/delete/sensor/" + sensor_id,
        type: "DELETE",
        dataType: "json",
        success: function(){
            window.location.href = room_view_url;
        },
    });

}

delete_button.addEventListener("click", deleteSensor);

const last_update_element = document.getElementById("lastUpdate");
const ctx = document.getElementById("sensor_chart").getContext('2d');
let delayed = false;
var sensorChart = NaN;
var last_update = "";


function configureData() {
    $.ajax({
        url: "/api/sensor/" + sensor_id + "/get-data?amount=30",
        type: "GET",
        dataType: "json",
        async: false,
        success: function(data){
            if (data["payload"]["last_update"]) {
                console.log(data)
                last_update = data["payload"]["last_update"];
                var rel_time = getTimeFromNow(last_update)
                last_update_element.innerText = "last Update: " + rel_time;
            }
            data["payload"]["timestamps"].forEach((timestamp) => {
                sensorChart.data.labels.push(getTimeFromNow(timestamp))
            });
            sensorChart.data.datasets =  createDataSets(data["payload"]["data"], data["payload"]["value_map"]);
            sensorChart.update()
        },
    });
}

function loadNewData() {
    $.ajax({
        url: "/api/sensor/" + sensor_id + "/get-update",
        type: "GET",
        dataType: "json",
        success: function(data){
            console.log(data)
            if (data["payload"]["last_update"]) {
                if (last_update != data["payload"]["last_update"]) {
                    last_update = data["payload"]["last_update"];
                    var rel_time = getTimeFromNow(last_update)
                    last_update_element.innerText = "last Update: " + rel_time;
                    var values = data["payload"]["data"];
                    sensorChart.data.datasets.forEach((dataset) => {
                        dataset.data.push(values[dataset.label]);
                    });
                    sensorChart.data.labels.push(rel_time);
                    sensorChart.update();
                }
            }
        }
    });
}

function createDataSets(values, valueMap) {
    datasets = [];

    for (var value in values){
        push = {
            label: value +  " in " + valueMap[value]["unit"],
            data: values[value],
            borderWidth: 1,
            borderColor: valueMap[value]["color"],
            backgroundColor: valueMap[value]["color"],
            tension: 0.4,
        }
        datasets.push(push);
    }
    return datasets;
}

function createChart() {
    sensorChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: NaN,
        },
        options: {
            legend: {
                labels: {
                    fontColor: "black",
                    fontSize: 14,
                }
            },
            parsing: false,
            normalized: true,
            scales: {
                yAxes: [{
                    display: true,
                    ticks: {
                        beginAtZero: true,
                        }
                    }],
                xAxes: [{
                        ticks: {
                            maxTicksLimit: window.innerWidth<700 ? 2:20,
                        }
                    }]
                },
            responsive: true,
            maintainAspectRatio: true,
        }
    });   
}

createChart();

configureData();
window.setInterval(function() {
    loadNewData();
}, 20000);


window.onresize = () => {
    sensorChart.options.scales.xAxes = [{
        ticks: {
            maxTicksLimit: window.innerWidth<700 ? 2:20,
        }
    }];
    sensorChart.update()
};