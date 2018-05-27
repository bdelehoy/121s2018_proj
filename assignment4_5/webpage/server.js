console.log("testing")




var spawn = require("child_process").spawn;
var process = spawn('python', ["C:/Users/Shoshani/Documents/card-algorithms/Space-Jam/assignment4_5/query_database.py","four"]);



process.stdout.on('data', function (chunk) {

    var textChunk = chunk.toString();// buffer to string

    console.log(textChunk);
});
/*
var spawn = require("child_process").spawn;
var process = spawn('python', ["C:/Users/Shoshani/Documents/card-algorithms/Space-Jam/assignment4_5/webpage/compute_input.py", "mayan"]);



process.stdout.on('data', function (chunk) {

    var textChunk = chunk.toString();// buffer to string

    console.log(textChunk);
});
*/