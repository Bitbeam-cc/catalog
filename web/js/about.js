About = function() {
    this.version = document.querySelector("#about_page span[prop=version]");
}

About.prototype.load = function() {
    ajax_get('/api/version', this.on_about_load.bind(this));
}

About.prototype.on_about_load = function(xhr) {
    if (xhr.status != 200) {
        return;
    }

    let data = JSON.parse(xhr.responseText);
    console.log(data);
    this.version.innerText = data['m-bitbeam'];
}
