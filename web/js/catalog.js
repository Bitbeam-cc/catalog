Catalog = function() {
    this.category = null;

    this.categories = document.querySelector("nav[prop=categories]");
    this.parts = document.querySelector("div[prop=parts]");
    this.pagination = document.querySelector("ul.pagination");
}

Catalog.prototype.parse_category = function(){
    let params = parse_url();

    if (params.category != undefined) {
        this.category = params.category;
        if (this.category == 'All'){
            this.category = null;
        }
    } else {
        this.category = null;
    }

    return params;
}

Catalog.prototype.pager_url = function(offset, limit = 12){
    let query = new URLSearchParams();

    if (this.category != null) {
        query.append('category', this.category);
    }
    if (offset != 0) {
        query.append('offset', offset);
    }
    if (limit != 12) {
        query.append('limit', limit);
    }

    return query.toString();
}

Catalog.prototype.init = function() {
    let params = this.parse_category();

    ajax_get("/api/categories", this.on_update_categories.bind(this));
    ajax_get("/api/parts?"+this.pager_url(params.offset | 0),
       this.on_update_parts.bind(this));
}

Catalog.prototype.update = function() {
    let params = this.parse_category();

    document.querySelector("a[category].active")
        .classList.remove("active");
    ajax_get("/api/parts?"+this.pager_url(params.offset | 0),
        this.on_update_parts.bind(this));
    document.querySelector("a[category="+(this.category || "All")+"]")
            .classList.add("active");
}

Catalog.prototype.redraw_pager = function(pager) {
    this.pagination.innerHTML = '';

    // Previous
    let li = document.createElement("li");
    li.classList.add("page-item");
    let a = document.createElement("a");
    a.classList.add("page-link");
    a.setAttribute("href", "#"+this.pager_url(pager.offset-pager.limit));
    a.innerText = "Previous";

    if (pager.page == 0){
        li.classList.add("disabled");
    }

    li.appendChild(a)
    this.pagination.appendChild(li);

    // TODO: pages between 2 3 [4] 5 6

    // Next
    li = document.createElement("li");
    li.classList.add("page-item");
    a = document.createElement("a");
    a.classList.add("page-link");
    a.setAttribute("href", "#"+this.pager_url(pager.offset+pager.limit));
    a.innerText = "Next";

    if (pager.page == pager.pages){
        li.classList.add("disabled");
    }

    li.appendChild(a)
    this.pagination.appendChild(li);
}

Catalog.prototype.on_update_categories = function(xhr) {
    if (xhr.status != 200){
        return;
    }

    this.categories.innerHTML = '';  // drop all children

    let elm = document.createElement("a");
    elm.classList.add("nav-link");
    if (this.category == null){
        elm.classList.add("active");
    }

    elm.setAttribute("href", "#");
    elm.setAttribute("category", "All");
    elm.innerText = "All";
    this.categories.appendChild(elm);

    let data = JSON.parse(xhr.responseText);
    data["categories"].forEach(function(it) {
        elm = document.createElement("a");
        elm.setAttribute("class", "nav-link");
        if (this.category == it.name){
            elm.classList.add("active");
        }

        elm.setAttribute("href", "#category="+it.name);
        elm.setAttribute("category", it.name);
        elm.innerText = it.name;
        qu = document.createElement("span");
        qu.setAttribute("class", "float-right");
        qu.innerText = it.quantity.toString();
        elm.appendChild(qu);

        this.categories.appendChild(elm);
    }.bind(this));
}

Catalog.prototype.on_update_parts = function(xhr) {
    if (xhr.status != 200){
        return;
    }

    this.parts.innerHTML = '';  // drop all children

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

            this.parts.appendChild(card);
    }.bind(this));

    this.redraw_pager(data["pager"]);
}
