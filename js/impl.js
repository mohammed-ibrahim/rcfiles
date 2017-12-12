

var globalPrimaryDictionary = new Array();
var globalItemsPracticed = 0;
var globalStartedAt = new Date();
var pickRandomWtItem = false;
var dontKnowStaticValue = "dontknow";

var panelDefaultColor = "white";
var panelShadedColor = "Gainsboro";

var colorCodeMapping = {
    a: "mintcream",
    b: "mistyrose",
    c: "aliceblue",
    d: "thistle",
    e: "silver"
}

/*

.____                     .___
|    |    _________     __| _/
|    |   /  _ \__  \   / __ | 
|    |__(  <_> ) __ \_/ /_/ | 
|_______ \____(____  /\____ | 
        \/         \/      \/ 

*/

function load() {
    var textBox = document.getElementById("primary_input_text");

    if (!textBox.value) {
        alert("Empty input");
        return false;
    }

    var data = textBox.value
    var sdata = data.split("\n");

    for (line in sdata) {
        linedata = sdata[line];
        console.log("line: " + linedata);
        var content = linedata.split(" - ");
        if (content.length == 2) {

            console.log("content: " + content[0]);
            console.log("value: " +  content[1]);
            var qid = guid();
            var dictObj = {key: content[0], value: content[1], state: "v", qid: qid};
            globalPrimaryDictionary.push(dictObj);
            //dictMap[qid] = dictObj;
        } else {
            console.error("Entry format error: " + linedata);
        }
    }

    console.log("Size of dictionary: " + globalPrimaryDictionary.length);

    return true;
}

/*

   _____         .__         __________                                          .__                
  /     \ _____  |__| ____   \______   \_______  ____   ____  ____   ______ _____|__| ____    ____  
 /  \ /  \\__  \ |  |/    \   |     ___/\_  __ \/  _ \_/ ___\/ __ \ /  ___//  ___/  |/    \  / ___\ 
/    Y    \/ __ \|  |   |  \  |    |     |  | \(  <_> )  \__\  ___/ \___ \ \___ \|  |   |  \/ /_/  >
\____|__  (____  /__|___|  /  |____|     |__|   \____/ \___  >___  >____  >____  >__|___|  /\___  / 
        \/     \/        \/                                \/    \/     \/     \/        \//_____/  
*/

function process(doValidate) {
    if (doValidate) {

        var success = validate();

        if (!success) {

            return;
        }
    }

    nextPage();
    showHideDivs();
    updateIndex();
    fillContent();
    updateStatusBar();
    resetPanels();
}


/*
____   ____      .__  .__    .___       __          
\   \ /   /____  |  | |__| __| _/____ _/  |_  ____  
 \   Y   /\__  \ |  | |  |/ __ |\__  \\   __\/ __ \ 
  \     /  / __ \|  |_|  / /_/ | / __ \|  | \  ___/ 
   \___/  (____  /____/__\____ |(____  /__|  \___  >
               \/             \/     \/          \/ 
*/
function validate() {

    var pageState = document.getElementById("page_state_holder").value;

    if (pageState === "walkthrough") {

        return validateWalkthrough();
    } else if (pageState === "mcq") {

        return validateMcq();
    } else if (pageState === "mat") {

        return validateMat();
    } else {
        alert("Page state not defined");
    }
}

function validateWalkthrough() {

    var index = parseInt(document.getElementById("index_holder").value);

    if ((!pickRandomWtItem) && index >= globalPrimaryDictionary.length) {

        alert("All items are done");
        return false;
    }

    globalItemsPracticed = globalItemsPracticed + 1;
    return true;
}

function validateMcq() {
    var checkedValueQid;

    if (document.getElementById("mcq_a").checked) {

        checkedValueQid = document.getElementById("mcq_a").value;
    } else if (document.getElementById("mcq_b").checked) {

        checkedValueQid = document.getElementById("mcq_b").value;
    } else if (document.getElementById("mcq_c").checked) {

        checkedValueQid = document.getElementById("mcq_c").value;
    } else if (document.getElementById("mcq_d").checked) {

        checkedValueQid = document.getElementById("mcq_d").value;
    }

    if (checkedValueQid) {
        var hiddenQid = document.getElementById("qid_holder").value
        if (hiddenQid !== checkedValueQid) {
            alert("wrong answer");
            return false;
        }
    } else {
        alert("Please select one answer");
        return false;
    }

    //At this stage the answer is correct!
    //So delete the question.
    var itemsToDelete = [hiddenQid];
    console.log("Requesting to delete from validateMcq: " + itemsToDelete);
    deleteItems(itemsToDelete);
    globalItemsPracticed = globalItemsPracticed + 1;

    return true;
}

function assertMatSelection(word) {
    
    var lhsQid = document.getElementById("mat_lhs_label_" + word).value;
    var valueOfSelectedRhs = document.getElementById("mat_lhs_select_" + word).value;

    if (!valueOfSelectedRhs) {

        alert("please make a selection");
        return false;
    }

    var rhsQid = document.getElementById(valueOfSelectedRhs).value;

    if (lhsQid !== rhsQid) {
        alert("Wrong answer!!");
        return false;
    }

    return lhsQid;
}

function validateMat() {

    var selectionItems = ["a", "b", "c", "d", "e"];
    var lhsTemplate = "mat_td_lhs_lab_";
    var lhsLabelTemplate = "mat_lhs_label_";
    var rhsLabelTemplate = "mat_rhs_label_";
    var collectedQids = [];

    for (i=0; i<selectionItems.length; i++) {
        var lhsTdId = lhsTemplate + selectionItems[i];
        var currentLhsTdColor = document.getElementById(lhsTdId).style.backgroundColor;
        var itemsOnRhs = getRhsElementsIdsWithColor(currentLhsTdColor);

        if (!itemsOnRhs || itemsOnRhs.length < 1) {

            alert("Please make selection on position: " + selectionItems[i]);
            return false;
        }

        var rhsTdId = itemsOnRhs[0];
        var lastCharOfRhsTdId = rhsTdId[rhsTdId.length - 1];
        var lhsQid = document.getElementById(lhsLabelTemplate + selectionItems[i]).value;
        var rhsQid = document.getElementById(rhsLabelTemplate + lastCharOfRhsTdId).value;

        if (lhsQid !== rhsQid) {

            alert("Wrong answer for: " + selectionItems[i]);
            return false;
        }

        collectedQids.push(lhsQid);
    }

    console.log("Requesting to delete from validateMat: " + collectedQids);
    deleteItems(collectedQids);
    globalItemsPracticed = globalItemsPracticed + 5;
    return true;
}


/*

  _________       .__  __         .__           /\  __________        _____                      .__      __________                        
 /   _____/_  _  _|__|/  |_  ____ |  |__       / /  \______   \ _____/ ____\______   ____   _____|  |__   \______   \_____     ____   ____  
 \_____  \\ \/ \/ /  \   __\/ ___\|  |  \     / /    |       _// __ \   __\\_  __ \_/ __ \ /  ___/  |  \   |     ___/\__  \   / ___\_/ __ \ 
 /        \\     /|  ||  | \  \___|   Y  \   / /     |    |   \  ___/|  |   |  | \/\  ___/ \___ \|   Y  \  |    |     / __ \_/ /_/  >  ___/ 
/_______  / \/\_/ |__||__|  \___  >___|  /  / /      |____|_  /\___  >__|   |__|    \___  >____  >___|  /  |____|    (____  /\___  / \___  >
        \/                      \/     \/   \/              \/     \/                   \/     \/     \/                  \//_____/      \/ 

*/

function nextPage() {

    var pageState = document.getElementById("page_state_holder").value;
    var windowCountHolder = parseInt(document.getElementById("window_count_holder").value);

    if (windowCountHolder <= 1) {
        var nextGroup = getNextGroup(pageState);
        document.getElementById("page_state_holder").value = nextGroup["group"];
        document.getElementById("window_count_holder").value = nextGroup["length"];
    } else {

        windowCountHolder = windowCountHolder - 1;
        document.getElementById("window_count_holder").value = windowCountHolder.toString();
    }
}


/*
 _______                   __      ________                              _________      .__                 __  .__               
 \      \   ____ ___  ____/  |_   /  _____/______  ____  __ ________    /   _____/ ____ |  |   ____   _____/  |_|__| ____   ____  
 /   |   \_/ __ \\  \/  /\   __\ /   \  __\_  __ \/  _ \|  |  \____ \   \_____  \_/ __ \|  | _/ __ \_/ ___\   __\  |/  _ \ /    \ 
/    |    \  ___/ >    <  |  |   \    \_\  \  | \(  <_> )  |  /  |_> >  /        \  ___/|  |_\  ___/\  \___|  | |  (  <_> )   |  \
\____|__  /\___  >__/\_ \ |__|    \______  /__|   \____/|____/|   __/  /_______  /\___  >____/\___  >\___  >__| |__|\____/|___|  /
        \/     \/      \/                \/                   |__|             \/     \/          \/     \/                    \/ 
*/
function getNextGroup(currentGroup) {

    if (currentGroup == "walkthrough") {

        return { group: "mcq", length: 7 }
    } else if (currentGroup == "mcq") {

        return { group: "mat", length: 7 }
    } else if (currentGroup == "mat") {

        pickRandomWtItem = true;
        return { group: "walkthrough", length: 5 }
    } else {
        alert("Invalid currentGroup");
    }
}

function showHideDivs() {

    var pageState = document.getElementById("page_state_holder").value;

    document.getElementById("input_div").style.display = "none";
    document.getElementById("walkthrough_div").style.display = "none";
    document.getElementById("mcq_div").style.display = "none";
    document.getElementById("mat_div").style.display = "none";

    var pageState = document.getElementById("page_state_holder").value;

    if (pageState === "walkthrough") {

        document.getElementById("walkthrough_div").style.display = "block";
    } else if (pageState === "mcq") {

        document.getElementById("mcq_div").style.display = "block";
    } else if (pageState === "mat") {

        document.getElementById("mat_div").style.display = "block";
    } else {

        alert("Page state not defined");
    }
}

function updateIndex() {

    var pageState = document.getElementById("page_state_holder").value;

    if (pageState === "walkthrough") {

        var index = parseInt(document.getElementById("index_holder").value)
        document.getElementById("index_holder").value = (index + 1).toString();
    }
}

/*
_________                __                 __    __________                   .__          __  .__               
\_   ___ \  ____   _____/  |_  ____   _____/  |_  \______   \____ ______  __ __|  | _____ _/  |_|__| ____   ____  
/    \  \/ /  _ \ /    \   __\/ __ \ /    \   __\  |     ___/  _ \\____ \|  |  \  | \__  \\   __\  |/  _ \ /    \ 
\     \___(  <_> )   |  \  | \  ___/|   |  \  |    |    |  (  <_> )  |_> >  |  /  |__/ __ \|  | |  (  <_> )   |  \
 \______  /\____/|___|  /__|  \___  >___|  /__|    |____|   \____/|   __/|____/|____(____  /__| |__|\____/|___|  /
        \/            \/          \/     \/                       |__|                   \/                    \/ 
*/

function fillContent() {
    var pageState = document.getElementById("page_state_holder").value;

    if (pageState === "walkthrough") {

        return fillWalkthrough();
    } else if (pageState === "mcq") {

        return fillMcq();
    } else if (pageState === "mat") {

        return fillMat();
    } else {
        alert("Page state not defined");
    }

}

function fillWalkthrough() {
    //TODO:
    var nextIndex;
    var index = parseInt(document.getElementById("index_holder").value)

    if (pickRandomWtItem) {

        nextIndex = getRandomInt(0, globalPrimaryDictionary.length);
    } else {

        if (index >= globalPrimaryDictionary.length) {
            alert("Dictionary items are done!");
            return false;
        }

        nextIndex = index;
    }
    var obj = globalPrimaryDictionary[nextIndex];
    console.log("Next pickedup index is: " + nextIndex);
    console.log("loaded object is: " + obj);
    var key = obj["key"];
    var value = obj["value"];

    document.getElementById("walkthrough_key").innerHTML = key;
    document.getElementById("walkthrough_value").innerHTML = value;
}

function fillMcq() {
    //TODO: move to reset panels
    document.getElementById("mcq_a").checked = false;
    document.getElementById("mcq_b").checked = false;
    document.getElementById("mcq_c").checked = false;
    document.getElementById("mcq_d").checked = false;

    var r1 = getRandomInt(0, globalPrimaryDictionary.length);
    var r2 = getRandomInt(0, globalPrimaryDictionary.length);
    var r3 = getRandomInt(0, globalPrimaryDictionary.length);
    var r4 = getRandomInt(0, globalPrimaryDictionary.length);

    var mcqKey = globalPrimaryDictionary[r1]["key"];
    var mcqValue = globalPrimaryDictionary[r1]["value"];
    document.getElementById("qid_holder").value = globalPrimaryDictionary[r1]["qid"];
    document.getElementById("mcq_question").innerHTML = mcqKey;

    var originalState = [r1, r2, r3, r4];
    var shuffeledArray = shuffle(originalState);
    document.getElementById("label_for_mcq_a").innerHTML = globalPrimaryDictionary[shuffeledArray[0]]["value"];
    document.getElementById("label_for_mcq_b").innerHTML = globalPrimaryDictionary[shuffeledArray[1]]["value"];
    document.getElementById("label_for_mcq_c").innerHTML = globalPrimaryDictionary[shuffeledArray[2]]["value"];
    document.getElementById("label_for_mcq_d").innerHTML = globalPrimaryDictionary[shuffeledArray[3]]["value"];

    document.getElementById("mcq_a").value = globalPrimaryDictionary[shuffeledArray[0]]["qid"];
    document.getElementById("mcq_b").value = globalPrimaryDictionary[shuffeledArray[1]]["qid"];
    document.getElementById("mcq_c").value = globalPrimaryDictionary[shuffeledArray[2]]["qid"];
    document.getElementById("mcq_d").value = globalPrimaryDictionary[shuffeledArray[3]]["qid"];
}

function fillMat() {
    var r1 = getRandomInt(0, globalPrimaryDictionary.length);
    var r2 = getRandomInt(0, globalPrimaryDictionary.length);
    var r3 = getRandomInt(0, globalPrimaryDictionary.length);
    var r4 = getRandomInt(0, globalPrimaryDictionary.length);
    var r5 = getRandomInt(0, globalPrimaryDictionary.length);

    document.getElementById("mat_lhs_label_a").innerHTML = globalPrimaryDictionary[r1]["key"];
    document.getElementById("mat_lhs_label_a").value = globalPrimaryDictionary[r1]["qid"];

    document.getElementById("mat_lhs_label_b").innerHTML = globalPrimaryDictionary[r2]["key"];
    document.getElementById("mat_lhs_label_b").value = globalPrimaryDictionary[r2]["qid"];

    document.getElementById("mat_lhs_label_c").innerHTML = globalPrimaryDictionary[r3]["key"];
    document.getElementById("mat_lhs_label_c").value = globalPrimaryDictionary[r3]["qid"];

    document.getElementById("mat_lhs_label_d").innerHTML = globalPrimaryDictionary[r4]["key"];
    document.getElementById("mat_lhs_label_d").value = globalPrimaryDictionary[r4]["qid"];

    document.getElementById("mat_lhs_label_e").innerHTML = globalPrimaryDictionary[r5]["key"];
    document.getElementById("mat_lhs_label_e").value = globalPrimaryDictionary[r5]["qid"];


    var originalState = [r1, r2, r3, r4, r5];
    var shuffeledArray = shuffle(originalState);

    document.getElementById("mat_rhs_label_a").innerHTML = globalPrimaryDictionary[shuffeledArray[0]]["value"];
    document.getElementById("mat_rhs_label_a").value = globalPrimaryDictionary[shuffeledArray[0]]["qid"];

    document.getElementById("mat_rhs_label_b").innerHTML = globalPrimaryDictionary[shuffeledArray[1]]["value"];
    document.getElementById("mat_rhs_label_b").value = globalPrimaryDictionary[shuffeledArray[1]]["qid"];

    document.getElementById("mat_rhs_label_c").innerHTML = globalPrimaryDictionary[shuffeledArray[2]]["value"];
    document.getElementById("mat_rhs_label_c").value = globalPrimaryDictionary[shuffeledArray[2]]["qid"];

    document.getElementById("mat_rhs_label_d").innerHTML = globalPrimaryDictionary[shuffeledArray[3]]["value"];
    document.getElementById("mat_rhs_label_d").value = globalPrimaryDictionary[shuffeledArray[3]]["qid"];

    document.getElementById("mat_rhs_label_e").innerHTML = globalPrimaryDictionary[shuffeledArray[4]]["value"];
    document.getElementById("mat_rhs_label_e").value = globalPrimaryDictionary[shuffeledArray[4]]["qid"];
}

/*
  _________ __          __                 __________               
 /   _____//  |______ _/  |_ __ __  ______ \______   \_____ _______ 
 \_____  \\   __\__  \\   __\  |  \/  ___/  |    |  _/\__  \\_  __ \
 /        \|  |  / __ \|  | |  |  /\___ \   |    |   \ / __ \|  | \/
/_______  /|__| (____  /__| |____//____  >  |______  /(____  /__|   
        \/           \/                \/          \/      \/       
*/

function updateStatusBar() {

    var indexValue = document.getElementById("index_holder").value;
    var pageState = document.getElementById("page_state_holder").value;
    var now = new Date();
    var diffInMin = (now - globalStartedAt)/60000;
    var surplusSeconds = ((now - globalStartedAt) % 60000)/1000;
    var numMinutes = round(diffInMin, 2);
    var statusText = "gci: " + indexValue + " pst: " + pageState + " dl: " + globalPrimaryDictionary.length + " practiced: " + globalItemsPracticed + " mins: " + toInteger(numMinutes) + " seconds: " + toInteger(surplusSeconds); 
    document.getElementById("status_bar").innerHTML = statusText;
}

/*

__________                      __    __________                      .__          
\______   \ ____   ______ _____/  |_  \______   \_____    ____   ____ |  |   ______
 |       _// __ \ /  ___// __ \   __\  |     ___/\__  \  /    \_/ __ \|  |  /  ___/
 |    |   \  ___/ \___ \\  ___/|  |    |    |     / __ \|   |  \  ___/|  |__\___ \ 
 |____|_  /\___  >____  >\___  >__|    |____|    (____  /___|  /\___  >____/____  >
        \/     \/     \/     \/                       \/     \/     \/          \/ 
*/

function resetPanels() {

    var pageState = document.getElementById("page_state_holder").value;

    if (pageState === "walkthrough") {

        return resetWalkthroughPanel();
    } else if (pageState === "mcq") {

        return resetMcqPanel();
    } else if (pageState === "mat") {

        return resetMatPanel();
    } else {

        alert("Page state not defined");
    }
}

function resetWalkthroughPanel() {

    if (document.getElementById("walkthrough_show_meaning").checked) {
        //Show meaning box.
        document.getElementById("walkthrough_value").style.display = "block";
    } else {
        //Hide meaning box.
        document.getElementById("walkthrough_value").style.display = "none";
    }
}

function resetMcqPanel() {

}

function resetMatPanel() {

    var panelSuffixes = ["a", "b", "c", "d", "e"];

    for (var i = 0; i<panelSuffixes.length; i++) {
        document.getElementById("mat_td_lhs_lab_" + panelSuffixes[i]).style.backgroundColor = panelDefaultColor;

        document.getElementById("mat_td_rhs_lab_" + panelSuffixes[i]).style.backgroundColor = panelDefaultColor;
    }

}

/*
  ___ ___         .__                           _____          __  .__               .___      
 /   |   \   ____ |  | ______   ___________    /     \   _____/  |_|  |__   ____   __| _/______
/    ~    \_/ __ \|  | \____ \_/ __ \_  __ \  /  \ /  \_/ __ \   __\  |  \ /  _ \ / __ |/  ___/
\    Y    /\  ___/|  |_|  |_> >  ___/|  | \/ /    Y    \  ___/|  | |   Y  (  <_> ) /_/ |\___ \ 
 \___|_  /  \___  >____/   __/ \___  >__|    \____|__  /\___  >__| |___|  /\____/\____ /____  >
       \/       \/     |__|        \/                \/     \/          \/            \/    \/ 
*/
function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min)) + min; //The maximum is exclusive and the minimum is inclusive
}

function randomArray(length, max) {
    return Array.apply(null, Array(length)).map(function() {
        return Math.round(Math.random() * max);
    });
}

function shuffle(array) {
    var currentIndex = array.length, temporaryValue, randomIndex;

    // While there remain elements to shuffle...
    while (0 !== currentIndex) {

        // Pick a remaining element...
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex -= 1;

        // And swap it with the current element.
        temporaryValue = array[currentIndex];
        array[currentIndex] = array[randomIndex];
        array[randomIndex] = temporaryValue;
    }

    return array;
}

function guid() {

    function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    }

    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
        s4() + '-' + s4() + s4() + s4();
}



function deleteItems(items) {
    for (i=globalPrimaryDictionary.length - 1; i >= 0;  i--) {
        var obj = globalPrimaryDictionary[i];
        var qid = obj["qid"];
        if (items.includes(qid)) {
            var deleted = globalPrimaryDictionary.splice(i, 1);
            console.log("deleted");
            console.log(deleted);
        }
    }

    console.log("After deleting size of dictionary is: " + globalPrimaryDictionary.length);
}

function round(value, precision) {
    var multiplier = Math.pow(10, precision || 0);
    return Math.round(value * multiplier) / multiplier;
}

function toInteger(number){ 
    return Math.floor(  // round to nearest integer
        Number(number)    // type cast your input
    ); 
};



/*
  ___ ___   __          .__     __      __        .__   __      __  .__                              .__     
 /   |   \_/  |_  _____ |  |   /  \    /  \_____  |  | |  | ___/  |_|  |_________  ____  __ __  ____ |  |__  
/    ~    \   __\/     \|  |   \   \/\/   /\__  \ |  | |  |/ /\   __\  |  \_  __ \/  _ \|  |  \/ ___\|  |  \ 
\    Y    /|  | |  Y Y  \  |__  \        /  / __ \|  |_|    <  |  | |   Y  \  | \(  <_> )  |  / /_/  >   Y  \
 \___|_  / |__| |__|_|  /____/   \__/\  /  (____  /____/__|_ \ |__| |___|  /__|   \____/|____/\___  /|___|  /
       \/             \/              \/        \/          \/           \/                  /_____/      \/ 
*/

function hwalShowMeaningBox() {
    document.getElementById("walkthrough_value").style.display = "block";
}

function hwalToggleMeaningBox() {
    document.getElementById("walkthrough_show_meaning").checked = !document.getElementById("walkthrough_show_meaning").checked;

    if (document.getElementById("walkthrough_show_meaning").checked) {
        //Show meaning box.
        document.getElementById("walkthrough_value").style.display = "block";
    } else {
        //Hide meaning box.
        document.getElementById("walkthrough_value").style.display = "none";
    }
}

/*
  ___ ___   __          .__       _____                
 /   |   \_/  |_  _____ |  |     /     \   ____  ______
/    ~    \   __\/     \|  |    /  \ /  \_/ ___\/ ____/
\    Y    /|  | |  Y Y  \  |__ /    Y    \  \__< <_|  |
 \___|_  / |__| |__|_|  /____/ \____|__  /\___  >__   |
       \/             \/               \/     \/   |__|
*/

function hmcqSelChange(element) {
    var elementId = element.id;
    var lastChar = elementId[elementId.length - 1];
    document.getElementById("mcq_" + lastChar).checked = true;
    hcomOnButtonClick();
}

/*
  ___ ___   __          .__       _____          __   
 /   |   \_/  |_  _____ |  |     /     \ _____ _/  |_ 
/    ~    \   __\/     \|  |    /  \ /  \\__  \\   __\
\    Y    /|  | |  Y Y  \  |__ /    Y    \/ __ \|  |  
 \___|_  / |__| |__|_|  /____/ \____|__  (____  /__|  
       \/             \/               \/     \/      
*/

function hmatMarkLastLhsSelection(element) {
    var currentColor = document.getElementById(element.id).style.backgroundColor;

    document.getElementById("last_lhs_selection_id_holder").value = element.id;

    var lastSelection = element.id;
    var lastChar = lastSelection[lastSelection.length - 1];
    document.getElementById(element.id).style.backgroundColor = colorCodeMapping[lastChar];
}

function getRhsElementsIdsWithColor(color) {
    var rhsElements = Array();

    if ((!color) || color === panelDefaultColor) {

        return rhsElements;
    }

    var itemsToCheck = ["a", "b", "c", "d", "e"];

    for (var i=0; i<itemsToCheck.length; i++) {

        var keyVar = itemsToCheck[i];
        var fullKey = "mat_td_rhs_lab_" + keyVar;

        if (document.getElementById(fullKey).style.backgroundColor === color) {

            rhsElements.push(fullKey);
        }
    }

    return rhsElements;
}

function hmatMatchLastSelection(element) {

    var lastSelection = document.getElementById("last_lhs_selection_id_holder").value;

    if ((!lastSelection) || (lastSelection === dontKnowStaticValue)) {
        return;
    }

    var lastChar = lastSelection[lastSelection.length - 1];
    document.getElementById(element.id).style.backgroundColor = colorCodeMapping[lastChar];

    var otherElementsWithSameColor = getRhsElementsIdsWithColor(colorCodeMapping[lastChar]);
    document.getElementById("last_lhs_selection_id_holder").value = dontKnowStaticValue;
    if (!otherElementsWithSameColor) {

        return;
    }

    var thisElementId = element.id;
    for (var i=0; i<otherElementsWithSameColor.length; i++) {

        var otherElementId = otherElementsWithSameColor[i];

        if (thisElementId !== otherElementId) {

            document.getElementById(otherElementId).style.backgroundColor = panelDefaultColor;
        }
    }
}

function hmatResetMatSelections() {

    var itemsToCheck = ["a", "b", "c", "d", "e"];

    for (var i=0; i<itemsToCheck.length; i++) {

        var keyVar = itemsToCheck[i];
        document.getElementById("mat_td_lhs_lab_" + keyVar).style.backgroundColor = panelDefaultColor;
        document.getElementById("mat_td_rhs_lab_" + keyVar).style.backgroundColor = panelDefaultColor;
    }

    document.getElementById("last_lhs_selection_id_holder").value = dontKnowStaticValue;
}

/*
  ___ ___   __          .__    _________                                       
 /   |   \_/  |_  _____ |  |   \_   ___ \  ____   _____   _____   ____   ____  
/    ~    \   __\/     \|  |   /    \  \/ /  _ \ /     \ /     \ /  _ \ /    \ 
\    Y    /|  | |  Y Y  \  |__ \     \___(  <_> )  Y Y  \  Y Y  (  <_> )   |  \
 \___|_  / |__| |__|_|  /____/  \______  /\____/|__|_|  /__|_|  /\____/|___|  /
       \/             \/               \/             \/      \/            \/ 
*/

function hcomOnButtonClick() {
    process(true);
}

function hinPloadDict() {

    var value = load();

    if (!value) {

        return;
    }

    document.getElementById("page_state_holder").value = "walkthrough";
    //document.getElementById("page_state_holder").value = "mat";

    var numOfInitialWalkThrough = 20;
    document.getElementById("window_count_holder").value = (numOfInitialWalkThrough + 1).toString();
    document.getElementById("index_holder").value = "-1";
    document.getElementById("status_bar").style.display = "block";
    
    process(false);
}

window.onload = function() {
    var textBox = document.getElementById("primary_input_text");
    textBox.value = "one - 1one and simple\n"
    textBox.value += "two - 2two and the average text content is this much.\n"
    textBox.value += "three - 3three ringa ringa roses.\n"
    textBox.value += "four - 4four ba ba black sheep have you.\n"
    textBox.value += "five - 5five twinkle twinkle little start.\n"
    textBox.value += "six - 6six a new page.\n"
    textBox.value += "seven - 7seven test data.\n"
    textBox.value += "eight - 8eight on average the eighth.\n"
    textBox.value += "nine - 9nine small\n"
    textBox.value += "zero - 0zero"
};

