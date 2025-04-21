import datetime
import pickle

from django.http import HttpResponse,StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views import View

from administrator.models import LoginTable,VoterTable,CandidateTable,ResultTable,CoordinatorTable
from administrator.form import CandidateForm,CoordinatorForm,OrganizorForm, VoterTableform, Voterform
from django.shortcuts import render, redirect
from django.views import View
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import os
from django.conf import settings
import shutil
import cv2
import face_recognition
import numpy as np
from rest_framework.views import APIView
from rest_framework import status
import random
from .serializers import *

# Create your views here.

class Candidates(View):
    def get(self,request):
        obj=CandidateTable.objects.all()
        print(obj)
        return render(request,'Votte/candidateslist.html',{'obj':obj})
    
class Candidatesvoter(View):
    def get(self,request):
        obj=CandidateTable.objects.all()
        print(obj)
        return render(request,'Votte/candidateslistvoter.html',{'obj':obj})
    
class Index(View):
    def get(self,request):
        return render(request,'Votte/index.html')
        
        
        
class MainSign(View):
    def get(self,request):
        return render(request, 'Votte/mainSign.html') 
    def post(self, request):
        try:
            email = request.POST['email']
            password = request.POST['password']
            
            # Try to get the user from the LoginTable
            obj = LoginTable.objects.get(name=email, password=password)
            print(obj.usertype)
            print(obj)
            
            # Store the user ID in the session
            request.session["id"] = obj.id
            
            # Redirect based on user type
            if obj.usertype == 'admin':
                return render(request, "Votte/admin_dashboard.html")
            elif obj.usertype == 'voter':
                id = request.session["id"]
                print(id)
                obj = VoterTable.objects.get(login_id=id)
                print(obj)
                return render(request, "Votte/myacc.html", {'val': obj})
            elif obj.usertype == 'organizer':
                id = request.session["id"]
                print(id)
                obj = CoordinatorTable.objects.get(login_id__id=id)
                print(obj)
                return render(request, "Votte/cordinatorhome.html", {'val': obj})
            else:
                return HttpResponse('''<script>alert("Sorry! Invalid user type.");window.location="/"</script>''')
        except LoginTable.DoesNotExist:
            # If the user does not exist in LoginTable
            return HttpResponse('''<script>alert("Sorry! Invalid username or password.");window.location="/"</script>''')
        except Exception as e:
            # Catch any other exceptions for debugging
            print(f"An error occurred: {e}")
            return HttpResponse('''<script>alert("An unexpected error occurred. Please try again later.");window.location="/"</script>''')        
class logout(View):
    def get(self,request):
        request.session.flush()
        return redirect('Index')
    
class OrgSignUp(View):
    def get(self,request):
        return render(request,'Votte/orgsignup.html')
    def post(self,request):
        form = OrganizorForm(request.POST)
        print("post")
        if form.is_valid():
            reg_form = form.save(commit=False)
            rf=LoginTable.objects.create_user(user_type='organizor',name =request.POST['email'],password=request.POST['password'])
            reg_form.login_id=rf
            rf.save()
            reg_form.save()
            return HttpResponse('''<script>alert("successfully added.");window.location="/OrgSignUp/"</script>''')
        return HttpResponse('''<script>alert("Sorry! User failed to add.");window.location="/OrgSignUp/"</script>''')
        

class OTP(View):
    def get(self,request):
        return render(request,'Votte/otp.html')    
from django.db.models import Count
class Result(View):
    def get(self,request):
       current_time = datetime.datetime.now()
       obj=CandidateTable.objects.annotate(vote_count=Count('vote')).order_by('-vote_count')
       return render(request,'Votte/result.html',{'obj':obj,'current_time':current_time})      

class SignIn(View):
    def get(self,request):
        return render(request,'Votte/signIn.html')      
    

class SignUp(View):
    def get(self,request):
        return render(request,'Votte/signup.html')  
 

class Verified(View):
    def get(self,request):
        return render(request,'Votte/verified.html')      
    

class View_voters_List(View):
    def get(self,request):
        obj=VoterTable.objects.all()
        return render(request,'Votte/view_voter_list.html',{'obj':obj})                          


class VoterSignUp(View):
    def get(self,request):
        return render(request,'Votte/voterSignUp.html') 
    def post(self, request):
            # Get form inputs
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            number = request.POST.get('number')
                # Check if the email or username already exists in LoginTable or VoterTable
            if LoginTable.objects.filter(name=email).exists():
                messages.error(request, 'Email already exists. Please use a different email address.')
                return HttpResponse('''<script>alert("Sorry!email already exist.");window.location="/VoterSignUp/"</script>''')
        
                

            if VoterTable.objects.filter(email=email).exists():
                messages.error(request, 'Username already exists. Please choose a different username.')
                return HttpResponse('''<script>alert("Sorry!email already exist.");window.location="/VoterSignUp/"</script>''')
        
            form = Voterform(request.POST, request.FILES)
            if form.is_valid():
                request.session['email'] = email

                if email:
                    # Step 1: Save email and password to LoginTable
                    login_record = LoginTable.objects.create(
                    name=email,
                    password=password,
                    usertype='voter'  # Assuming usertype is 'organizer' for this case
                )
                person_instance = form.save(commit=False)

                # Create a unique directory for each criminal
                person_dir = os.path.join(settings.MEDIA_ROOT, 'known_images', person_instance.name)
                os.makedirs(person_dir, exist_ok=True)

                # Save uploaded image to the specified directory
                image_file = request.FILES['photo']
                image_path = os.path.join(person_dir, image_file.name)
                
                # Saving the image file
                with open(image_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
                
                # Save the path of the image file in the model instance and update known_faces.txt
                person_instance.known_face_encoding.name = os.path.join('known_images', person_instance.name, image_file.name)
                otp = generate_otp()
                # Save the instance to the database
                person_instance.login_id=login_record
                person_instance.otp=otp
                person_instance.save()

                # Update the known_faces.txt file with the criminal's name
                known_faces_path = os.path.join(settings.MEDIA_ROOT, 'known_faces.txt')
                with open(known_faces_path, 'a') as f:
                    f.write(f"{person_instance.name}\n")

                               # Step 3: Send OTP via email
                send_mail(
                    'Your OTP for Registration',
                    f'Your OTP is: {otp}\nIt is valid for 5 minutes.',
                    'anaghapeethan@gmail.com',  # Replace with your email
                    [email],
                )

                # Step 4: Provide feedback to the user
                messages.success(request, f'OTP sent to {email}.')
                return redirect('OTPvoter')  

                # return HttpResponse('''<script>alert("Image uploaded successfully"); window.location="/view_criminal"</script>''')


            # Store email in session




 # Redirect to OTP verification page

            else:
                messages.error(request, 'Please provide a valid email address.')

            return render(request, "Votte/voterSignUp.html")         

 
class delete_voter(View):
    def get(self, request, c_id):
        # Retrieve the criminal record by ID
        criminal_instance = get_object_or_404(VoterTable, id=c_id)
        

        
        # Path to the criminal's image directory
        person_dir = os.path.join(settings.MEDIA_ROOT, 'known_images', criminal_instance.name)

        # Move the image to a recycle bin or delete
        if os.path.exists(person_dir):
            # Ensure `recycle_bin` folder exists
            recycle_bin_dir = os.path.join(settings.MEDIA_ROOT, 'recycle_bin')
            os.makedirs(recycle_bin_dir, exist_ok=True)

            # Move entire person directory to recycle bin
            shutil.move(person_dir, recycle_bin_dir)

        # Remove the criminal's name from `known_faces.txt`
        known_faces_path = os.path.join(settings.MEDIA_ROOT, 'known_faces.txt')
        with open(known_faces_path, 'r') as f:
            lines = f.readlines()
        
        # Rewrite file without the deleted criminal's name
        with open(known_faces_path, 'w') as f:
            for line in lines:
                if line.strip() != criminal_instance.name:
                    f.write(line)
        login_instance=LoginTable.objects.filter(id=criminal_instance.login_id.id).first()
        login_instance.delete()
        # Delete the database record
        # criminal_instance.delete()

        return HttpResponse('''<script>alert("voter deleted successfully"); window.location="/VoterList/"</script>''')

class Voting_Panel(View):
    def get(self,request):
        return render(request,'Votte/voting_panel.html')
                
    

class UserProfile(View):
    def get(self,request):
        return render(request,'Votte/user.html')
    
class Coordinator(View):
    def get(self,request):
        profile_instance=CoordinatorTable.objects.filter(login_id__id=request.session["id"])
        return render(request,'Votte/cordinatorhome.html',{'profile_instance':profile_instance})
    
class MyAccount(View):
    def get(self,request):

       
        
        
        return render(request,'Votte/myacc.html')        


    

class Voting(View):
    def get(self,request):
        can_inst=CandidateTable.objects.all()
        print(can_inst)

        return render(request,'Votte/voting.html',{'can_inst':can_inst})
    def post(self, request, *args, **kwargs):

    
        candidate_id = request.POST.get('candidate_id')

        # Validate voter
        try:
            voter = VoterTable.objects.get(login_id__id=request.session['id'])  # Ensure this is unique
        except VoterTable.DoesNotExist:
            return JsonResponse({'error': 'Voter not found!'}, status=404)

        # Check if the voter has already voted
        if voter.voter_status:
            return JsonResponse({'error': 'You have already voted!'}, status=400)

        # Validate candidate
        try:
            candidate = CandidateTable.objects.get(id=candidate_id)  # Ensure this is unique
        except CandidateTable.DoesNotExist:
            return JsonResponse({'error': 'Candidate not found!'}, status=404)

        # Record the vote
        vote = Vote.objects.create(voter=voter, candidate=candidate)
        voter.voter_status = True  # Mark voter as having voted
        voter.save()
        send_mail(
                'You have casted your vote sucessfully',
                f'You have casted your vote sucessfully',
                'anaghapeethan@gmail.com',  # Replace with your email
                [voter.email],
            )

        # return JsonResponse({'message': 'Vote cast successfully!', 'vote_hash': vote.vote_hash})
        return redirect('alreadyvote')

class Addcand(View):
    def get(self,request):
        return render(request,'Votte/addcand.html')
    def post(self,request):
        form=CandidateForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponse('''<script>alert("successfully added");window.location="/Addcand/"</script>''')
    
class VoterList(View):
      def get(self,request):
         obj=VoterTable.objects.all()
         return render(request,'Votte/voterList.html',{'obj':obj})
      
class ApproveVoters(View):
      def get(self,request):
       obj=VoterTable.objects.all()
       return render(request,'Votte/approveVoters.html',{'obj':obj})

      
class AdminDashboard(View):
      def get(self,request):
        return render(request,'Votte/adminDashboard.html')

      
class ManageCandidates(View):
      def get(self,request):
        obj=CandidateTable.objects.all()
        return render(request,'Votte/managecandidate.html',{'val':obj}) 
      
class Edit_candidate(View):
      def get(self,request,id):
        obj=CandidateTable.objects.get(id=id)
        return render(request,'Votte/editcand.html',{'val':obj})  
      def post(self,request,id):
        obj=CandidateTable.objects.get(id=id)
        form=CandidateForm(request.POST,instance=obj)
        if form.is_valid():
            form.save()
        return HttpResponse('''<script>alert("successfully Updated");window.location="/Addcand/"</script>''')
      
class DeleteCandidate(View):
      def get(self,request,id):
        obj=CandidateTable.objects.get(id=id)
        obj.delete()
        return HttpResponse('''<script>alert("successfully deleted");window.location="/ManageCandidates"</script>''')
    

      
class AddCordinator(View):
    def get(self,request):
        return render(request,'Votte/addcordinator.html')
    def post(self,request):
        form=CoordinatorForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponse('''<script>alert("successfully added");window.location="/AddCordinator/"</script>''')     
    
      
class Cordinatorlist(View):
      def get(self,request):
        obj=CoordinatorTable.objects.all()
        return render(request,'Votte/coordinatorlist.html',{'obj':obj})     
      
class CandidateList(View):
   def get(self,request):
        obj=CandidateTable.objects.all()
        return render(request,'Votte/candidateslist.html',{'obj':obj})  


from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.views import View
from datetime import timedelta
from django.utils.timezone import now
import random
import time


def generate_otp():
    """Generate a 4-digit OTP."""
    return str(random.randint(1000, 9999)) 


class Register(View):
    def get(self, request):
        return render(request, "Votte/orgsignup.html")

    def post(self, request):
        # Get form inputs
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        number = request.POST.get('number')

        # Store email in session
        request.session['email'] = email

        if email:
            # Step 1: Save email and password to LoginTable
            login_record = LoginTable.objects.create(
                name=email,
                password=password,
                usertype='organizer'  # Assuming usertype is 'organizer' for this case
            )

            # Step 2: Generate OTP and save it to CoordinatorTable
            otp = generate_otp()
            CoordinatorTable.objects.create(
                login_id=login_record,  # Link to the LoginTable record
                name=name,
                email=email,
                number=number,
                otp=otp,
               
            )

            # # Step 3: Send OTP via email
            # send_mail(
            #     'Your OTP for Registration',
            #     f'Your OTP is: {otp}\nIt is valid for 5 minutes.',
            #     'anaghapeethan@gmail.com',  # Replace with your email
            #     [email],
            # )

            # Step 4: Provide feedback to the user
            messages.success(request, f'OTP sent to {email}.')
            return redirect('OTP')  # Redirect to OTP verification page

        else:
            messages.error(request, 'Please provide a valid email address.')

        return render(request, "Votte/orgsignup.html")


    

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import CoordinatorTable, Vote
from django.core.exceptions import ObjectDoesNotExist

class VerifyOTP(View):
    def get(self, request):
        # Ensure that the email exists in the session
        if 'email' not in request.session:
            messages.error(request, 'Session expired. Please start the registration process again.')
            return redirect('Register')  # Redirect to registration page
        
        email = request.session['email']
        return render(request, "Votte/otp.html", {'email': email})

    def post(self, request):
        # Ensure that the email exists in the session
        if 'email' not in request.session:
            messages.error(request, 'Session expired. Please start the registration process again.')
            return redirect('Register')  # Redirect to registration page
        
        email = request.session['email']
        otp = request.POST.get('otp')

        try:
            # Fetch the Coordinator record based on the email
            otp_record = CoordinatorTable.objects.get(email=email)
            if otp_record.otp:
             print("OTP is verified")
            else:
             print("OTP is not verified")
        except ObjectDoesNotExist:
            messages.error(request, 'No registration record found for this email.')
            return render(request, "votte/otp.html", {'email': email})

        # Validate OTP and check its expiration
        if otp_record.otp == otp and otp_record.is_valid():
            
            messages.success(request, 'OTP verified successfully! Registration complete.')
            return HttpResponse('''<script>alert("otp verified");window.location="/"</script>''')   
        else:
             return HttpResponse('''<script>alert("otp incorrect");window.location="/Register"</script>''')
            
        
        return render(request, "votte/otp.html", {'email': email})
class VerifyOTPvoter(View):
    def get(self, request):
        # Ensure that the email exists in the session
        if 'email' not in request.session:
            messages.error(request, 'Session expired. Please start the registration process again.')
            return redirect('Register')  # Redirect to registration page
        
        email = request.session['email']
        return render(request, "Votte/otpvoter.html", {'email': email})

    def post(self, request):
        # Ensure that the email exists in the session
        if 'email' not in request.session:
            messages.error(request, 'Session expired. Please start the registration process again.')
            return redirect('Register')  # Redirect to registration page
        
        email = request.session['email']
        otp = request.POST.get('otp')

        try:
            # Fetch the Coordinator record based on the email
            otp_record = VoterTable.objects.get(email=email)
            if otp_record.otp:
             print("OTP is verified")
            else:
             print("OTP is not verified")
        except ObjectDoesNotExist:
            messages.error(request, 'No registration record found for this email.')
            return render(request, "votte/otpvoter.html", {'email': email})

        # Validate OTP and check its expiration
        if otp_record.otp == otp:
            
            messages.success(request, 'OTP verified successfully! Registration complete.')
            return HttpResponse('''<script>alert("otp verified login again");window.location="/"</script>''')   
        else:
             return HttpResponse('''<script>alert("otp incorrect");window.location="/OTPvoter/"</script>''')
            
        
        return render(request, "votte/otp.html", {'email': email})

# # Load YOLO model
# yolo_net = cv2.dnn.readNet("/home/sharafu/Desktop/djangoprojects/repositorypatrolwatch-main/yolov3.weights", "/home/sharafu/Desktop/djangoprojects/repositorypatrolwatch-main/yolov3.cfg")
# layer_names = yolo_net.getLayerNames()
# output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]
# with open("coco.names", "r") as f:
#     classes = [line.strip() for line in f.readlines()]

class Monitor_camera1(View):
    def get(self, request, id):
        vote_inst = Vote.objects.filter(voter__id=id).first()
        if vote_inst:
            return redirect('alreadyvote')
        else:
            print("Camera started")

            try:
                # Query the specific voter using the passed voter ID
                voter = VoterTable.objects.get(id=id)
                if not voter.known_face_encoding:
                    return JsonResponse({"error": "No face encoding file for this voter."}, status=400)

                # Load the image and extract the face encoding
                face_image_path = voter.known_face_encoding.path
                print("File exists:", face_image_path)
                voter_image = face_recognition.load_image_file(face_image_path)
                known_face_encodings = face_recognition.face_encodings(voter_image)

                if len(known_face_encodings) == 0:
                    return JsonResponse({"error": "No face detected in the stored image."}, status=400)

                known_face_encoding = known_face_encodings[0]  # Use the first detected face
                known_face_names = [voter.name]
                print(f"Loaded encoding for voter: {voter.name}")

            except VoterTable.DoesNotExist:
                return JsonResponse({"error": "Voter not found."}, status=404)
            except Exception as e:
                print(f"Error processing face encoding: {e}")
                return JsonResponse({"error": "Error processing face encoding."}, status=500)

            cap = cv2.VideoCapture(0)  # Initialize the camera feed
            if not cap.isOpened():
                print("Error: Could not access the camera.")
                return JsonResponse({"error": "Could not access the camera"}, status=500)

            start_time = time.time()
            person_detected = False

            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to grab frame from the camera")
                        break

                    # Resize and convert frame for face recognition
                    frame = cv2.resize(frame, (1280, 720))
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Detect face locations and encodings
                    face_locations = face_recognition.face_locations(rgb_frame)
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                    for face_encoding in face_encodings:
                        matches = face_recognition.compare_faces([known_face_encoding], face_encoding)
                        if True in matches:
                            match_index = matches.index(True)
                            name = known_face_names[match_index]
                            print(f"Match found: {name}")
                            person_detected = True
                            break

                    # Draw rectangles around detected faces
                    for (top, right, bottom, left) in face_locations:
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                    # Show the video feed
                    cv2.imshow("Face Recognition", frame)

                    # Break the loop if person is detected or 30 seconds have elapsed
                    if person_detected or (time.time() - start_time > 30):
                        if not person_detected:
                            print("30 seconds elapsed")
                        break

                    # Exit on 'q' key press
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

            finally:
                # Cleanup camera and OpenCV windows
                cap.release()
                cv2.destroyAllWindows()

            # Navigation based on detection result
            if person_detected:
                return HttpResponse(
                    '''<script>alert("FACE VERIFIED");window.location="/Voting"</script>'''
                )
            else:
                return HttpResponse(
                    '''<script>alert("FACE NOT VERIFIED. CONTACT ADMIN.");window.location="/"</script>'''
                )
class alreadyvote(View):
    def get(self,request):
        return render(request,'Votte/already.html')            
    


from rest_framework.response import Response
from rest_framework import status
class MainSignAPIView(APIView):
    # def post(self, request):
        # email = request.data.get('email')
        # password = request.data.get('password')
        # try:
        #     obj = LoginTable.objects.get(name=email)
            
        #     # Check if the password matches (if hashed, use check_password)
        #     if obj.password != password:
        #         return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
            
        #     # Store user ID in session
        #     request.session["id"] = obj.id
            
        #     # Redirect based on user type
        #     if obj.usertype == 'admin':
        #         return Response({"message": "Login successful", "redirect": "/admin_dashboard"}, status=status.HTTP_200_OK)
        #     elif obj.usertype == 'voter':
        #         voter = get_object_or_404(VoterTable, login_id=obj.id)
        #         return Response({"message": "Login successful", "redirect": "/myacc", "data": {"name": voter.name, "id": voter.id}}, status=status.HTTP_200_OK)
        #     elif obj.usertype == 'organizer':
        #         coordinator = get_object_or_404(CoordinatorTable, login_id__id=obj.id)
        #         return Response({"message": "Login successful", "redirect": "/coordinatorhome", "data": {"name": coordinator.name, "id": coordinator.id}}, status=status.HTTP_200_OK)
        #     else:
        #         return Response({"error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST)
        # except LoginTable.DoesNotExist:
        #     return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        def post(self, request):
        
            response_dict = {}
            print("request data :-------------------> ", request.data)
            password = request.data.get("password")
            print("Password ------------------> ",password)
            username = request.data.get("email")
            print("Username ------------------> ",username)
            try:
                user = LoginTable.objects.filter(name=username, password=password).first()
                print("user_obj :-----------", user)
            except LoginTable.DoesNotExist:
                response_dict["message"] = "No account found for this username. Please signup."
                return Response(response_dict, status=status.HTTP_200_OK)
        
            if user.usertype == "voter":
                response_dict = {
                    "login_id": str(user.id),
                    "user_type": user.usertype,
                    "status": "success",
                }   
                print("User details :--------------> ",response_dict)
                return Response(response_dict, status=status.HTTP_200_OK)
            else:
                response_dict["message "] = "Your account has not been approved yet or you are a CLIENT user."
                return Response(response_dict, status=status.HTTP_200_OK)

class LogoutAPIView(APIView):
    def get(self, request):
        request.session.flush()
        return Response({"message": "Logout successful", "redirect": "/"}, status=status.HTTP_200_OK)
    
class OrgSignUpAPIView(APIView):
    def post(self, request):
        form = OrganizorForm(request.data)
        if form.is_valid():
            reg_form = form.save(commit=False)
            rf = LoginTable.objects.create_user(user_type='organizor', name=request.data['email'], password=request.data['password'])
            reg_form.login_id = rf
            rf.save()
            reg_form.save()
            return Response({"message": "Successfully added", "redirect": "/OrgSignUp/"}, status=status.HTTP_201_CREATED)
        return Response({"error": "User failed to add"}, status=status.HTTP_400_BAD_REQUEST)
    
class OTPAPIView(APIView):
    def get(self, request):
        return Response({"message": "OTP Page"}, status=status.HTTP_200_OK)

class ResultAPIView(APIView):
    def get(self, request):
        current_time = datetime.datetime.now()
        obj = CandidateTable.objects.annotate(vote_count=Count('vote')).order_by('-vote_count')
        results = [{"candidate": candidate.name, "vote_count": candidate.vote_count} for candidate in obj]
        return Response({"results": results, "current_time": current_time}, status=status.HTTP_200_OK)
    
class SignInAPIView(APIView):
    def get(self, request):
        return Response({"message": "Sign In Page"}, status=status.HTTP_200_OK)


class SignUpAPIView(APIView):
    def get(self, request):
        return Response({"message": "Sign Up Page"}, status=status.HTTP_200_OK)

        
        
    def post(self, request):
        print("###############", request.data)
        try:
            # Get form inputs
            name = request.data.get('name')
            email = request.data.get('email')
            password = request.data.get('password')
            number = request.data.get('number')

            # Validate required fields
            if not all([name, email, password]):
                return Response(
                    {"error": "Name, email, and password are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if email already exists in LoginTable
            if LoginTable.objects.filter(name=email).exists():
                return Response(
                    {"error": "Email already exists. Please use a different email address."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if email already exists in VoterTable
            if VoterTable.objects.filter(email=email).exists():
                return Response(
                    {"error": "Username already exists. Please choose a different username."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate form
            form = Voterform(request.data, request.FILES)
            if not form.is_valid():
                return Response(
                    {"error": "Invalid form data.", "details": form.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Step 1: Save email and password to LoginTable
            login_record = LoginTable.objects.create(
                name=email,
                password=password,  # Note: Consider hashing the password
                usertype='voter'
            )

            # Step 2: Prepare VoterTable instance
            person_instance = form.save(commit=False)

            # Create a unique directory for the voter
            person_dir = os.path.join(settings.MEDIA_ROOT, 'known_images', person_instance.name)
            os.makedirs(person_dir, exist_ok=True)

            # Save uploaded image
            image_file = request.data.get('photo')
            if not image_file:
                return Response(
                    {"error": "Photo is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            image_path = os.path.join(person_dir, image_file.name)
            with open(image_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # Save the image path in the model
            person_instance.known_face_encoding = os.path.join('known_images', person_instance.name, image_file.name)

            # Generate and save OTP
            otp = generate_otp()
            person_instance.login_id = login_record
            person_instance.otp = otp
            person_instance.save()

            # Update known_faces.txt
            known_faces_path = os.path.join(settings.MEDIA_ROOT, 'known_faces.txt')
            with open(known_faces_path, 'a') as f:
                f.write(f"{person_instance.name}\n")

            # Step 3: Send OTP via email
            try:
                send_mail(
                    'Your OTP for Registration',
                    f'Your OTP is: {otp}\nIt is valid for 5 minutes.',
                    'anaghapeethan@gmail.com',  # Replace with your email
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                # Delete the created records if email sending fails
                person_instance.delete()
                login_record.delete()
                return Response(
                    {"error": f"Failed to send OTP: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Step 4: Return success response
            return Response(
                {
                    "message": f"OTP sent to {email}.",
                    "next_url": "/OTPvoter/"  # Provide the URL for OTP verification
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class VerifiedAPIView(APIView):
    def get(self, request):
        return Response({"message": "Verified Page"}, status=status.HTTP_200_OK)

class ViewVotersListAPIView(APIView):
    def get(self, request):
        obj = VoterTable.objects.all()
        voters = [{"id": voter.id, "name": voter.name, "email": voter.email} for voter in obj]
        return Response({"voters": voters}, status=status.HTTP_200_OK)

class VoterSignUpAPIView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')
        number = request.data.get('number')
        
        if LoginTable.objects.filter(name=email).exists():
            return Response({"error": "Email already exists. Please use a different email address."}, status=status.HTTP_400_BAD_REQUEST)
        
        rf = LoginTable.objects.create_user(user_type='voter', name=email, password=password)
        VoterTable.objects.create(login_id=rf, name=name, email=email, number=number)
        return Response({"message": "Voter successfully registered"}, status=status.HTTP_201_CREATED)

class DeleteVoterAPIView(APIView):
    def delete(self, request, voter_id):
        voter_instance = get_object_or_404(VoterTable, id=voter_id)
        
        person_dir = os.path.join(settings.MEDIA_ROOT, 'known_images', voter_instance.name)
        
        if os.path.exists(person_dir):
            recycle_bin_dir = os.path.join(settings.MEDIA_ROOT, 'recycle_bin')
            os.makedirs(recycle_bin_dir, exist_ok=True)
            shutil.move(person_dir, recycle_bin_dir)
        
        known_faces_path = os.path.join(settings.MEDIA_ROOT, 'known_faces.txt')
        with open(known_faces_path, 'r') as f:
            lines = f.readlines()
        
        with open(known_faces_path, 'w') as f:
            for line in lines:
                if line.strip() != voter_instance.name:
                    f.write(line)
        
        login_instance = LoginTable.objects.filter(id=voter_instance.login_id.id).first()
        if login_instance:
            login_instance.delete()
        
        voter_instance.delete()
        
        return Response({"message": "Voter deleted successfully", "redirect": "/VoterList/"}, status=status.HTTP_200_OK)

class VotingPanelAPIView(APIView):
    def get(self, request):
        return Response({"message": "Voting Panel"}, status=status.HTTP_200_OK)

class UserProfileAPIView(APIView):
    def get(self, request,id):
        voter_instance = get_object_or_404(VoterTable, login_id__id=id)
        serializer=VoterTableserializer(voter_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


        
class CoordinatorAPIView(APIView):
    def get(self, request):
        profile_instance = CoordinatorTable.objects.filter(login_id__id=request.session.get("id"))
        return Response({"profile_instance": list(profile_instance.values())}, status=status.HTTP_200_OK)

class MyAccountAPIView(APIView):
    def get(self, request):
        return Response({"message": "My Account"}, status=status.HTTP_200_OK)

class VotingAPIView(APIView):
    def get(self, request):
        candidates = CandidateTable.objects.all()
        return Response({"candidates": list(candidates.values())}, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        candidate_id = request.data.get('candidate_id')
        voter_login_id = request.data.get('voter_loginid')
        
        try:
            voter = VoterTable.objects.get(login_id__id=voter_login_id)
        except VoterTable.DoesNotExist:
            return Response({'message': 'Voter not found!'}, status=status.HTTP_200_OK)

        if voter.voter_status:
            return Response({'message': 'You have already voted!'}, status=status.HTTP_201_CREATED)

        try:
            candidate = CandidateTable.objects.get(id=candidate_id)
        except CandidateTable.DoesNotExist:
            return Response({'message': 'Candidate not found!'}, status=status.HTTP_200_OK)

        Vote.objects.create(voter=voter, candidate=candidate)
        voter.voter_status = True
        voter.save()
        
        send_mail(
            'You have cast your vote successfully',
            'You have cast your vote successfully.',
            'anaghapeethan@gmail.com',  
            [voter.email],
        )
        
        return Response({'message': 'Vote cast successfully!'}, status=status.HTTP_200_OK)

class AddCandidateAPIView(APIView):
    def post(self, request):
        form = CandidateForm(request.data)
        if form.is_valid():
            form.save()
            return Response({'message': 'Candidate successfully added'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

class VoterListAPIView(APIView):
    def get(self, request):
        voters = VoterTable.objects.all()
        return Response({'voters': list(voters.values())}, status=status.HTTP_200_OK)

class ApproveVotersAPIView(APIView):
    def get(self, request):
        voters = VoterTable.objects.all()
        return Response({'voters': list(voters.values())}, status=status.HTTP_200_OK)

class AdminDashboardAPIView(APIView):
    def get(self, request):
        return Response({'message': 'Admin Dashboard'}, status=status.HTTP_200_OK)

class ManageCandidatesAPIView(APIView):
    def get(self, request):
        candidates = CandidateTable.objects.all()
        return Response({'candidates': list(candidates.values())}, status=status.HTTP_200_OK)

class EditCandidateAPIView(APIView):
    def post(self, request, id):
        candidate = get_object_or_404(CandidateTable, id=id)
        form = CandidateForm(request.data, instance=candidate)
        if form.is_valid():
            form.save()
            return Response({'message': 'Candidate successfully updated'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

class DeleteCandidateAPIView(APIView):
    def delete(self, request, id):
        candidate = get_object_or_404(CandidateTable, id=id)
        candidate.delete()
        return Response({'message': 'Candidate successfully deleted'}, status=status.HTTP_200_OK)

class AddCoordinatorAPIView(APIView):
    def post(self, request):
        form = CoordinatorForm(request.data)
        if form.is_valid():
            form.save()
            return Response({'message': 'Coordinator successfully added'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

class CoordinatorListAPIView(APIView):
    def get(self, request):
        coordinators = CoordinatorTable.objects.all()
        return Response({'coordinators': list(coordinators.values())}, status=status.HTTP_200_OK)

class CandidateListAPIView(APIView):
    def get(self, request):
        candidates = CandidateTable.objects.all()
        return Response({'candidates': list(candidates.values())}, status=status.HTTP_200_OK)

class RegisterAPIView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')
        number = request.data.get('number')

        request.session['email'] = email

        if email:
            login_record = LoginTable.objects.create(
                name=email,
                password=password,
                usertype='organizer'
            )

            otp = generate_otp()
            CoordinatorTable.objects.create(
                login_id=login_record,
                name=name,
                email=email,
                number=number,
                otp=otp,
            )

            messages.success(request, f'OTP sent to {email}.')
            return Response({'message': f'OTP sent to {email}.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Please provide a valid email address.'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            otp_record = CoordinatorTable.objects.get(email=email)
            if otp_record.otp == otp:
                return Response({'message': 'OTP verified successfully!'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except CoordinatorTable.DoesNotExist:
            return Response({'error': 'No registration record found for this email.'}, status=status.HTTP_404_NOT_FOUND)

class VerifyOTPVoterAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')


        try:
            otp_record = VoterTable.objects.get(email=email)
            if otp_record.otp == otp:
                return Response({'message': 'OTP verified successfully!'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except VoterTable.DoesNotExist:
            return Response({'error': 'No registration record found for this email.'}, status=status.HTTP_404_NOT_FOUND)

class MonitorCameraAPIView(APIView):
    def post(self, request, id):
            print(request.FILES.get('image'))
        # try:
        #     # Check if voter has already voted
        #     vote_inst = Vote.objects.filter(voter__id=id).first()
        #     print(vote_inst)
            # if vote_inst:
            #     return Response(
            #         # {"message": "Voter has already voted.", "redirect_url": "/alreadyvote/"},
            #         {"message": "Voter has already voted."},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )

            # Get voter
            try:
                voter = VoterTable.objects.get(login_id__id=id)
            except VoterTable.DoesNotExist:
                return Response(
                    {"message": "Voter not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if voter has a face encoding
            if not voter.known_face_encoding:
                return Response(
                    {"message": "No face encoding file for this voter."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Load stored voter face encoding
            try:
                voter_image = face_recognition.load_image_file(voter.known_face_encoding.path)
                known_face_encodings = face_recognition.face_encodings(voter_image)
                if len(known_face_encodings) == 0:
                    
                    return Response(
                        {"message": "No face detected in the stored voter image."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                known_face_encoding = known_face_encodings[0]
            except Exception as e:
                return Response(
                    {"error": f"Error processing stored face encoding: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # # Check for uploaded image
            # if 'image' not in request.FILES.get('image'):
            #     return Response(
            #         {"error": "No image file provided."},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )

            # Process uploaded image
            try:
                uploaded_file = request.FILES.get('image')
                print(uploaded_file)
                # Read image file into a numpy array
                file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                if image is None:
                    return Response(
                        {"message": "Invalid image file."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Convert to RGB for face_recognition
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_image)
                if len(face_encodings) == 0:
                    return Response(
                        {"message": "No face detected in the uploaded image."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Compare faces
                face_encoding = face_encodings[0]
                matches = face_recognition.compare_faces([known_face_encoding], face_encoding)
                if True in matches:
                    return Response(
                        {"message": "Face verified successfully."},
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"message": "Face verification failed."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except Exception as e:
                return Response(
                    {"error": f"Error processing uploaded image: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # except Exception as e:
        #     return Response(
        #         {"error": f"An unexpected error occurred: {str(e)}"},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
class AlreadyVotedAPIView(APIView):
    def get(self, request):
        return Response({'message': 'You have already voted'}, status=status.HTTP_200_OK)