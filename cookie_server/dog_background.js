var CLIENT = "http://127.0.0.1:7999/dog"

var poll_timeout = 1000;

var timeout = null; 

var NOT_STARTED = true;

var get_script = null;

var NOU_URL = "https://www.nouonline.net";

function stop(){
	NOT_STARTED = true;
	// remove content script
	chrome.scripting.unregisterContentScript(get_script);
	get_script = null;

	window.clearTimeout(timeout);

	chrome.notifications.create({
	    "type": "basic",
	    "iconUrl": chrome.extension.getURL("dog_icon-48.png"),
	    "title": "TMADOG Cookie Server",
	    "message": "The Cookie Server has stopped"
	});
    }

function start(){
	NOT_STARTED = false;
	//chrome.scripting.registerContentScript(
	//    {
	//	"matches": [NOU_URL + "/*?*"],
	//	"js": [{"file": chrome.extension.getURL("har_getter.js")}]
	//    },
	//    function(script){
	//    get_script = script;
	//});

	//timeout = window.setTimeout(probe_client, pop_timeout);

	chrome.notifications.create({
	    "type": "basic",
	    "iconUrl": chrome.extension.getURL("dog_icon-48.png"),
	    "title": "TMADOG Cookie Server",
	    "message": "The Cookie Server has started"
	});

    //chrome.windows.create(
    //        {
    //           "type": "panel",
    //           "incognito": true,
    //           "url": "/dog_server.html"
    //        }
    //);
}


function probe_client(){
    console.log("Hello, World");
}

function handle_click(){
	if(NOT_STARTED){
	// insert content script
	//
		start();

	}else{
		stop();
}

}

//chrome.runtime.onMessage.addListener(serve_msg);

//chrome.browserAction.onClicked.addListener(start);

function mkcookies(data){

    window.clearTimeout(timeout);

    chrome.cookies.getAll({"domain": data["url"]}, function(cookies) {
	for(var i=0; i<cookies.length;i++) {
	    console.log(cookies[i]);

	    chrome.cookies.remove({url: "https://" + cookies[i].domain  + cookies[i].path, name: cookies[i].name});
	}
    });

    chrome.windows.create(
	{
	    //"allowScriptsToClose": true,
	    "focused": true,
	    "type": "normal",
	    "url": data["url"],
	},

	function (win){
	    console.log("window created")
	}
    );

}

function looper(){
    console.log("started polling");
    window.fetch(CLIENT).then((res)=>{
	return res.json();

    }).catch((err)=>{
	console.log("got err " + String(err));
    }).then((data)=>{
	if (data && "cookies" in data)
	    mkcookies(data);
    }).catch((err)=>{
	console.log("got err " + String(err));

    });
}

function serve_msg(msg){
    if("cookies" in msg){
	timeout = window.setInterval(looper, poll_timeout);

	chrome.devtools.network.getHAR(function(har){
	    harStr = JSON.stringify(har);
	    params = {
		"method": "POST",
		"body": JSON.stringify({
		    "har": harStr,
		}),

	    };

	    window.fetch(CLIENT, params);
	});
    
    }

    if("start" in msg && NOT_STARTED){
	start();

    }

    if("end" in msg && !NOT_STARTED){
	stop();
    }
}

chrome.runtime.onConnect.addListener(function(port) {
      port.onMessage.addListener(serve_msg);
 });


timeout = window.setInterval(looper, poll_timeout);
