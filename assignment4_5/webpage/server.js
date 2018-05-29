const express = require('express');
const bodyParser = require('body-parser')
var spawn = require("child_process").spawn;

const app = express();
app.use(bodyParser.urlencoded({extended: true}))
app.listen(3000, function() {console.log('listening on 3000\ngo to localhost:3000 in a web browser')})
app.set('view engine', 'ejs')
app.use(express.static(__dirname + '/views'));

var textChunk = [];
var query_to_display_back_to_user;


app.get('/', (req, res) => {
    console.log("GET")
    res.render('index.ejs', { results: textChunk , user_query: query_to_display_back_to_user})
    textChunk=[]
    query_to_display_back_to_user = ""
})



app.post('/query', (req, res) => {
    console.log("POST Received this from the user: ", req.body.search_query)
    query_to_display_back_to_user = req.body.search_query;
    
    // Setting up argv for the python script
    var python_cmd_array = ["query_database.py"];
    var split_queries = req.body.search_query.split(" ");
    for (i = 0; i <= split_queries.length; i++) {
        if(split_queries[i] != "") {
            python_cmd_array.push(split_queries[i])
        }
    }
    for (i = 0; i < python_cmd_array.length; i++) {
        if (python_cmd_array[i] == undefined) {
            python_cmd_array.splice(i, 1)
        }
    }
    console.log("POST sending this to query_database.py: ", python_cmd_array)


    console.log("POST starting py process")
    var process = spawn('python', python_cmd_array);
    process.stdout.on('data', function (chunk) {
        console.log("POST received stdout from python.")
        var temp = []
        temp = chunk.toString().split("\n");

        for(i = 0; i < temp.length; i++) {
            var fields = temp[i].split("\t")
            // fields[0] = Rank
            // fields[1] = Doc ID
            // fields[2] = TFIDF score
            // fields[3] = URL
            //console.log(fields)
            textChunk.push(fields)
        }
    });

    process.stdout.on('end', function () {
        console.log("POST stdout from python finished.")
        if(textChunk.length == 0) {
            //console.log("POST No results found!")
            textChunk.push(["", "n/a", "n/a", ""]) // follow the format of a generic search result
        } 
        res.redirect("/");
    })

})
