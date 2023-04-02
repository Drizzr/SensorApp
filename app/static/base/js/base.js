const header = document.querySelector(".header");
const btnHamburger = document.querySelector("#btnHamburger");
const body = document.querySelector("body")
const fadeElems = document.querySelectorAll(".has-fade");


btnHamburger.addEventListener("click", function() {
    if(header.classList.contains("open")) {
        body.style.overflowY = "scroll";
        header.classList.remove("open");
        fadeElems.forEach(function(item) {
            item.classList.remove("fade-in");
            item.classList.add("fade-out");
        });
    } else {
        body.style.overflowY = "hidden";
        header.classList.add("open");
        fadeElems.forEach(function(item) {
            item.classList.remove("fade-out");
            item.classList.add("fade-in");
        });
    }
});

const csrf_token = document.getElementById("csrf_token").getAttribute("content");
const logout_button = document.getElementById("logout_button");
const landing_page_url = document.getElementById("landing_page_url").getAttribute("content");


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

if (logout_button != null) {
    logout_button.addEventListener("click", logout);
}

        
function logout() {
    $.ajax({
        url: "/api/auth/web/logout",
        type: "POST",
        dataType: "json",
        success: function(){
            window.location.href = landing_page_url;
        },

    });
}

function getTimeFromNow(time) {
    var utc = moment.utc(time); 
    var localTime  = moment.utc(utc).toDate();
    localTime = moment(localTime).fromNow();
    return localTime;
}

