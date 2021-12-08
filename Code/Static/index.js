      PART OF THE WORK SYSTEM, NOT READY YET

function test() {
	let object;
	let httpRequest = new XMLHttpRequest(); // asynchronous request
	httpRequest.open("GET", "../static/game_data.json", true);
	httpRequest.send();
	httpRequest.addEventListener("readystatechange", function() {
    	if (this.readyState === this.DONE) {
      		// when the request has completed
        	object = JSON.parse(this.response);
					return object;
    	}
		});
	}

const data = test();
console.log(data);
