from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth import logout as auth_logout

#old stuff
from datetime import datetime
#from django.db import models
#from models import Stats
from operator import itemgetter
from django.views.decorators.csrf import csrf_exempt
from .models import Stats2, compoundExercises, exercise, routine, exerciseForRoutine, exerciseCompare2, muscle, muscleGroupMajor, muscleGroupMinor, auxExercise, routineEntry, generatedRoutineExercise, muscleStats
from django.template import RequestContext
from django.core import serializers
#from django.utils import simplejson
import random
import json

from django.http import HttpResponse
#end olf


# Create your views here.

def index(request):
    if request.user.is_authenticated():
        #send them to /home
        template = loader.get_template('index.html')
        exerciseList = auxExercise.objects.filter(isCompound = True)
        context = {
            'compoundExercises': exerciseList,
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("signin")

def signin(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")
    else:
        #send them to /home
        template = loader.get_template('signin.html')
        context = {

        }
        return HttpResponse(template.render(context, request))

def headerSignIn(request):
    if request.is_ajax():
        if request.method == "POST":
            data = request.POST.getlist("data[]")
            user = authenticate(username=str(data[0]), password=str(data[1]))
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse("return this string")
            else:
                return HttpResponse("Does not match")

def signout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")

#old stuff

def saveStats(request):
    name = request.POST.getlist('dataSend[]') #[BenchWeight, benchRep, SquatWeight, SquatRep, DeadWeight, DeadRep, PullupWeight, PullupRep, User]
    if request.method == 'POST':
        if request.is_ajax():
            userForeign = request.user
            stats = Stats2(BenchWeight=name[0], BenchReps=name[1], SquatWeight=name[2], SquatReps=name[3], DeadWeight=name[4], DeadReps=name[5], PullupWeight=name[6], PullupReps=name[7], author=userForeign)
            stats.save()
            return HttpResponse(userForeign)
    else:
        return HttpResponse("Error")

def newUser(request):
    info = request.POST.getlist('dataSend[]')
    if request.method == 'POST':
        if request.is_ajax():
            #strip info[0] everything before @
            username = info[0].split('@')[0]
            #new_user = User(Username=username, Email=info[0], Password=info[1])

            new_user=User.objects.create_user(username, info[0], info[1])
            #new_user.first_name = self.cleaned_data['first_name']
            #new_user.last_name = self.cleaned_data['last_name']
            new_user.save()
            return HttpResponse("Welcome, " + username)
    else:
        return HttpResponse("Error")

def getMuscleDict():
    allMuscles = muscle.objects.all()
    muscleDict = []
    for x in allMuscles:
        muscleDict.append({'muscleName': str(x.muscleName), 'primaries':[], 'secondaries':[], 'pk':x.pk, 'muscleStrength':0})
    return muscleDict

def muscleDictPopulateScore(row, exercisePk, heur):
    primaries = muscleGroupMajor.objects.filter(exerciseActual = exercisePk, muscleActual = row['pk'])
    secondaries = muscleGroupMinor.objects.filter(exerciseActual = exercisePk, muscleActual = row['pk'])
    for x in primaries:
        row['primaries'].append(heur)
    for y in secondaries:
        row['secondaries'].append(heur)
    return row

def calculateMuscleStrength(muscleDict, PRIMHEUR, SECONDHEUR): #primheur and secondheur are modifiable heuristics. Starting out with 70% 30% but that could change
    for y in muscleDict:
        prim = 0
        second = 0
        for a in y['primaries']:
            prim = prim + a
        for b in y['secondaries']:
            second = second + b
        if len(y['primaries']) >= 1:
            if len(y['secondaries']) >=1:
                muscleStrength = ((PRIMHEUR * (prim/len(y['primaries']))) + (SECONDHEUR * (second/len(y['secondaries'])))) #gr8 (1,1)
            else:
                muscleStrength = (((prim/len(y['primaries'])))) #no secondaries (1,0)
        elif len(y['primaries']) == 0:
            if (len(y['secondaries'])) >=1:
                muscleStrength = (((second/len(y['secondaries'])))) #no primaries (0,1)
            else:
                muscleStrength = 0

        y['muscleStrength'] = round(muscleStrength,3)
    return muscleDict

def updateMuscleCounter2(routineWeek, muscleCounter):
    print "MUSCLECOUNTER ENTRY: ", muscleCounter
    for x in routineWeek:
        primary = muscleGroupMajor.objects.filter(exerciseActual = x[1])
        for y in primary:
            if y.muscleActual.pk in muscleCounter:
                muscleCounter[y.muscleActual.pk][1] = muscleCounter[y.muscleActual.pk][1] + ((x[2] * (10/x[3])) * 0.6) # sets * 10/rep. Heuristic takes account for number of sets and prioritizes lower reps (because lower rep = compound). Need to mult this by major or minor for each muscle
            else:
                muscleCounter[y.muscleActual.pk] = [y.muscleActual.muscleName, ((x[2] * (10/x[3])) * 0.6)]

        secondary = muscleGroupMinor.objects.filter(exerciseActual = x[1])
        for y in secondary:
            if y.muscleActual.pk in muscleCounter:
                muscleCounter[y.muscleActual.pk][1] = muscleCounter[y.muscleActual.pk][1] + ((x[2] * (10/x[3])) * 0.4) # sets * 10/rep. Heuristic takes account for number of sets and prioritizes lower reps (because lower rep = compound). Need to mult this by major or minor for each muscle
            else:
                muscleCounter[y.muscleActual.pk] = [y.muscleActual.muscleName, ((x[2] * (10/x[3])) * 0.4)]
    print "MUSCLECOUNTER EXIT: ", muscleCounter
    return muscleCounter

def generateMondayRoutine2(musclesUsed, exerciseCounter, dayNumber):
    print "entered generateMondayRoutine2"
    exerciseCounter['dayNumber'] = dayNumber
    compoundCounter = 0
    isolationCounter = 0
    compoundMax = 10
    isolationMax = 10
    routineWeek = []
    for x in musclesUsed:
        primary = muscleGroupMajor.objects.filter(muscleActual = x[0]).order_by('?')
        for y in primary:
            exerciseAddedFlag = False
            if compoundCounter <= compoundMax:
                #check if there is a compound, use the first one found
                try:
                    print "current y = ", y
                    compoundLift = auxExercise.objects.get(exerciseActual = y.exerciseActual.pk, isCompound = True)
                    print "exerciseCounter = ", exerciseCounter
                    if compoundLift.exerciseActual.exerciseName in exerciseCounter:
                        if (exerciseCounter[compoundLift.exerciseActual.exerciseName][1] + 1) >= dayNumber:
                            print "exercise found duplicate", compoundLift.exerciseActual.exerciseName
                            break
                        else:
                            exerciseCounter[compoundLift.exerciseActual.exerciseName]= [compoundLift.exerciseActual.pk, dayNumber]
                    else:
                        print "exercise is new", compoundLift.exerciseActual.exerciseName
                        exerciseCounter[compoundLift.exerciseActual.exerciseName]= [compoundLift.exerciseActual.pk, dayNumber]
                    flag = True
                    for t in routineWeek:
                        if t[1] == compoundLift.exerciseActual.pk:
                            flag = False
                            t[2] = t[2] + 1
                    if flag: #exercise does not exist exists, append it
                        routineWeek.append([compoundLift.exerciseActual.exerciseName,compoundLift.exerciseActual.pk,3,5,"Compound exercise for "+x[1]])
                        exerciseAddedFlag = True
                    compoundCounter = compoundCounter + 1
                    break
                except:
                    print "EXERCISE", y.exerciseActual.exerciseName , "NOT COMPOUND. NOT ADDING"
            if not exerciseAddedFlag:
                print y.muscleActual.muscleName, "did not receive any compound exercises. ERROR:1"

        secondary = muscleGroupMajor.objects.filter(muscleActual = x[0]).order_by('?')
        for y in secondary:
            exerciseAddedFlag = False
            if isolationCounter <= isolationMax:
                try:
                    isolationLift = auxExercise.objects.get(exerciseActual = y.exerciseActual.pk, isCompound = False)
                    if isolationLift.exerciseActual.exerciseName in exerciseCounter:
                        if (exerciseCounter[isolationLift.exerciseActual.exerciseName][1] + 1) >= dayNumber:
                            print "exercise found duplicate", isolationLift.exerciseActual.exerciseName
                            break
                        else:
                            exerciseCounter[isolationLift.exerciseActual.exerciseName] = [isolationLift.exerciseActual.pk, dayNumber]
                    else:
                        print "exercise is new", isolationLift.exerciseActual.exerciseName
                        exerciseCounter[isolationLift.exerciseActual.exerciseName]= [isolationLift.exerciseActual.pk,dayNumber]
                    flag = True
                    for t in routineWeek:
                        if t[1] == isolationLift.exerciseActual.pk:
                            flag = False
                            t[2] = t[2] + 1
                    if flag: #exercise does not exist exists, append it
                        routineWeek.append([isolationLift.exerciseActual.exerciseName,isolationLift.exerciseActual.pk, 3, 10, "Isolation exercise for "+x[1]])
                        exerciseAddedFlag = True
                    isolationCounter = isolationCounter + 1
                    break
                except:
                    print "EXERCISE", y.exerciseActual.exerciseName , "NOT ISOLATION. NOT ADDING"
            if not exerciseAddedFlag:
                print y.muscleActual.muscleName, "did not receive any isolation exercises. ERROR:1"
    return (routineWeek, exerciseCounter)

@csrf_exempt
def compareUser(request):
    if request.method == 'POST':
        #if request.is_ajax():
        if 1 == 1:
            info = request.POST.getlist('dataSend[]') #Contains {gender:true, bweight:200, rows: [[1,5,225],[2,5,315]]} . [exercisePK, rep, weight]
            info = json.loads(info[0])
            print "info = ", info
            try:
                muscleDict = getMuscleDict() #[{muscleName, primaries[], secondaries[], pk, muscleStrength}..{}]
                outerArr = []
                gender = info['gender'] #true or false
                bodyWeightUser = info['bweight']
                for x in info['rows']:
                    exerciseLookUp = exercise.objects.get(pk = int(x[0]))
                    reps = x[1]
                    weightLifted = x[2]
                    oneRepMax = (weightLifted / (1.0278 - ( 0.0278 * reps))) #Brzycki Formula
                    try:
                        comparison = exerciseCompare2.objects.filter(exerciseActual = exerciseLookUp, genderMale = gender, bodyWeight__lte=bodyWeightUser).order_by('-bodyWeight')[0] #still need to filter by bodyWeight
                    except:
                        comparison = exerciseCompare2.objects.filter(exerciseActual = exerciseLookUp, genderMale = gender).order_by('bodyWeight')[0]
                    value = "Beginner"
                    heur = 1.0
                    if oneRepMax >= comparison.elite:
                        value = "Elite"
                        heur = 5.0
                    elif oneRepMax >= comparison.advanced:
                        value = "Advanced"
                        heur = 4.0 + ((oneRepMax - comparison.elite) / (comparison.elite - comparison.advanced))
                    elif oneRepMax >= comparison.intermediate:
                        value = "Intermediate"
                        heur = 3.0 + ((oneRepMax - comparison.advanced) / (comparison.advanced - comparison.intermediate))
                    elif oneRepMax >= comparison.novice:
                        value = "Novice"
                        heur = 2.0 + ((oneRepMax - comparison.intermediate) / (comparison.intermediate - comparison.novice))
                    elif oneRepMax >= comparison.beginner:
                        value = "Beginner"
                        heur = 1.0 + ((oneRepMax - comparison.beginner) / (comparison.novice - comparison.beginner))
                    valueReturned  = {'Value':value, 'OneRepMax':round(oneRepMax,3), 'ExercisePK':x[0], 'exerciseName': exerciseLookUp.exerciseName, 'Strength':round(heur,3)}
                    print "valueReturned = ", valueReturned
                    outerArr.append(valueReturned)
                    for y in muscleDict:
                        #if y['pk'] == int(x[0]): #if the current exercise(x) uses the given muscle(y). Meaning if there is a muscleGroupMajor or muscleGroupMinor using (exerciseActual=x.pk, muscleActual=y.pk)
                        y = muscleDictPopulateScore(y, int(x[0]), heur)
                muscleDict = calculateMuscleStrength(muscleDict, 0.7, 0.3)

                muscleStatsArr = []
                for x in muscleDict:
                    if x['muscleStrength'] > 0:
                        #below returns dict which cant be sorted. Going to return an array instead
                        #muscleStats.append(x)
                        score = "Beginner"
                        if x['muscleStrength'] > 4:
                            score = "Elite"
                        elif x['muscleStrength'] > 3:
                            score = "Advanced"
                        elif x['muscleStrength'] > 2:
                            score = "Intermediate"
                        elif x['muscleStrength'] > 1:
                            score = "Novice"

                        muscleStatsArr.append([x['pk'], x['muscleName'], x['muscleStrength'], score])
                muscleStatsArr = sorted(muscleStatsArr, key=itemgetter(2)) #index #2. Sorting stats by lowest first
                try:
                    authorAdd = request.user
                    newRoutine = routineEntry(author=authorAdd, date=datetime.now)
                    newRoutine.save()
                    newlyCreated = routineEntry.objects.filter(author=request.user).latest('pk')
                except:
                    newRoutine = routineEntry(date=datetime.now)
                    newRoutine.save()
                    newlyCreated = routineEntry.objects.all().latest('pk')
                    print newlyCreated

                for x in muscleStatsArr:
                    thisMuscle = muscle.objects.get(pk=x[0])
                    newMuscleStat = muscleStats(muscleActual=thisMuscle, muscleStrength=x[2], muscleScore=x[3], entryForm=newlyCreated)
                    newMuscleStat.save()

                json_stuff = json.dumps({"exerciseStats" : outerArr, "muscleStats" : muscleStatsArr, "forRoutine" : newlyCreated.pk})
                #print "inbetween"
                return HttpResponse(json_stuff, content_type ="application/json")
            except:
                #print "inside except"
                return HttpResponse("Error in except")
            print "DONE WITH ALL OF IT"


@csrf_exempt
def genRoutine(request):
    if request.method == 'POST':
        print "entered"
        info = request.POST.getlist('dataSend[]') #Contains routineEntry.pk
        info = json.loads(info[0])
        print "INFO = ", info['routineEntryVal']

        try:
            #get routineEntry
            #get muscleStats
            newlyCreated = routineEntry.objects.get(pk=info['routineEntryVal'])
            print "newlyCreated = ", newlyCreated
            muscleStatList = muscleStats.objects.filter(entryForm = newlyCreated)
            print "muscleStatList = ", muscleStatList
            #muscleStatsArr = ([x['pk'], x['muscleName'], x['muscleStrength'], score])
            muscleStatsArr = []
            for x in muscleStatList:
                muscleStatsArr.append([x.muscleActual.pk, str(x.muscleActual.muscleName), x.muscleStrength, str(x.muscleScore)])

            print "muscleStatsArr = ", muscleStatsArr
            routineWeek = {'monday':[], 'tuesday':[], 'wednesday':[], 'thursday':[], 'friday':[]} #contains pks to exercises on their given days
            allMuscles = muscle.objects.all()
            for x in allMuscles:
                if any(t[0] == x.pk for t in muscleStatsArr):
                    pass
                else:
                    muscleStatsArr.append([x.pk, x.muscleName, 0, "indeterminate"])

            exerciseCounter = {}

            print "LENGTH OF ROUTINE =", len(muscleStatsArr)
            mondayTuple = generateMondayRoutine2(muscleStatsArr[:5], exerciseCounter, 1)
            routineWeek['monday'] = mondayTuple[0]
            exerciseCounter = mondayTuple[1]
            print "Monday routine =", routineWeek['monday']

            tuesdayTuple = generateMondayRoutine2(muscleStatsArr[5:10], exerciseCounter, 2)
            routineWeek['tuesday'] = tuesdayTuple[0]
            exerciseCounter = tuesdayTuple[1]
            print "Tuesday routine =", routineWeek['tuesday']

            wednesdayTuple = generateMondayRoutine2(muscleStatsArr[10:15], exerciseCounter, 3)
            routineWeek['wednesday'] = wednesdayTuple[0]
            exerciseCounter = wednesdayTuple[1]
            print "Wednesday routine - ", routineWeek['wednesday']

            thursdayTuple = generateMondayRoutine2(muscleStatsArr[:7], exerciseCounter, 4)
            routineWeek['thursday'] = thursdayTuple[0]
            exerciseCounter = thursdayTuple[1]
            print "Thursday routine - ", routineWeek['thursday']

            fridayTuple = generateMondayRoutine2(muscleStatsArr[7:10] + muscleStatsArr[15:18], exerciseCounter, 5)
            routineWeek['friday'] = fridayTuple[0]
            exerciseCounter = fridayTuple[1]
            print "Friday routine = ", routineWeek['friday']
            """routineWeek['monday'] = generateMondayRoutine2(muscleStatsArr[:5], exerciseCounter)
            print "monday routine = ", routineWeek['monday']
            routineWeek['tuesday'] = generateMondayRoutine2(muscleStatsArr[5:10])
            print "tuesday routine = ", routineWeek['tuesday']
            routineWeek['wednesday'] = generateMondayRoutine2(muscleStatsArr[10:15])
            print "wed routine =", routineWeek['wednesday']
            routineWeek['thursday'] = generateMondayRoutine2(muscleStatsArr[:5])
            print "thurs routine =", routineWeek['thursday']
            routineWeek['friday'] = generateMondayRoutine2(muscleStatsArr[5:10])
            print "fri routine = ", routineWeek['friday']"""

            for x in routineWeek:
                for y in routineWeek[x]:
                    exerciseAdd = exercise.objects.get(pk=y[1])
                    newExercise = generatedRoutineExercise(entryForm=newlyCreated, exerciseActual=exerciseAdd, sets= y[2], reps = y[3], notes = y[4], routineDay = x)
                    newExercise.save()

            json_stuff = json.dumps({"routineMonday" : routineWeek['monday'], "routineTuesday" : routineWeek['tuesday'], "routineWednesday" : routineWeek['wednesday'], "routineThursday" : routineWeek['thursday'], "routineFriday" : routineWeek['friday']})
            #print "inbetween"
            return HttpResponse(json_stuff, content_type ="application/json")
        except:
            #print "inside except"
            return HttpResponse("Error in except")
    print "DONE WITH ALL OF IT"

def endFile(request):
    print "end"
    return "end"