from django.http.response import HttpResponse
from django.shortcuts import render
import datetime 
from studentmanagementapp.models import Students
from studentmanagementapp.models import Courses, Subjects
from studentmanagementapp.models import Attendance, AttendanceReport, CustomUser

def student_home(request):
    student_obj = Students.objects.get(admin=request.user.id)
    attendance_total = AttendanceReport.objects.filter(student_id = student_obj).count()
    attendance_present = AttendanceReport.objects.filter(student_id = student_obj, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(student_id = student_obj, status=False).count()
    course = Courses.objects.get(id = student_obj.course_id.id )
    subjects = Subjects.objects.filter(course_id = course).count()
    subject_name=[]
    data_present=[]
    data_absent=[]
    subject_data=Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=True).count()
        attendance_absent_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=False).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)

    return render(request,"student_template/student_home_template.html",{"total_attendance":attendance_total, "attendance_absent":attendance_absent, "attendance_present":attendance_present,"subject":subjects,"data_name":subject_name,"data1":data_present,"data2":data_absent})

def student_view_attendance(request):
    student=Students.objects.get(admin=request.user.id)
    course=student.course_id
    subjects = Subjects.objects.filter(course_id=course)
    return render(request,"student_template/student_view_attendance.html",{"subjects":subjects})

def student_view_attendance_post(request):
    subject_id = request.POST.get("subject")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    start_date_parse = datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    end_date_parse = datetime.datetime.strptime(end_date,"%Y-%m-%d").date()
    subject_obj = Subjects.objects.get(id=subject_id)
    user_object = CustomUser.objects.get(id=request.user.id)
    stud_obj = Students.objects.get(admin=user_object)

    attendance=Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse), subject_id=subject_obj)
    attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=stud_obj)
    return render(request,"student_template/student_attendance_data.html",{"attendance_reports":attendance_reports})