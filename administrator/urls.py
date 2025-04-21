from django.urls import path
from .views import *

urlpatterns = [
    path('ApproveVoters/',ApproveVoters.as_view(),name='Approvevoters'),
  
    path('',Index.as_view(),name='Index'),
    path('logout/',logout.as_view(),name='logout'),
    # path('OrgSignUp/',OrgSignUp.as_view(),name='OrgSignUp'),
    path('Register',Register.as_view(),name="Register"),#organiser registration
    path('MainSign/',MainSign.as_view(),name='MainSign'),#voterregistration
    path('OTP/',VerifyOTP.as_view(),name='OTP'),
    path('OTPvoter/',VerifyOTPvoter.as_view(),name='OTPvoter'),
    path('Result/',Result.as_view(),name='Result'),
    path('SignIn/',SignIn.as_view(),name='SignIn'),
    path('SignUp/',SignUp.as_view(),name='SignUp'),
    path('Verified/',Verified.as_view(),name='Verified'),
    path('View_voters_List/',View_voters_List.as_view(),name='View_voters_List'),
    path('VoterSignUp/',VoterSignUp.as_view(),name='VoterSignUp'),
    path('Voting_Panel/',Voting_Panel.as_view(),name='Voting_Panel'),
    path('AdminDashboard/',AdminDashboard.as_view(),name='AdminDashboard'),
    path('UserProfile/',UserProfile.as_view(),name='UserProfile'),
    path('Coordinator/',Coordinator.as_view(),name='Coordinator'),
    path('MyAccount/',MyAccount.as_view(),name='MyAccount'),
    path('Candidates/',Candidates.as_view(),name='Candidates'),
    path('Candidatesvoter/',Candidatesvoter.as_view(),name='Candidatesvoter'),
    path('Result/',Result.as_view(),name='Result'),
    path('Voting/',Voting.as_view(),name='Voting'),
    path('Addcand/',Addcand.as_view(),name='Addcand'),
    path('VoterList/',VoterList.as_view(),name='VoterList'),
    path('delete_voter/<int:c_id>',delete_voter.as_view(),name='delete_voter'),
    path('ApproveVoters/',ApproveVoters.as_view(),name='ApproveVoters'),
    path('ManageCandidates/',ManageCandidates.as_view(),name='ManageCandidates'),
    path('Edit_candidate/<int:id>/',Edit_candidate.as_view(),name='Edit_candidate'),
    path('DeleteCandidate/<int:id>/',DeleteCandidate.as_view(),name='DeleteCandidate'),
    path('AddCordinator/',AddCordinator.as_view(),name='AddCordinator'),
    path('Cordinatorlist/',Cordinatorlist.as_view(),name='Cordinatorlist'),
    path('CandidateList/',CandidateList.as_view(),name='CandidateList'),
    path('monitor_camera/<int:id>',Monitor_camera1.as_view(),name='Monitor_camera'),
    path('alreadyvote',alreadyvote.as_view(),name='alreadyvote'),
     
    
    
    path('api/login/', MainSignAPIView.as_view(), name='api-login'),
    path('api/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('api/orgsignup/', OrgSignUpAPIView.as_view(), name='api-orgsignup'),
    path('api/otp/', OTPAPIView.as_view(), name='api-otp'),
    path('api/result/', ResultAPIView.as_view(), name='api-result'),
    path('api/signin/', SignInAPIView.as_view(), name='api-signin'),
    path('api/signup/', SignUpAPIView.as_view(), name='api-signup'),
    path('api/verified/', VerifiedAPIView.as_view(), name='api-verified'),
    path('api/view_voters_list/', ViewVotersListAPIView.as_view(), name='api-view-voters-list'),
    path('api/voter_signup/', VoterSignUpAPIView.as_view(), name='api-voter-signup'),
    path('api/delete_voter/<int:voter_id>/', DeleteVoterAPIView.as_view(), name='api-delete-voter'),
    path('api/voting_panel/', VotingPanelAPIView.as_view(), name='api-voting-panel'),
    path('api/user_profile/<int:id>', UserProfileAPIView.as_view(), name='api-user-profile'),
    path('api/coordinator/', CoordinatorAPIView.as_view(), name='api-coordinator'),
    path('api/my_account/', MyAccountAPIView.as_view(), name='api-my-account'),
    path('api/voting/', VotingAPIView.as_view(), name='api-voting'),
    path('api/add_candidate/', AddCandidateAPIView.as_view(), name='api-add-candidate'),
    path('api/voter_list/', VoterListAPIView.as_view(), name='api-voter-list'),
    path('api/approve_voters/', ApproveVotersAPIView.as_view(), name='api-approve-voters'),
    path('api/admin_dashboard/', AdminDashboardAPIView.as_view(), name='api-admin-dashboard'),
    path('api/manage_candidates/', ManageCandidatesAPIView.as_view(), name='api-manage-candidates'),
    path('api/edit_candidate/<int:id>/', EditCandidateAPIView.as_view(), name='api-edit-candidate'),
    path('api/delete_candidate/<int:id>/', DeleteCandidateAPIView.as_view(), name='api-delete-candidate'),
    path('api/add_coordinator/', AddCoordinatorAPIView.as_view(), name='api-add-coordinator'),
    path('api/coordinator_list/', CoordinatorListAPIView.as_view(), name='api-coordinator-list'),
    path('api/candidate_list/', CandidateListAPIView.as_view(), name='api-candidate-list'),
    path('api/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/verify_otp/', VerifyOTPAPIView.as_view(), name='api-verify-otp'),
    path('api/verify_otp_voter/', VerifyOTPVoterAPIView.as_view(), name='api-verify-otp-voter'),
    path('api/monitor_camera/<int:id>/', MonitorCameraAPIView.as_view(), name='api-monitor-camera'),
    path('api/already_voted/', AlreadyVotedAPIView.as_view(), name='api-already-voted'),
]

    
    
    
    
