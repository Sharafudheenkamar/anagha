from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(LoginTable)
admin.site.register(ResultTable)
admin.site.register(VoterTable)
admin.site.register(CandidateTable)
admin.site.register(CoordinatorTable)
admin.site.register(Vote)