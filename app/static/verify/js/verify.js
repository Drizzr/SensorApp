
const request_button = document.getElementById("new_verify_link_button");

request_button.addEventListener("click", request_verfiy_token);

function check_verify_status() {
    $.ajax({
        url: "/auth/verify-status",
        type: "GET",
        dataType: "json",
        async: false,
        success: function(data) {
            console.log(data);
            if (data.verified == true) {
                console.log(1)
                window.location.href = landing_page_url;
            }
        }
    });
}


function request_verfiy_token() {
    $.ajax({
        url: "/auth/verify/new-link",
        type: "POST",
        dataType: "json",
        async: false,
        success: function(data){
            alert("a new link has been send to your email")
        },
    });
}

check_verify_status();

window.setInterval(function() {
    check_verify_status();
}, 2000);
