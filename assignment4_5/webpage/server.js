console.log("testing")



/*
var spawn = require("child_process").spawn;
var process = spawn('python', ["query_database.py","four"]);



process.stdout.on('data', function (chunk) {

    var textChunk = chunk.toString();// buffer to string

    console.log(textChunk);
});*/

var spawn = require("child_process").spawn;
var process = spawn('python', ["compute_input.py", "mayan"]);



process.stdout.on('data', function (chunk) {

    var textChunk = chunk.toString();// buffer to string

    console.log(textChunk);
});
