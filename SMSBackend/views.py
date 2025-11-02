from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, parser_classes, permission_classes, authentication_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Students
from .serializers import StudentSerializer

def ren(request):
    return render(request, "register.html")

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([AllowAny])
def Register(request):
    print("📩 Incoming data:", request.data)
    year_suffix = datetime.now().strftime("%y")
    
    # Generate Student ID → STU25001, STU25002, etc.
    last_student = Students.objects.filter(Sid__startswith=f"STU{year_suffix}").order_by('-Sid').first()
    if last_student and last_student.Sid[5:].isdigit():
        last_number = int(last_student.Sid[5:])
    else:
        last_number = 0

    new_number = last_number + 1
    generated_Sid = f"STU{year_suffix}{new_number:03d}"

    # Prepare data for serializer
    student_data = {
        "Sid": generated_Sid,
        "name": request.data.get("name"),
        "email": request.data.get("email"),
        "password": make_password('krify@123'),
        "DOB": request.data.get("DOB"),
        "Address": request.data.get("Address"),
        "phone_number": request.data.get("phone_number"),
        "role": 'User',
        "gender": request.data.get("gender"),
        "profile_pic": request.data.get("profile_pic"),
    }

    serializer = StudentSerializer(data=student_data)
    if not serializer.is_valid():
        print("❌ Serializer errors:", serializer.errors)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Student registered successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        "status": "error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def Login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try :
        user = Students.objects.get(email=email)
    except Students.DoesNotExist:
        return Response({'message': "user not found"}, status=400)
    
    if not check_password(password, user.password):
        return Response({"message":"Incorrect Password"}, status=400)
    
    refresh = RefreshToken.for_user(user)

    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": {
            "id": user.Sid,
            "phone": user.phone_number,
            "role": user.role,
        }
    }, status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_all_students(request):
    try:
        students = Students.objects.all().order_by('Sid')

        serializer = StudentSerializer(students, many=True)

        total_students = students.count()

        return Response({
            'total_students': total_students, 
            'students': serializer.data
        }, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_student(request, Sid):
    print("✅ get_student view reached:", Sid)
    try :
        student = get_object_or_404(Students, Sid=Sid)
    except Students.DoesNotExist:
        return Response({"message": "student not found"}, status=400)
    
    serializer = StudentSerializer(student)
    return Response(serializer.data)
 # make sure this exists

@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([AllowAny])
def update_student(request, pk):
    try:
        student = Students.objects.get(id=pk)
    except Students.DoesNotExist:
        return Response(
            {"status": "error", "message": "Student not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Prepare serializer for update
    serializer = StudentSerializer(student, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "status": "success",
                "message": "Student updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def remove_student(request, Sid):

    try :
        user = Students.objects.get(Sid=Sid)
        user.delete()
        return Response({
            "status": "success",
            "message": f"Student {Sid} deleted successfully."
        }, status=status.HTTP_200_OK)
    except Students.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Student not found."
        }, status=status.HTTP_404_NOT_FOUND)
