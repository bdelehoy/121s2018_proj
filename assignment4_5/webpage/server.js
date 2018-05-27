console.log("testing")
const express = require('express');
const app = express();
app.listen(3000, function() {console.log('listening on 3000')})


app.get('/', (req, res) => {
    var spawn = require("child_process").spawn;
    var process = spawn('python', ["C:/Users/Shoshani/Documents/card-algorithms/Space-Jam/assignment4_5/query_database.py","four"]);



    process.stdout.on('data', function (chunk) {
        console.log("data returned")
        var textChunk = chunk.toString();// buffer to string

        re.send(textChunk);
    });
})



/*
app.get('/', (req, res) => {
   // res.send('Hello World yall')
    var spawn = require("child_process").spawn;
    var process = spawn('python', ["C:/Users/Shoshani/Documents/card-algorithms/Space-Jam/assignment4_5/webpage/compute_input.py", "mayan"]);

    process.stdout.on('data', function (chunk) {

        var textChunk = chunk.toString();// buffer to string
        res.send(textChunk);
    });
})
*/



    