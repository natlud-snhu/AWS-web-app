var lambdaCalculatorTimer = false;
var results = 0;

function lambdaCalculate(input_type) {
    convert = false; //Whether to convert to or from a 24bit float
    if (input_type == "number") { //user inputted in first field
        var rawInput = Number(document.getElementById("float_input").value); //converts input into a number
        if (Object.is(rawInput, NaN)) { //failed conversion
            document.getElementById("results").innerHTML = "Input isn't a number!";
            return null;
        } else if (rawInput < 1 && rawInput > -1) {
            document.getElementById("results").innerHTML = "Input must not be be smaller than 1!";
            return null;
        } else if (rawInput < -18446673704965374000 || rawInput > 18446673704965374000) {
            document.getElementById("results").innerHTML = "Input is too large!";
            return null;          
        }
        convert = true;
    } else if (input_type == "hexadecimal") { //user inputted in second field
        var rawInput = document.getElementById("float_output").value;
        if (isNaN(rawInput)) {//isn't a number
            return null;
        } else {
            rawInput = parseInt(rawInput); //converts rawInput from hex string to integer
            if (rawInput > 0xFFFFFF | rawInput < -0xFFFFFF) { //out of bounds
                return null;
            }
        }
    } else if (input_type == "binary") { //user inputted in third field
        var rawInput = document.getElementById("binary_output").value;
        if (isNaN(rawInput)) {//isn't a number
            return null;
        } else {
            rawInput = parseInt(rawInput, 2); //converts rawInput from hex string to integer
            console.log(rawInput);
            if (rawInput > 0xFFFFFF | rawInput < -0xFFFFFF) { //out of bounds
                return null;
            }
        }
    }
    if (lambdaCalculatorTimer == false) { //ensures enough time has elapsed between calls to prevent spamming
        lambdaCalculatorTimer = true; //function is on cooldown
        setTimeout(() => {lambdaCalculatorTimer = false;},500); //only allows function to be called once every half second
        AWS.config.region = 'us-east-2'; // Region
        AWS.config.credentials = new AWS.CognitoIdentityCredentials({
            IdentityPoolId: 'us-east-2:894043a5-2b88-485a-ae29-a3738b87c005',
        });
        var lambda = new AWS.Lambda();
        console.log(JSON.stringify({convertto: convert.toString(), number: rawInput}));
        lambda.invoke({
            FunctionName: 'calculator',
            Payload: JSON.stringify({convertto: convert.toString(), number: rawInput})
        }, function(err, data) {
            var results = JSON.parse(data.Payload)["results"];
            //display results
            if (JSON.parse(data.Payload)["statusCode"] == "400") { //received HTTP fail status
                document.getElementById("results").innerHTML = "Failed!";
                return null;
            }
            document.getElementById("results").innerHTML = ""; //Success!
            if (convert) {
                results = results.slice(1, results.lastIndexOf('"'))
                document.getElementById("float_output").value = results;
                document.getElementById("binary_output").value = parseInt(results, 16).toString(2);
            } else if (input_type == "hexadecimal") {
                document.getElementById("float_input").value = results;
                document.getElementById("binary_output").value = rawInput.toString(2);
            } else if (input_type == "binary") {
                document.getElementById("float_input").value = results;
                document.getElementById("float_output").value = "0x" + rawInput.toString(16);
            }
        }) 
    }
}