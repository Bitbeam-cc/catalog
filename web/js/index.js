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
    elm.setAttribute("category", "All");
    elm.innerText = "All";
    categories.appendChild(elm);

    let data = JSON.parse(xhr.responseText);
    data["categories"].forEach(function(it){
        elm = document.createElement("a");
        elm.setAttribute("class", "nav-link");
        if (category == it.name){
            elm.classList.add("active");
        }

        elm.setAttribute("href", "#category="+it.name);
        elm.setAttribute("category", it.name);
        elm.innerText = it.name;
        qu = document.createElement("span");
        qu.setAttribute("class", "float-right");
        qu.innerText = it.quantity.toString();
        elm.appendChild(qu);

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
    let params = parse_url();
    if (params.category != undefined) {
        category = params.category;
        if (category == 'All'){
            category = null;
        }
    } else {
        category = null;
    }

    if (active == null || active[0].id != 'catalog_page') {
        if (active != null) {
            active.hide();
            document.querySelector("a[page].active").classList.remove("active");
        }
        active = $("#catalog_page");
        active.show();
        document.querySelector("a[page=catalog].nav-link").classList.add("active");
        ajax_get("/api/categories", on_update_categories);
        ajax_get("/api/parts?"+pager_url(params.offset | 0), on_update_parts);
    } else {
        document.querySelector("[prop=categories] .active")
            .classList.remove("active");
        ajax_get("/api/parts?"+pager_url(params.offset | 0), on_update_parts);
        document.querySelector("a[category="+(category || "All")+"]")
            .classList.add("active");
    }
}

function switch_about(){
    if (active != null) {
        active.hide();
        document.querySelector("a[page].active").classList.remove("active");
    }

    active = $("#about_page");
    active.show();
    document.querySelector("a[page=about]").classList.add("active");
}

function switch_download(){
    if (active != null) {
        active.hide();
        document.querySelector("a[page].active").classList.remove("active");
    }

    active = $("#download_page");
    active.show();
    document.querySelector("a[page=download]").classList.add("active");
}

function parse_hash(){
    if (window.location.hash == "#about"){
        switch_about();
    } else if (window.location.hash == "#download"){
        switch_download();
    } else {
        switch_catalog();
    }
}

document.addEventListener("DOMContentLoaded", function(event){
    $("a[page=catalog]").click(switch_catalog);
    $("a[page=about]").click(switch_about);
    $("a[page=download]").click(switch_download);

    parse_hash();
});

window.addEventListener('hashchange', function() {
    parse_hash();
}, false);
