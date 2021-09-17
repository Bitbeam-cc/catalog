Page = function(){
    this.active = null;

    this.link_catalog = document.querySelector("a[page=catalog].nav-link");
    this.link_about = document.querySelector("a[page=about]");
    this.link_download = document.querySelector("a[page=download]");

    this.catalog = new Catalog();

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

Page.prototype.switch_about = function() {
    if (this.active && this.active.id == "about_page"){
        return;
    }

    this.hide();
    this.show("#about_page");
    this.link_about.classList.add('active');
}

Page.prototype.switch_download = function() {
    if (this.active && this.active.id == "download_page"){
        return;
    }

    this.hide();
    this.show("#download_page");
    this.link_download.classList.add('active');
}

Page.prototype.parse_hash = function() {
    if (window.location.hash == "#about"){
        this.switch_about();
    } else if (window.location.hash == "#download"){
        this.switch_download();
    } else if (window.location.hash == "#piece"){
        this.switch_piece();
    } else {
        this.switch_catalog();
    }
}

Page.prototype.on_loaded = function(event) {
    this.link_catalog.addEventListener(
        'click', this.switch_catalog.bind(this));
    this.link_about.addEventListener(
        'click', this.switch_about.bind(this));
    this.link_download.addEventListener(
        'click', this.switch_download.bind(this));
    this.parse_hash();
}

let page = new Page();
