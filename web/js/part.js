Part = function() {
    this.title = document.querySelector('#part_page h2');
    this.img = document.querySelector('#part_page img');
    this.link_stl = document.querySelector('#part_page a[type=stl]');
    this.link_dat = document.querySelector('#part_page a[type=dat]');
    this.categories = document.querySelector('#part_page ul');
}

Part.prototype.load = function() {
    let params = parse_url();
    ajax_get("/api/parts/"+params.part, this.on_part_load.bind(this));
}

Part.prototype.on_part_load = function(xhr) {
    if (xhr.status != 200) {
        return;
    }

    let data = JSON.parse(xhr.responseText);
    console.log(data);
    this.title.innerText = data['name'];
    this.img.setAttribute('src', '/png/'+data['file']+'.png');
    this.link_stl.setAttribute('href', '/stl/'+data['file']+'.stl');
    this.link_dat.setAttribute('href', '/parts/'+data['file']+'.dat');

    this.categories.innerHTML = '';
    data['categories'].forEach(function(it, index){
        let link = document.createElement('a');
        link.setAttribute('href', '#category='+it['category'])
        link.innerText = it['category'];

        let li = document.createElement('li');
        li.setAttribute('class', 'list-group-item');
        li.appendChild(link);
        this.categories.appendChild(li);
    }.bind(this));
}
