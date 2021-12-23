import json
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from studentmanagementapp.models import Attendance, AttendanceReport, SessionYearModels, Students, Subjects
from studentmanagementapp.models import Courses

def staff_home(request):
    subjects = Subjects.objects.filter(staff_id = request.user.id)
    course_id_list = []
    for subject in subjects:
        course = Courses.objects.get(id = subject.course_id.id)
        course_id_list.append(course.id)

    final_course = []
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)

    students_count = Students.objects.filter(course_id__in = final_course).count()


    attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()
    # print(subjects.count())

    subject_list=[]
    attendance_list=[]
    for subject in subjects:
        attendance_count1=Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)


    students_attendance = Students.objects.filter(course_id__in = final_course)
    student_list = []
    student_list_attendance_present = []
    student_list_attendance_absent= []
    for student in students_attendance:
        attendance_present_count=AttendanceReport.objects.filter(status=True, student_id =student.id ).count()
        attendance_absent_count=AttendanceReport.objects.filter(status=False, student_id =student.id).count()
        student_list.append(student.admin.username)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    return render(request,"staff_template/staff_home_template.html",{"students_count":students_count,"attendance_count":attendance_count, "subjects":subjects, "subject_list":subject_list, "attendance_list":attendance_list, "student_list":student_list, "present_list":student_list_attendance_present, "absent_list":student_list_attendance_absent})

def staff_take_attendance(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_years=SessionYearModels.object.all()
    return render(request, "staff_template/staff_take_attendance.html",{"subjects":subjects,"session_years":session_years})

@csrf_exempt

def get_students(request):
    subject_id=request.POST.get("subject")
    session_year=request.POST.get("session_year")

    subject=Subjects.objects.get(id=subject_id)
    session_model=SessionYearModels.object.get(id=session_year)
    students=Students.objects.filter(course_id=subject.course_id,session_year_id=session_model)
    student_data=serializers.serialize("python",students)
    list_data=[]

    for student in students:
        data_small={"id":student.admin.id,"name":student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def save_attendance_data(request):
    student_ids=request.POST.get("student_ids")
    subject_id=request.POST.get("subject_id")
    attendance_date=request.POST.get("attendance_date")
    session_year_id=request.POST.get("session_year_id")

    subject_model=Subjects.objects.get(id=subject_id)
    session_model=SessionYearModels.object.get(id=session_year_id)
    json_sstudent=json.loads(student_ids)
    
    try: 
        attendance=Attendance(subject_id=subject_model,attendance_date=attendance_date,session_year_id=session_model)
        attendance.save()
        
        for stud in json_sstudent:
            student=Students.objects.get(admin=stud['id'])
            attendance_report=AttendanceReport(student_id=student,attendance_id=attendance,status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")

def staff_update_attendance(request):
    subjects = Subjects.objects.filter(staff_id = request.user.id)
    session_year_id = SessionYearModels.object.all()
    return render(request,"staff_template/staff_update_attendance.html",{"subjects":subjects, "session_year_id":session_year_id})

@csrf_exempt

def get_attendance_dates(request):
    subject = request.POST.get("subject")
    session_year_id = request.POST.get("session_year_id")
    subject_obj = Subjects.objects.get(id = subject)
    session_year_obj = SessionYearModels.object.get(id = session_year_id)
    attendance = Attendance.objects.filter(subject_id = subject_obj,session_year_id = session_year_obj)
    attendance_obj = []
    for attendance_single in attendance:
        data = {"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)

@csrf_exempt

def get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")

    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id = attendance )
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)


@csrf_exempt
def save_updateattendance_data(request):
    student_ids=request.POST.get("student_ids")
    attendance_date=request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id = attendance_date )
    json_sstudent=json.loads(student_ids)
    
    try: 
        for stud in json_sstudent:
            student=Students.objects.get(admin=stud['id'])
            attendance_report=AttendanceReport.objects.get(student_id=student,attendance_id=attendance)
            attendance_report.status = stud['status']
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")
