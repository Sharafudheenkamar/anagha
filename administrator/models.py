from django.db import models

# Create your models here.
from django.utils.timezone import now
from datetime import timedelta
import hashlib
from django.utils.crypto import get_random_string

# Create your models here.
class LoginTable(models.Model):
    name = models.CharField(max_length=30,null=True,blank=True)
    password = models.CharField(max_length=30,null=True,blank=True)
    usertype = models.CharField(max_length=30,null=True,blank=True)
    status=models.CharField(max_length=30,null=True,blank=True)
   
    

    
class VoterTable(models.Model):
    voter_id = models.CharField(max_length=100, unique=True, editable=False,null=True,blank=True)
    login_id = models.ForeignKey(LoginTable,on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=30,null=True,blank=True)
    email = models.CharField(max_length=30,null=True,blank=True)
    department = models.CharField(max_length=30,null=True,blank=True)
    voter_status = models.BooleanField(default=False)
    otp=models.CharField(max_length=30,null=True,blank=True)
    known_face_encoding= models.FileField(null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.voter_id:
            self.voter_id = get_random_string(length=12)  # Generate unique ID
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.id} ({self.email})"

class CandidateTable(models.Model):
    candidate_id = models.CharField(max_length=100, unique=True, editable=False,null=True,blank=True)
    name = models.CharField(max_length=30,null=True,blank=True)
    candidate_image=models.FileField(upload_to='candidate_image',null=True,blank=True)
    post = models.CharField(max_length=30,null=True,blank=True)
    party = models.CharField(max_length=30,null=True,blank=True)
    candidate_id = models.CharField(max_length=30,null=True,blank=True)
    def save(self, *args, **kwargs):
        if not self.candidate_id:
            self.candidate_id = get_random_string(length=12)  # Generate unique ID
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.party})"
    
from django.db import models
from django.utils.timezone import now

class CoordinatorTable(models.Model):
    login_id = models.ForeignKey(LoginTable, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    email = models.CharField(max_length=30, null=True, blank=True)
    number = models.CharField(max_length=30, null=True, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(default=now)  # Set default to `now()`

    def is_valid(self):
        """Check if the OTP is valid (not older than 5 minutes)."""
        return now() <= self.created_at + timedelta(minutes=5)

       
    
class ResultTable(models.Model):
    voter_id = models.ForeignKey(VoterTable,on_delete=models.CASCADE,null=True,blank=True)
    candidate_id = models.ForeignKey(CandidateTable,on_delete=models.CASCADE,null=True,blank=True)
    post= models.CharField(max_length=30,null=True,blank=True)
    count= models.CharField(max_length=30,null=True,blank=True)


  

import hashlib


class Vote(models.Model):
    vote_id = models.CharField(max_length=100, unique=True, editable=False)
    voter = models.OneToOneField(VoterTable, on_delete=models.CASCADE)  # Prevent multiple votes
    candidate = models.ForeignKey(CandidateTable, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    previous_hash = models.CharField(max_length=64, blank=True, null=True)  # Link to previous vote
    vote_hash = models.CharField(max_length=64, blank=True, editable=False)  # Current vote's hash

    def save(self, *args, **kwargs):
        # Generate vote ID
        if not self.vote_id:
            self.vote_id = get_random_string(length=16)
        
        # Generate hash of the current vote
        vote_data = f"{self.vote_id}{self.voter.voter_id}{self.candidate.candidate_id}{self.timestamp}"
        self.vote_hash = hashlib.sha256(vote_data.encode()).hexdigest()

        # Assign the previous hash
        if not self.previous_hash:
            last_vote = Vote.objects.order_by('-timestamp').first()
            self.previous_hash = last_vote.vote_hash if last_vote else None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Vote by {self.voter.name} for {self.candidate.name}"