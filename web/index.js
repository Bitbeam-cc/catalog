var categories = document.querySelector("nav[prop=categories]");
var parts = document.querySelector("div[prop=parts]");
var pagination = document.querySelector("ul.pagination");
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

function on_update_categories(xhr){
    if (xhr.status != 200){
        return;
    }

    categories.innerHTML = '';  // drop all children

    let elm = document.createElement("a");
    elm.classList.add("nav-link");
    elm.classList.add("active");

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
    data["categories"].forEach(function(it, index){
        elm = document.createElement("a");
        elm.setAttribute("class", "nav-link");
        elm.setAttribute("href", "#");
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

function redraw_pager(pager){
    pagination.innerHTML = '';

    // Previous
    let li = document.createElement("li");
    li.classList.add("page-item");
    let a = document.createElement("a");
    a.classList.add("page-link");
    a.setAttribute("href", "#");
    a.innerText = "Previous";

    if (pager.page == 0){
        li.classList.add("disabled");
    } else {
        a.addEventListener("click", function(){
            let url = "/api/parts?offset="+(pager.offset-pager.limit);
            if (category != null) {
                url += "&category="+category;
            }
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
    a.setAttribute("href", "#");
    a.innerText = "Next";

    if (pager.page == pager.pages){
        li.classList.add("disabled");
    } else {
        a.addEventListener("click", function(){
            let url = "/api/parts?offset="+(pager.offset+pager.limit);
            if (category != null) {
                url += "&category="+category;
            }
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

    parts.innerHTML = '';  // drop all children

    let data = JSON.parse(xhr.responseText);
    data["parts"].forEach(function(it, index){
            console.log(index + " is " + it);
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



document.addEventListener("DOMContentLoaded", function(event){
    if (window.location.hash == "#about"){
        document.querySelector("#about").style.display="";
    } else if (window.location.hash == "#api"){
        let api = document.querySelector("#api");
        api.style.display="";
        let script = document.createElement("script");
        script.src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js"
        api.appendChild(script);
    } else {
        document.querySelector("#catalog").style.display="";
        ajax_get("/api/categories", on_update_categories);
        ajax_get("/api/parts", on_update_parts);
    }
});
