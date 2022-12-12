
const request_verify_token = document.getElementById("request_verfiy_token").getAttribute("content");
const csrf_token = document.getElementById("csrf_token").getAttribute("content");


function check_verify_status() {
    $.ajax({
        url: "/auth/verify-status",
        type: "GET",
        dataType: "json",
        async: false,
        success: function(data){
            console.log(data)
        },
    });
}

check_verify_status();