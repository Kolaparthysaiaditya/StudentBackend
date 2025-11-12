from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, parser_classes, permission_classes, authentication_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db.models import Avg, Count, Sum
from datetime import date
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Students, Enrollment, Course
from .serializers import StudentSerializer, CourseSerializer, EnrollmentSerializer

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
        courses = Course.objects.all()
        enrolements = Enrollment.objects.all()
        serializer = StudentSerializer(students, many=True)

        total_students = students.count()
        total_courses = courses.count()
        total_Enrollments = enrolements.count()

        return Response({
            'total_students': total_students, 
            'total_courses' : total_courses,
            'total_Enrollments': total_Enrollments,
            'students': serializer.data,
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


@api_view(['GET'])
@permission_classes([AllowAny])
def get_enrollment_details(request, Sid):
    try:
        student = Students.objects.get(Sid=Sid)
        enrollment = Enrollment.objects.get(student=student)
        
        marks = float(enrollment.marks or 0)

        if marks >= 35:
            status = "pass"
        else:
            status = "fail"

        return Response({
            "id":enrollment.id,
            "enrollment_id": enrollment.enrollment_id,
            "student": student.name,
            "course": enrollment.course.name,
            "marks": enrollment.marks,
            "status": status,
            "created_on": enrollment.created_on.strftime("%Y-%m-%d %H:%M"),
        }, status=200)

    except Students.DoesNotExist:
        return Response({"message": "Student not found"}, status=404)
    except Enrollment.DoesNotExist:
        return Response({"message": "Enrollment not found"}, status=404)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_marks(request, id):
    try:
        enrollment = Enrollment.objects.get(enrollment_id=id)
        marks = request.data.get("marks")
        remark = request.data.get("remark", "")

        # Convert marks to int safely
        marks_int = int(marks) if marks is not None else None
        status = "Pass" if marks_int is not None and marks_int >= 40 else "Fail"

        enrollment.marks = marks_int
        enrollment.remark = remark
        enrollment.status = status
        enrollment.save()

        return Response({
            "status": "success",
            "message": f"Marks updated successfully for {enrollment.student.name}",
            "marks": marks_int,
            "status_value": status,
        }, status=200)
    except Enrollment.DoesNotExist:
        return Response({"message": "Enrollment not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)




@api_view(['GET'])
@permission_classes([AllowAny])
def average_age(request):
    today = date.today()
    students = Students.objects.exclude(DOB__isnull=True)

    total_students = Students.objects.count()
    male_count = Students.objects.filter(gender="Male").count()
    female_count = Students.objects.filter(gender="Female").count()

    if total_students == 0:
        return Response({
            "average": 0,
            "male": 0,
            "female": 0,
            "students": 0
        })

    # ✅ Calculate average age
    total_age = 0
    for student in students:
        age = today.year - student.DOB.year - (
            (today.month, today.day) < (student.DOB.month, student.DOB.day)
        )
        total_age += age

    avg_age = round(total_age / students.count(), 2) if students.exists() else 0

    # ✅ Calculate gender percentages
    male_percentage = round((male_count / total_students) * 100, 2)
    female_percentage = round((female_count / total_students) * 100, 2)

    return Response({
        "students": total_students,
        "average": avg_age,
        "male": male_percentage,
        "female": female_percentage
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_courses(request):
    try:
        courses = Course.objects.all().order_by('courseId')
        serializer = CourseSerializer(courses, many=True)
        return Response({
            "total_courses": courses.count(),
            "courses": serializer.data
        }, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_enrolled_details(request, course_name):
    try:
        # Case-insensitive search for course
        try:
            course = Course.objects.get(name__iexact=course_name)
        except Course.DoesNotExist:
            return Response({"message": "Course not found."}, status=404)

        enrollments = Enrollment.objects.filter(course=course)

        if not enrollments.exists():
            return Response({
                "course_name": course.name,
                "course_id": course.courseId,
                "total_enrolled": 0,
                "students": []
            }, status=200)

        students_data = []
        for enrollment in enrollments:
            students_data.append({
                "enrollment_id": enrollment.enrollment_id,
                "student_id": enrollment.student.Sid,
                "student_name": enrollment.student.name,
                "email": enrollment.student.email,
                "marks": enrollment.marks,
                "status": enrollment.status,
                "remark": enrollment.remark,
                "created_on": enrollment.created_on.strftime("%Y-%m-%d %H:%M"),
            })

        return Response({
            "course_name": course.name,
            "course_id": course.courseId,
            "total_enrolled": enrollments.count(),
            "students": students_data
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def course_statistics(request):
    try:
        # 1) Total number of courses
        total_courses = Course.objects.count()

        # 2) Number of distinct courses that have at least one enrollment
        enrolled_courses_qs = Course.objects.filter(enrolled_students__isnull=False).distinct()
        total_enrolled_courses = enrolled_courses_qs.count()

        # 3) Total enrolled duration: sum course.duration for EACH enrollment
        #    (counts a course's duration once per enrollment)
        total_enrolled_duration = Enrollment.objects.aggregate(
            total=Sum('course__duration')
        )['total'] or 0

        # 4) Most popular course (by enrollment count)
        popular_course = (
            Course.objects
            .annotate(enrollment_count=Count('enrolled_students'))
            .order_by('-enrollment_count')
            .first()
        )

        if popular_course:
            most_popular_course = popular_course.name
            most_popular_count = popular_course.enrollment_count
        else:
            most_popular_course = None
            most_popular_count = 0

        return Response({
            "total_courses": total_courses,
            "total_enrolled_courses": total_enrolled_courses,
            "total_enrolled_duration": total_enrolled_duration,
            "most_popular_course": most_popular_course,
            "enrolled_count_in_popular_course": most_popular_count,
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_course(request):
    try:
        data = request.data
        name = (data.get("name") or "").strip()

        if Course.objects.filter(name__iexact=name).exists():
            return Response({"message": "Course name already exists"}, status=status.HTTP_400_BAD_REQUEST)


        # Auto-generate CourseId like CRS25001, CRS25002...
        year_suffix = datetime.now().strftime("%y")
        last_course = Course.objects.filter(courseId__startswith=f"CRS{year_suffix}").order_by('-courseId').first()
        if last_course and last_course.courseId[5:].isdigit():
            last_number = int(last_course.courseId[5:])
        else:
            last_number = 0
        new_number = last_number + 1
        generated_courseId = f"CRS{year_suffix}{new_number:03d}"

        course_data = {
            "courseId": generated_courseId,
            "name": data.get("name"),
            "description": data.get("description"),
            "duration": data.get("duration"),
            "instructor": data.get("instructor"),
            "level": data.get("level"),
            "fee": data.get("fee"),
        }

        serializer = CourseSerializer(data=course_data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Course added successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_course(request, courseId):
    try:
        course = Course.objects.get(courseId=courseId)
    except Course.DoesNotExist:
        return Response({"message": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if 'courseName' is in the request and already exists in another course
    new_course_name = request.data.get('courseName')
    if new_course_name:
        existing_course = Course.objects.filter(courseName__iexact=new_course_name).exclude(courseId=courseId).first()
        if existing_course:
            return Response({
                "status": "error",
                "message": "Course name already exists"
            }, status=status.HTTP_400_BAD_REQUEST)

    serializer = CourseSerializer(course, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Course updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        "status": "error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_course(request, courseId):
    try:
        course = Course.objects.get(courseId=courseId)
        course.delete()
        return Response({
            "status": "success",
            "message": f"Course {courseId} deleted successfully"
        }, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Course not found"
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_enrollments(request):
    enrollments = Enrollment.objects.select_related('student', 'course').all()
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_enrollment(request):
    try:
        data = request.data
        student_id = data.get("student_id")
        course_id = data.get("course_id")
        marks = data.get("marks", 0)
        remark = data.get("remark", "")

        # Generate unique enrollment_id like ENR25001
        year_suffix = datetime.now().strftime("%y")
        last_enr = Enrollment.objects.filter(enrollment_id__startswith=f"ENR{year_suffix}").order_by('-enrollment_id').first()
        if last_enr and last_enr.enrollment_id[5:].isdigit():
            last_num = int(last_enr.enrollment_id[5:]) + 1
        else:
            last_num = 1
        enrollment_id = f"ENR{year_suffix}{last_num:03d}"

        enrollment = Enrollment.objects.create(
            enrollment_id=enrollment_id,
            student_id=student_id,
            course_id=course_id,
            marks=marks,
            remark=remark
        )
        return Response({"message": "Enrollment added successfully!"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_enrollment(request, enrollment_id):
    try:
        enroll = Enrollment.objects.get(enrollment_id=enrollment_id)
        marks = request.data.get("marks")
        remark = request.data.get("remark")

        if marks is not None:
            enroll.marks = marks
        if remark is not None:
            enroll.remark = remark

        enroll.save()
        return Response({"message": "Enrollment updated successfully"}, status=200)
    except Enrollment.DoesNotExist:
        return Response({"error": "Enrollment not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_students(request):
    students = Students.objects.all()
    data = [{"id": s.id, "name": s.name, "Sid": s.Sid} for s in students]
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_courses(request):
    courses = Course.objects.all()
    data = [{"id": c.id, "courseId": c.courseId, "name": c.name, "level": c.level} for c in courses]
    return Response(data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_enrollment(request, enrollment_id):
    try:
        enrollment = Enrollment.objects.get(enrollment_id=enrollment_id)
        enrollment.delete()
        return Response({
            "status": "success",
            "message": f"Enrollment {enrollment_id} deleted successfully."
        }, status=status.HTTP_200_OK)
    except Enrollment.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Enrollment not found."
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def all_students_marks(request):
    try:
        enrollments = Enrollment.objects.select_related('student', 'course').all().order_by('-created_on')

        marks_list = []
        marks_values = []

        for enr in enrollments:
            mark_value = None
            if enr.marks:
                try:
                    mark_value = float(enr.marks)
                    marks_values.append(mark_value)
                except ValueError:
                    pass

            marks_list.append({
                "student_id": enr.student.Sid,
                "student_name":enr.student.name,
                "enrollment_id": enr.enrollment_id,
                "course_name": enr.course.name,
                "marks": enr.marks,
                "status": enr.status,
                "remark": enr.remark,
                "date": enr.created_on.strftime("%Y-%m-%d"),
            })

        # Calculate stats
        highest = max(marks_values) if marks_values else None
        lowest = min(marks_values) if marks_values else None
        average = round(sum(marks_values) / len(marks_values), 2) if marks_values else None

        return Response({
            "students_marks": marks_list,
            "summary": {
                "highest_marks": float(highest),
                "lowest_marks": lowest,
                "average_marks": average
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_marks_record(request, enrollment_id):
    """
    Update all enrollment fields: student, course, marks, remark, status, date.
    """
    try:
        enrollment = Enrollment.objects.get(enrollment_id=enrollment_id)
        data = request.data

        # Optional updates
        student_id = data.get("student_id")
        course_id = data.get("course_id")
        marks = data.get("marks")
        remark = data.get("remark")
        status_val = data.get("status")
        date = data.get("date")

        from .models import Students, Course

        if student_id:
            student = Students.objects.filter(Sid=student_id).first()
            if student:
                enrollment.student = student

        if course_id:
            course = Course.objects.filter(courseId=course_id).first()
            if course:
                enrollment.course = course

        if marks is not None:
            enrollment.marks = marks
            try:
                marks_value = float(marks)
                enrollment.status = "pass" if marks_value >= 35 else "fail"
            except ValueError:
                enrollment.status = None

        if remark is not None:
            enrollment.remark = remark

        if status_val:
            enrollment.status = status_val.lower()

        if date:
            from datetime import datetime
            try:
                enrollment.created_on = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                pass

        enrollment.save()

        return Response({
            "message": "Enrollment updated successfully",
            "updated": {
                "enrollment_id": enrollment.enrollment_id,
                "student_name": enrollment.student.name,
                "course_name": enrollment.course.name,
                "marks": enrollment.marks,
                "status": enrollment.status,
                "remark": enrollment.remark,
                "date": enrollment.created_on.strftime("%Y-%m-%d"),
            }
        }, status=status.HTTP_200_OK)

    except Enrollment.DoesNotExist:
        return Response({"error": "Enrollment not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

