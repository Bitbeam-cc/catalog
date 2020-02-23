var active = null;      // active page

var category = null;

function ajax_get(url, callback){
    let xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
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

function on_update_categories(xhr){
    if (xhr.status != 200){
        return;
    }

    let categories = document.querySelector("nav[prop=categories]");
    categories.innerHTML = '';  // drop all children

    let elm = document.createElement("a");
    elm.classList.add("nav-link");
    if (category == null){
        elm.classList.add("active");
    }

    elm.setAttribute("href", "#");
    elm.innerText = "All";
    elm.addEventListener("click", function(ev){
        category = null;
        document.querySelector("[prop=categories] .active").classList.remove("active");
        ev.target.classList.add("active");
        ajax_get("/api/parts", on_update_parts);
    });
    categories.appendChild(elm);

    let data = JSON.parse(xhr.responseText);
    data["categories"].forEach(function(it){
        elm = document.createElement("a");
        elm.setAttribute("class", "nav-link");
        if (category == it){
            elm.classList.add("active");
        }

        elm.setAttribute("href", "#catergory="+it);
        elm.innerText = it;
        elm.addEventListener("click", function(ev){
            category = it;
            document.querySelector("[prop=categories] .active").classList.remove("active");
            ev.target.classList.add("active");
            ajax_get("/api/parts?category="+it, on_update_parts);
        });

        categories.appendChild(elm);
    });
}

function pager_url(offset){
    let params = {};
    if (category != null) {
        params.category = category;
    }
    if (offset != 0) {
        params.offset = offset;
    }
    return $.param(params);
}

function redraw_pager(pager){
    let pagination = document.querySelector("ul.pagination");
    pagination.innerHTML = '';

    // Previous
    let li = document.createElement("li");
    li.classList.add("page-item");
    let a = document.createElement("a");
    a.classList.add("page-link");
    a.setAttribute("href", "#"+pager_url(pager.offset-pager.limit));
    a.innerText = "Previous";

    if (pager.page == 0){
        li.classList.add("disabled");
    } else {
        a.addEventListener("click", function(){
            let url = "/api/parts?"+pager_url(pager.offset-pager.limit);
            ajax_get(url, on_update_parts);
        });
    }

    li.appendChild(a)
    pagination.appendChild(li);

    // TODO: pages between 2 3 [4] 5 6

    // Next
    li = document.createElement("li");
    li.classList.add("page-item");
    a = document.createElement("a");
    a.classList.add("page-link");
    a.setAttribute("href", "#"+pager_url(pager.offset+pager.limit));
    a.innerText = "Next";

    if (pager.page == pager.pages){
        li.classList.add("disabled");
    } else {
        a.addEventListener("click", function(){
            let url = "/api/parts?"+pager_url(pager.offset+pager.limit);
            ajax_get(url, on_update_parts);
        });
    }

    li.appendChild(a)
    pagination.appendChild(li);
}

function on_update_parts(xhr){
    if (xhr.status != 200){
        return;
    }

    let parts = document.querySelector("div[prop=parts]");
    parts.innerHTML = '';  // drop all children

    let data = JSON.parse(xhr.responseText);
    data["parts"].forEach(function(it, index){
            let card = document.createElement("div");
            card.setAttribute("class", "card");

            let img = document.createElement("img");
            img.setAttribute("class", "card-img-top");
            img.setAttribute("src", "/png/"+it["file"]+".png");
            card.appendChild(img)

            let body = document.createElement("div");
            body.setAttribute("class", "card-body");
            card.appendChild(body)

            let title = document.createElement("h5");
            title.setAttribute("class", "card-title");
            title.innerText = it["name"];
            body.appendChild(title);

            /*
            let file = document.createElement("a");
            file.setAttribute("class", "card-link");
            file.setAttribute("href", it["file"]+".stl");
            file.innerText = it["file"];
            body.appendChild(file);
            */

            parts.appendChild(card);
    });

    redraw_pager(data["pager"]);
}


function switch_catalog(){
    if (active != null) {
        active.hide();
    }

    let params = parse_url();
    if (params.category != undefined) {
        category = params.category;
    }

    active = $("#catalog_page");
    active.show();
    ajax_get("/api/categories", on_update_categories);
    ajax_get("/api/parts?"+pager_url(params.offset | 0), on_update_parts);
}

function switch_about(){
    if (active != null) {
        active.hide();
    }

    active = $("#about_page");
    active.show();
}

function switch_api(){
    if (active != null) {
        active.hide();
    }

    active = $("#api_page");
    active.show();

    if ($("redoc").children().length == 0) {
        $.getScript("https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js");
    }
}

document.addEventListener("DOMContentLoaded", function(event){
    $("a[page=catalog]").click(switch_catalog);
    $("a[page=about]").click(switch_about);
    $("a[page=api]").click(switch_api);

    if (window.location.hash == "#about"){
        switch_about();
    } else if (window.location.hash == "#api"){
        switch_api();
    } else {
        switch_catalog();
    }
});
