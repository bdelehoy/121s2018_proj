const express = require('express');
const bodyParser = require('body-parser')
var spawn = require("child_process").spawn;

const app = express();
app.use(bodyParser.urlencoded({extended: true}))
app.listen(3000, function() {console.log('listening on 3000\ngo to localhost:3000 in a web browser')})
app.set('view engine', 'ejs')
app.use(express.static(__dirname + '/views'));

var textChunk = [];


app.get('/', (req, res) => {
   //console.log("GET", textChunk)
   res.render('index.ejs', { results: textChunk })
    textChunk=[]
})



app.post('/query', (req, res) => {
    console.log("POST starting py process")
    console.log("POST sending this to query_database: ", req.body.search_query)
    
    var python_cmd_array = ["query_database.py"];
    for (i = 0; i <= req.body.search_query.split().length; i++) {
        python_cmd_array.push(req.body.search_query.split(" ")[i])
    }
    for (i = 0; i < python_cmd_array.length; i++) {
        if (python_cmd_array[i] == undefined) {
            python_cmd_array.splice(i, 1)
        }
    }
    console.log("POST command array contains: ", python_cmd_array)


    var process = spawn('python', python_cmd_array);
    console.log("POST process created")
    process.stdout.on('data', function (chunk) {
        console.log("POST stdout from python started.")
        var temp = []
        temp = chunk.toString().split("\n");

        for(i = 0; i < temp.length; i++) {
            var fields = temp[i].split("\t")
            //console.log(fields)
            textChunk.push(fields)
        }
        temp = []
    });

    process.stdout.on('end', function () {
        console.log("POST stdout from python finished.")
        if(textChunk.length == 0) { 
            //console.log("POST No results found!") 
            textChunk.push(["", "", "No results.", ""]) // follow the format of a generic search result
        } 
        res.redirect("/");
    })

})
    