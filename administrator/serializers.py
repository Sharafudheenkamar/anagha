from rest_framework import serializers
from .models import *


class LoginTableserializer(serializers.ModelSerializer):
    class Meta:
        model = LoginTable
        fields = ['name','password','usertype','status']

class VoterTableserializer(serializers.ModelSerializer):
    class Meta:
        model = VoterTable
        fields = ['voter_id','login_id','name','email','department','voter_status','otp','known_face_encoding']

class CandidateTableserializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateTable
        fields = ['candidate_id','name','post','party','candidate_id']

class CoordinatorTableserializer(serializers.ModelSerializer):
    class Meta:
        model = CoordinatorTable
        fields = ['login_id','name','email','number','otp','created_at']

class ResultTableserializer(serializers.ModelSerializer):
    class Meta:
        model = ResultTable
        fields = ['voter_id','candidate_id','post','count']

class Voteserializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['voter_id','voter','candidate','timestamp','previous_hash','vote_hash']







