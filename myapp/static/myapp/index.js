function getCookie(c_name) {
    if(document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if(c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if(c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function scrollIntoView(eleID) {
    var e = document.getElementById(eleID);
    if (!!e && e.scrollIntoView) {
        e.scrollIntoView();
    }
}
$('[data-toggle="tooltip"]').tooltip();


var boxCount = 0;
var selectedExercises = [];
$("input.exerciseCheck").change(function (value) {
    if ($('#exe'+extractExerciseInfo(value).id).is(':checked')) {
        $('#exe'+extractExerciseInfo(value).id).addClass('checked');
        if(boxCount == 0){
            $('#exerciseForm').append("<h4>Enter Weight Range</h4>"
                + "<p class='help-block'>Enter the reps and weight of each lift so that we can compare which muscles are strong and weak (For better results, use rep ranges 1-3)</p>");
            //$('#exerciseFrequency').append("<hr><h4>Enter Exercise Frequency</h4>"
            //+ "<p class='help-block'>Enter the number of sets, reps, and how many days a week that each exercise should be done</p>");
        }
        //append this exercise
        $('#exerciseForm').append(exerciseFormBuilder(extractExerciseInfo(value)));
        //$('#exerciseFrequency').append(exerciseFrequencyBuilder(extractExerciseInfo(value)));
        selectedExercises.push((extractExerciseInfo(value)).id);
        boxCount++;
    } else {
        $('#exe'+extractExerciseInfo(value).id).removeClass('checked');
        //remove this exercise
        $("#cust"+extractExerciseInfo(value).id).remove();
        //$("#fre"+extractExerciseInfo(value).id).remove();
        if(boxCount == 1){
            $('#exerciseForm').empty();
            //$('#exerciseFrequency').empty();
        }
        var index = selectedExercises.indexOf(extractExerciseInfo(value).id);
        selectedExercises.splice(index, 1);
        boxCount--;
    }
});

function exerciseFrequencyBuilder(value){
    var returnedHtml =  "<div id='fre" + value.id + "' class='form-group' style='margin-bottom:5px;'>"
        + "<form class='form-horizontal'>"
        + "<fieldset>"
        + "<label class='col-md-2 control-label' for='prependedtext'>" + value.name + "</label>"
        + "<div class='col-md-9'>"
        + "<div class='input-group'>"
        + "<div class='input-group-addon'><input type='number' class='form-control' id='set" + value.id + "' placeholder='Sets'></div>"
        + "<div class='input-group-addon'><input type='number' class='form-control' id='rep" + value.id + "' placeholder='Reps'></div>"
        + "<div class='input-group-addon'><input type='number' class='form-control' min='1' max='5' id='freq" + value.id + "' placeholder='Days'></div>"
        + "</div>"
        + "</div>"
        + "</div>"
        + "</fieldset>"
        + "</form>";
    return returnedHtml;
}

function exerciseFormBuilder(value){
    var returnedHtml =  "<div id='cust" + value.id + "' class='form-group' style='margin-bottom:5px;'>"
        + "<form class='form-horizontal'>"
        + "<fieldset>"
        + "<label class='col-md-2 control-label' for='prependedtext'>" + value.name + "</label>"
        + "<div class='col-md-9'>"
        + "<div class='input-group'>"
        + "<div class='input-group-addon'><input type='number' class='form-control' id='reps" + value.id + "' placeholder='reps'></div>"
        + "<div class='input-group-addon'><input type='number' class='form-control' id='weight" + value.id + "' placeholder='weight'></div>"
        + "</div>"
        + "</div>"
        + "</div>"
        + "</fieldset>"
        + "</form>";
    return returnedHtml;
}

function extractExerciseInfo(value){
    var name = value.currentTarget.labels[0].innerText;
    var id = value.currentTarget.labels[0].childNodes[1].id;
    id = id.split("exe")[1];
    return {'name':name, 'id':id}
}

function extractFormInfo(value){
    var value = parseInt(value);
    var pk = value;
    var reps,weight;
    if($("#reps"+value).val()){
        reps = parseInt($("#reps"+value).val());
    }
    else{
        $("#creationError").append("<p style='color:red;'>Please fill out the number of reps</p><br>");
    }
    if($("#weight"+value).val()){
        weight = parseInt($("#weight"+value).val());
    }
    else{
        $("#creationError").append("<p style='color:red;'>Please fill out the number of sets</p><br>");
    }
    var returnme = [pk, reps, weight];
    for(var i=0; i < returnme.length; i++){
        if(isNaN(returnme[i])){
            return false;
        }
    }
    return returnme;
}

$( "#createRoutine" ).click(function() { //probably removing this
    $("#creationError").empty();
    $("#resultLifts").empty();
    $(".resultMuscleC").empty();
    $("#resultMusclesTitle").empty();
    if($("#bodyWeight").val()){
        var bodyWeight = parseInt($("#bodyWeight").val());
    }
    else{
        $("#creationError").append("<p style='color:red;'>Please enter your weight!</p><br>");
        return false;
    }
    var data = [];
    var dataInside = [];
    for(var i=0; i < selectedExercises.length; i++){
        var errorCheck = extractFormInfo(selectedExercises[i]);
        if(errorCheck == false){
            //undefined value somewhere
            console.log("undefined value somewhere");
            return false;
        }
        else{
            dataInside.push(errorCheck);
        }
        //need pk, set, rep freq, beg, nov, int, adv, elite
    }
    data.push(dataInside);
    var dataSend = {gender:($("#genderMale").is(':checked')), bweight:bodyWeight, rows: data[0]};
    $("#preMuscleLoader").append("<div id='routineBeforeL' class='loading-container'>"
        + "<div class='loading'></div>"
        + "<div id='loading-text'>loading</div>"
        + "</div>");
    $.ajax({
        type: 'POST',
        url: 'compareUser/',
        headers : {
            "X-CSRFToken": getCookie("csrftoken")
        },
        async:false,
        data: {'dataSend[]': JSON.stringify(dataSend)},
        //processData: false,
        //contentType: false,
        success: function(json) {
            $("#resultLifts").append("<hr>");
            $("#resultLifts").append("<h4>Exercise Score</h4>");
            for(var i=0; i < json.exerciseStats.length; i++){
                $("#resultLifts").append("<p>" + json.exerciseStats[i].exerciseName + " - " + json.exerciseStats[i].Value + ". Strength Score: " + json.exerciseStats[i].Strength + " with estimated 1 rep max of: " + json.exerciseStats[i].OneRepMax + "</p></br>");
            }
            $("#resultLifts").append("<hr>");
            $("#resultMusclesTitle").append("<h4>Muscle Score</h4>");
            $("#BeginnerMuscle").append("<label><u>Beginner</u></label>");
            $("#NoviceMuscle").append("<label><u>Novice</u></label>");
            $("#IntermediateMuscle").append("<label><u>Intermediate</u></label>");
            $("#AdvancedMuscle").append("<label><u>Advanced</u></label>");
            $("#EliteMuscle").append("<label><u>Elite</u></label>");
            for(var i=0; i < json.muscleStats.length; i++){
                $("#" + json.muscleStats[i][3] + "Muscle").append("<p>" + json.muscleStats[i][1] + " - " + json.muscleStats[i][2] + "</p>");
            }

            $("#preMuscleLoader").empty()
            $("#preRoutineLoader").append("<div id='routineBeforeL' class='loading-container'>"
                + "<div class='loading'></div>"
                + "<div id='loading-text'>loading</div>"
                + "</div>");
            scrollIntoView("preRoutineLoader");
            generateRoutineSeq(json.forRoutine);
        },
        error: function(json){
            console.log("ERROR", json);
        }
    })
    function generateRoutineSeq(routineEntry){
        var dataSend = {routineEntryVal:routineEntry};
        $.ajax({
            type: 'POST',
            url: 'genRoutine/',
            headers : {
                "X-CSRFToken": getCookie("csrftoken")
            },
            //async:false,
            data: {'dataSend[]': JSON.stringify(dataSend)},
            //processData: false,
            //contentType: false,
            success: function(json) {

                for(var i=0; i < json.routineMonday.length; i++){
                    $("#mondayRoutine").append("<td><a data-toggle='tooltip' title='" + json.routineMonday[i][4] + "'>" + json.routineMonday[i][0] + "<br>" + json.routineMonday[i][2] + " x " + json.routineMonday[i][3] +"</a></td>");
                }
                for(var i=0; i < json.routineTuesday.length; i++){
                    $("#tuesdayRoutine").append("<td><a data-toggle='tooltip' title='" + json.routineTuesday[i][4] + "'>" + json.routineTuesday[i][0] + "<br>" + json.routineTuesday[i][2] + " x " + json.routineTuesday[i][3] +"</a></td>");
                }
                for(var i=0; i < json.routineWednesday.length; i++){
                    $("#wednesdayRoutine").append("<td><a data-toggle='tooltip' title='" + json.routineWednesday[i][4] + "'>" + json.routineWednesday[i][0] + "<br>" + json.routineWednesday[i][2] + " x " + json.routineWednesday[i][3] +"</a></td>");
                }
                for(var i=0; i < json.routineThursday.length; i++){
                    $("#thursdayRoutine").append("<td><a data-toggle='tooltip' title='" + json.routineThursday[i][4] + "'>" + json.routineThursday[i][0] + "<br>" + json.routineThursday[i][2] + " x " + json.routineThursday[i][3] +"</a></td>");
                }
                for(var i=0; i < json.routineFriday.length; i++){
                    $("#fridayRoutine").append("<td><a data-toggle='tooltip' title='" + json.routineFriday[i][4] + "'>" + json.routineFriday[i][0] + "<br>" + json.routineFriday[i][2] + " x " + json.routineFriday[i][3] +"</a></td>");
                }
                $("#preRoutineLoader").empty();
                $("#resultRoutine").show();
                scrollIntoView("resultRoutine");
                console.log("SUCCESS");
            },
            error: function(json){
                console.log("ERROR", json);
            }
        })
    }

});