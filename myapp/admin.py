from .models import Stats2, compoundExercises, exercise, routine, exerciseForRoutine, exerciseCompare2, muscle, muscleGroupMajor, muscleGroupMinor, auxExercise, routineEntry, generatedRoutineExercise, muscleStats
from django.contrib import admin

admin.site.register(routineEntry)
admin.site.register(generatedRoutineExercise)
admin.site.register(muscleStats)
admin.site.register(Stats2)
admin.site.register(exercise)
admin.site.register(auxExercise)
admin.site.register(routine)
admin.site.register(exerciseForRoutine)
admin.site.register(exerciseCompare2)
admin.site.register(muscle)
admin.site.register(muscleGroupMajor)
admin.site.register(muscleGroupMinor)

admin.site.register(compoundExercises)