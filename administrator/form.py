from django.forms import ModelForm
from administrator.models import CandidateTable,CoordinatorTable, VoterTable


class CandidateForm(ModelForm):
    class Meta:
        model=CandidateTable
        fields=[
            'name',
            'post',
            'party',
            'candidate_id'
            
        ]
        
class CoordinatorForm(ModelForm):
    class Meta:
        model= CoordinatorTable
        fields=[
            'name',
            'email',
            'number',
            'otp'   
        ]
 
class OrganizorForm(ModelForm):
    class meta:
        model = CoordinatorTable
        fields=[
            'name',
            'email',
            'password',
            'number'
            
            
        ]            
    
class VoterTableform(ModelForm):
    class Meta:
        model=VoterTable
        exclude=['login_id','department','voter_status']

class Voterform(ModelForm):
    class Meta:
        model = VoterTable
        fields=['name','email']   