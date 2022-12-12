const view_calls = document.getElementById("view-calls");
const api_calls = document.getElementById("api-calls");
const unique_users = document.getElementById("unique-users");
const new_users = document.getElementById("new-users");
const total_users = document.getElementById("total-users");
const total_sensors = document.getElementById("total-sensors");

const shutdown_button = document.getElementById("shutdown_button");

if (shutdown_button !== null) {
    shutdown_button.addEventListener("click", shutdown);
}


const log_container = document.getElementById("log-container");

const ctx = document.getElementById("responsive_chart").getContext('2d');

var chart = NaN

const csrf_token = document.getElementById("csrf_token").getAttribute("content");

function connect_api() {
    $.ajax({
        url: "/api/auth/api-connect/web",
        type: "POST",
        dataType: "json",
        headers: {"X-CSRFToken": csrf_token},
        async: false,
        success: function(data){
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrf_token);
                        }
                        xhr.setRequestHeader("x-access-token", data.payload["x-access-token"]);
                        xhr.setRequestHeader("x-refresh-token", data.payload["x-refresh-token"]);
                    }
        
            });
            $(document).ajaxError(function myErrorHandler(event, xhr, ajaxOptions, thrownError) {
                if (xhr.status === 401) {
                    connect_api();
                }
            });
            console.log("successfully pre-connected to api-service")
        },
        error: function(data){
            console.log(data);
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrf_token);
                    }
                }
            }); 
        },
    });
}


connect_api();
function createDataSets(values, color_map) {
    datasets = [];

    for (var value in values){
        push = {
            label: value,
            data: values[value],
            borderWidth: 1,
            borderColor: color_map[value],
            tension: 0.4,
        }
        datasets.push(push);
    }
    return datasets;
}

function shutdown() {
    $.ajax({
        url: "/api/admin/emergency/shutdown",
        type: "POST",
    });
}

function getDayData() {
    $.ajax({
        url: "/api/admin/dashboard/get-data/today",
        type: "GET",
        dataType: "json",
        success: function(data){
                console.log(data)
                view_calls.innerText = data["payload"]["view_calls"];
                api_calls.innerText = data["payload"]["api_calls"];
                unique_users.innerText = data["payload"]["unique_users"];
                new_users.innerText = data["payload"]["new_registered_users"];
                total_users.innerText = data["payload"]["total_users"];
                total_sensors.innerText = data["payload"]["total_sensors"];
                
            },
        });
}

function loadChartData(amount) {
    $.ajax({
        url: "/api/admin/dashboard/chart-data?amount=" + amount.toString(),
        type: "GET",
        dataType: "json",
        success: function(data){
                chart.data.labels = data["payload"]["timestamps"];  
                chart.data.datasets = createDataSets(data["payload"]["data"], data["payload"]["colors"]);
                chart.update();
            },
    });
}


function createChart() {
    chart = new Chart(ctx, {
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

createChart()
loadChartData(30);
getDayData();
window.setInterval(function() {
    getDayData();
}, 20000);

window.onresize = () => {
    chart.options.scales.xAxes = [{
        ticks: {
            maxTicksLimit: window.innerWidth<700 ? 2:20,
        }
    }];
    chart.update()
};