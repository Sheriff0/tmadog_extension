var port = chrome.runtime.connect({
      name: "Sample Communication"
 });

port.postMessage("Hi BackGround");

port.onMessage.addListener(function(msg) {
  alert("message recieved" + msg);
});
