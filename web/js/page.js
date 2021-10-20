Page = function(){
    this.active = null;

    this.link_catalog = document.querySelector("a[page=catalog].nav-link");
    this.link_about = document.querySelector("a[page=about]");

    this.catalog = new Catalog();
    this.part = new Part();

    document.addEventListener("DOMContentLoaded", this.on_loaded.bind(this));
    window.addEventListener('hashchange', function() {
        this.parse_hash();
    }.bind(this), false);
}

Page.prototype.hide = function() {
    if (this.active != null) {
        this.active.style.display = 'none';
        document.querySelector("a[page].active").classList.remove("active");
    }
}

Page.prototype.show = function(id) {
    this.active = document.querySelector(id);
    this.active.style.display = '';
}

Page.prototype.switch_catalog = function() {
    let update = false;
    if (this.active && this.active.id == "catalog_page"){
        update = true;
    }

    if (!update) {
        this.hide();
        this.show("#catalog_page");
        this.link_catalog.classList.add('active');
        this.catalog.init();
    } else {
        this.catalog.update();
    }
}

Page.prototype.switch_part = function() {
    if (this.active && this.active.id == "part_page"){
        return;
    }

    this.hide();
    this.show("#part_page");
    this.link_catalog.classList.add('active');
    this.part.load();
}


Page.prototype.switch_about = function() {
    if (this.active && this.active.id == "about_page"){
        return;
    }

    this.hide();
    this.show("#about_page");
    this.link_about.classList.add('active');
}


Page.prototype.parse_hash = function() {
    let page_url = document.location.hash.split('=')[0];
    if (page_url == "#about"){
        this.switch_about();
    } else if (page_url == "#part"){
        this.switch_part();
    } else {
        this.switch_catalog();
    }
}

Page.prototype.on_loaded = function(event) {
    this.link_catalog.addEventListener(
        'click', this.switch_catalog.bind(this));
    this.link_about.addEventListener(
        'click', this.switch_about.bind(this));
    this.parse_hash();
}

let page = new Page();
