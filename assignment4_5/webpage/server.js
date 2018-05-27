console.log("testing")

/*
var spawn = require('child_process').spawn,
    //py = spawn('python', ['compute_input.py']),
    py = spawn('python', ['query_database.py', 'four']),
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9],
    dataString = '';

py.stdout.on('data', function (chunk) {
    console.log('returns data')
    dataString += chunk.toString('utf8');
    console.log(dataString)
});
py.stdout.on('end', function () {
    console.log('Sum of numbers=', dataString);
});

py.stdin.end();
*/

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
