function ajax_get(url, callback){
    let xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Accept", "application/json");
    xhr.onreadystatechange = function(){
        if (xhr.readyState != 4){
            return;
        }
        callback(xhr);
    };
    xhr.send();
}

function parse_url(){
    let params = {};
    document.location.hash.substring(1).split("&").forEach(function(it){
        let keyval = it.split("=");
        params[keyval[0]]=keyval[1];
    });
    return params;
}
