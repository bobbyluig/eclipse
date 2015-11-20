var ws = new Wampy('ws://127.0.0.1:8080/ws/', {realm: 'lycanthrope'});

var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");

ws.subscribe('com.image', function(data) {
	var image = new Image();
	image.onload = function() {
		ctx.canvas.width = image.width;
		ctx.canvas.height = image.height;
		ctx.drawImage(image, 0, 0);
	}

	image.src = "data:image/jpeg;base64," + data[0];
});