from __future__ import unicode_literals

from django.db import models

from django.db import models
import datetime
from django.contrib.auth.models import User
#from django.utils import timezone


#new stuff
class compoundExercises(models.Model):
    exerciseName = models.CharField(max_length=30)

    def __unicode__(self):
        return self.exerciseName
#end new

# Create your models here.
class Stats(models.Model):
    BenchWeight = models.IntegerField(max_length=10)
    BenchReps = models.IntegerField(max_length=10)
    SquatWeight = models.IntegerField(max_length=10)
    SquatReps = models.IntegerField(max_length=10)
    DeadWeight = models.IntegerField(max_length=10)
    DeadReps = models.IntegerField(max_length=10)
    PullupWeight = models.IntegerField(max_length=10)
    PullupReps = models.IntegerField(max_length=10)

class exercise(models.Model):
    exerciseName = models.CharField(max_length=30)
    author = models.ForeignKey(User, null=True, blank=True)
    def __unicode__(self):
        return self.exerciseName

class auxExercise(models.Model):
    exerciseActual = models.ForeignKey(exercise)
    isCompound = models.BooleanField()
    def __unicode__(self):
        return self.exerciseActual.exerciseName
#new

class muscle(models.Model):
    muscleName = models.CharField(max_length=30)
    def __unicode__(self):
        return self.muscleName

class routineEntry(models.Model): #contains (indirectly) muscleStats and the generated routine
    author = models.ForeignKey(User, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    def __unicode__(self):
        return str(self.pk)


DAY_CHOICES = (
    ('monday', 'monday'),
    ('tuesday', 'tuesday'),
    ('wednesday', 'wednesday'),
    ('thursday', 'thursday'),
    ('friday', 'friday'),
)
class generatedRoutineExercise(models.Model):
    entryForm = models.ForeignKey(routineEntry)
    exerciseActual = models.ForeignKey(exercise)
    sets = models.IntegerField(max_length=3)
    reps = models.IntegerField(max_length=3)
    notes = models.CharField(max_length=75)
    routineDay = models.CharField(max_length=6, choices=DAY_CHOICES, default='monday')
    def __unicode__(self):
        return self.routineDay + " - " + self.exerciseActual.exerciseName

class muscleStats(models.Model):
    muscleActual = models.ForeignKey(muscle)
    muscleStrength = models.FloatField(max_length=10)
    muscleScore = models.CharField(max_length=30)
    entryForm = models.ForeignKey(routineEntry)

class exerciseCompare2(models.Model):
    exerciseActual = models.ForeignKey(exercise)
    genderMale = models.BooleanField()
    bodyWeight = models.IntegerField(max_length=10)
    beginner = models.IntegerField(max_length=10)
    novice = models.IntegerField(max_length=10)
    intermediate = models.IntegerField(max_length=10)
    advanced = models.IntegerField(max_length=10)
    elite = models.IntegerField(max_length=10)
    def __unicode__(self):
        return self.exerciseActual.exerciseName + " - {}".format(self.genderMale) + " - {}".format(self.bodyWeight)

class muscleGroupMajor(models.Model):
    exerciseActual = models.ForeignKey(exercise)
    muscleActual = models.ForeignKey(muscle)
    def __unicode__(self):
        return self.exerciseActual.exerciseName + " - " + self.muscleActual.muscleName

class muscleGroupMinor(models.Model):
    exerciseActual = models.ForeignKey(exercise)
    muscleActual = models.ForeignKey(muscle)
    def __unicode__(self):
        return self.exerciseActual.exerciseName + " - " + self.muscleActual.muscleName

    #routine Generator
    #class routineType(models.Model):
    #routineName = models.CharField(max_length=30)
    #upVote = models.IntegerField(max_length=10)
    #downVote = models.IntegerField(max_length=10)
    #date = models.DateTimeField(auto_now_add=True, blank=True)
    #number of compound/isolation lifts
    #emphasis on certain muscle(groups?)
    #emphasis on volume (sets/reps)
    #How many days per week to lift  (MWF? 5 days? 7 days?)
    #How much cardio
    #how much rest per set


#EndNew
class Stats2(models.Model):
    BenchWeight = models.IntegerField(max_length=10)
    BenchReps = models.IntegerField(max_length=10)
    SquatWeight = models.IntegerField(max_length=10)
    SquatReps = models.IntegerField(max_length=10)
    DeadWeight = models.IntegerField(max_length=10)
    DeadReps = models.IntegerField(max_length=10)
    PullupWeight = models.IntegerField(max_length=10)
    PullupReps = models.IntegerField(max_length=10)
    author = models.ForeignKey(User, null=True, blank=True)



class routine(models.Model):
    routineName = models.CharField(max_length=50)
    author = models.ForeignKey(User, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    upVote = models.IntegerField(max_length=10)
    downVote = models.IntegerField(max_length=10)
    def __unicode__(self):
        return self.routineName

class exerciseForRoutine(models.Model):
    exerciseName = models.ForeignKey(exercise)
    actualRoutine = models.ForeignKey(routine)
    exerciseSets = models.IntegerField(max_length=10)
    exerciseReps = models.IntegerField(max_length=10)
    exerciseFrequency = models.IntegerField(max_length=10)
    beginner = models.IntegerField(max_length=10)
    novice = models.IntegerField(max_length=10)
    intermediate = models.IntegerField(max_length=10)
    advanced = models.IntegerField(max_length=10)
    elite = models.IntegerField(max_length=10)
    def __unicode__(self):
        return self.exerciseName.exerciseName  + " - " + self.actualRoutine.routineName

# Create your models here.
