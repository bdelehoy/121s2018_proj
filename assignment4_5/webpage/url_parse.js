console.log("testing")
var param = window.location.search;
param = param.substr(14).split("+").join(" ");
document.write( param); 
