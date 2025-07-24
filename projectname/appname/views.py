from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET
from .forms import CustomUserCreationForm, LoginForm, StaffSignupForm, CourseUploadForm
from .models import StudentProfile, StaffProfile, StaffUpdate, Enrollment, Course


# ---------- Public Pages ----------
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')


# ---------- Authentication ----------
def login(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        selected_role = request.POST.get("role")

        user = authenticate(request, username=username, password=password)

        if user:
            auth_login(request, user)

            if selected_role == "admin" and not user.is_superuser:
                messages.error(request, "⚠️ Not an admin account.")
                return redirect("login")
            if selected_role == "staff" and not hasattr(user, 'staffprofile'):
                messages.error(request, "⚠️ Not a staff account.")
                return redirect("login")
            if selected_role == "student" and not hasattr(user, 'studentprofile'):
                messages.error(request, "⚠️ Not a student account.")
                return redirect("login")

            return redirect("home")
        else:
            messages.error(request, "Invalid credentials.")
            return redirect("login")

    return render(request, "login.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    return redirect('home')


# ---------- Signup ----------
def signup(request):  # Student Signup
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.save()
            StudentProfile.objects.create(user=user)
            messages.success(request, "✅ Student account created successfully!")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form, 'role': 'student'})


def staff_signup(request):
    if request.method == 'POST':
        form = StaffSignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            full_name = form.cleaned_data['full_name']
            department = form.cleaned_data['department']

            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = True
            user.save()

            StaffProfile.objects.create(user=user, full_name=full_name, department=department)

            messages.success(request, "✅ Staff account created. Please log in.")
            return redirect('login')
    else:
        form = StaffSignupForm()

    return render(request, 'staff_signup.html', {'form': form})


# ---------- Dashboards ----------
@login_required
def dashboard(request):
    user = request.user
    if user.is_superuser:
        return redirect('admindashboard')
    elif hasattr(user, 'staffprofile'):
        return redirect('staffdashboard')
    elif hasattr(user, 'studentprofile'):
        return redirect('studentdashboard')
    return redirect('home')


@login_required
def studentdashboard(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
        enrolled_courses = Enrollment.objects.filter(student=student)
        enrolled_count = enrolled_courses.count()
    except StudentProfile.DoesNotExist:
        student = None
        enrolled_courses = []
        enrolled_count = 0

    context = {
        'student': student,
        'enrolled_courses': enrolled_courses,
        'enrolled_count': enrolled_count
    }
    return render(request, 'studentdashboard.html', context)


@login_required
def staffdashboard(request):
    try:
        staff = StaffUpdate.objects.get(user=request.user)
    except StaffUpdate.DoesNotExist:
        staff = None

    return render(request, 'staffdashboard.html', {'staff': staff})


# ---------- Student Profile Update ----------
@login_required
def update_student(request):
    student = StudentProfile.objects.get(user=request.user)
    error_msg = None

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")
        college = request.POST.get("college")
        branch = request.POST.get("branch")
        year = request.POST.get("year")
        roll_number = request.POST.get("roll_number")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        address = request.POST.get("address")
        profile_image = request.FILES.get("profile_image")  # <-- Correct variable

        if not all([full_name, mobile, email, branch, gender,dob, address, year, college]):
            error_msg = "⚠️ Please fill all required fields."
        else:
            student.full_name = full_name
            student.mobile = mobile
            student.email = email
            student.college = college
            student.branch = branch
            student.year = year
            student.roll_number = roll_number
            student.dob = dob 
            student.gender = gender
            student.address = address

            if profile_image:  # <-- Fixed here
                student.image = profile_image  # Assuming your model field is `image`

            student.save()
            return redirect('studentdashboard')

    return render(request, 'update_student.html', {'student': student, 'error_msg': error_msg})


# ---------- Staff Profile Update ----------
@login_required
def update_staff(request, user_id=None):
    if user_id:
        # Admin is editing another staff profile
        if not request.user.is_superuser:
            return redirect('home')  # or show 403
        user = get_object_or_404(User, id=user_id)
    else:
        # Staff updating their own profile
        user = request.user

    try:
        staff = StaffUpdate.objects.get(user=user)
    except StaffUpdate.DoesNotExist:
        staff = StaffUpdate.objects.create(user=user)

    error_msg = None

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        department = request.POST.get('department')
        designation = request.POST.get('designation')
        experience = request.POST.get('experience')
        qualification = request.POST.get('qualification')
        linkedin = request.POST.get('linkedin')
        address = request.POST.get('address')
        profile_image = request.FILES.get('profile_image')

        if not all([full_name, email, mobile, department, designation, experience, qualification, linkedin, address]):
            error_msg = "⚠️ Please fill in all fields."
        else:
            staff.full_name = full_name
            staff.email = email
            staff.mobile = mobile
            staff.department = department
            staff.designation = designation
            staff.experience = experience
            staff.qualification = qualification
            staff.linkedin = linkedin
            staff.address = address
            if profile_image:
                staff.profile_image = profile_image
            staff.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect('admindashboard' if request.user.is_superuser else 'staffdashboard')

    return render(request, 'update_staff.html', {'staff': staff, 'error_msg': error_msg})


# ---------- Course Management ----------
@login_required
def upload_course(request):
    if request.method == 'POST':
        form = CourseUploadForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.uploaded_by = request.user
            course.save()
            return redirect('course_approval')
    else:
        form = CourseUploadForm()
    return render(request, 'upload_course.html', {'form': form})


@login_required
def course_approval(request):
    courses = Course.objects.filter(uploaded_by=request.user, is_approved=False)
      # Staff will see all their uploaded courses (approved + pending)
    if hasattr(request.user, 'staffprofile'):
        staff_courses = Course.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    else:
        staff_courses = []

    # Admin will see all pending courses from all users
    pending_courses = []
    if request.user.is_superuser:
        pending_courses = Course.objects.filter(is_approved=False).order_by('-uploaded_at')

    return render(request, 'course_approval.html', {
        'staff_courses': staff_courses,
        'pending_courses': pending_courses,
        'courses': courses,
    })



from django.db.models import Q

@login_required
def all_courses(request):
    query = request.GET.get('q')
    courses = Course.objects.filter(is_approved=True).order_by('-uploaded_at')

    if query:
        courses = courses.filter(Q(title__icontains=query))

    user_role = None
    if hasattr(request.user, 'staffprofile'):
        user_role = 'staff'
    elif hasattr(request.user, 'studentprofile'):
        user_role = 'student'
    elif request.user.is_superuser:
        user_role = 'admin'

    return render(request, 'all_courses.html', {
        'courses': courses,
        'user_role': user_role,
        'query': query,
    })




def is_admin(user):
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def admindashboard(request):
    students = StudentProfile.objects.select_related('user')
    staff = StaffProfile.objects.select_related('user')
    courses = Course.objects.select_related('uploaded_by').all()
    profile, _ = AdminProfile.objects.get_or_create(user=request.user)

    context = {
        'students': students,
        'staff': staff,
        'courses': courses,
        'profile': profile,  # ✅ Add this
    }
    return render(request, 'admindashboard.html', context)




@login_required
@user_passes_test(is_admin)
def delete_student(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()  # This will also delete related StudentProfile due to on_delete=models.CASCADE
    return redirect('admindashboard')



@login_required
@user_passes_test(is_admin)
def delete_staff(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()  # Deletes StaffProfile as well
    return redirect('admindashboard')



@login_required
@user_passes_test(is_admin)
def approve_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.is_approved = True
    course.save()
    messages.success(request, f'✅ Course "{course.title}" approved successfully!')
    return redirect('admindashboard')  # or 'admindashboard'



@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # If admin, allow deletion of any course
    if request.user.is_superuser:
        course.delete()
        return redirect('admindashboard')
    
    # If staff, only allow deletion of unapproved courses they uploaded
    if course.uploaded_by == request.user and not course.is_approved:
        course.delete()
        return redirect('course_approval')

    return redirect('home')  # Unauthorized fallback



from .forms import UserUpdateForm, AdminProfileForm
from .models import AdminProfile

@login_required
def update_admin_profile(request):
    user = request.user
    profile, created = AdminProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = AdminProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('admindashboard')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = AdminProfileForm(instance=profile)

    return render(request, 'update_admin_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    })



@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user

    if hasattr(user, 'studentprofile'):
        student_profile = user.studentprofile  # ✅ Get the student profile
        if Enrollment.objects.filter(student=student_profile, course=course).exists():
            messages.info(request, 'You are already enrolled in this course.')
        else:
            Enrollment.objects.create(student=student_profile, course=course)  # ✅ Fix is here
            messages.success(request, f'✅ You have successfully enrolled in "{course.title}".')
    else:
        messages.error(request, "Only students can enroll in courses.")

    return redirect('studentdashboard')


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrolled = False
    show_material = False

    if hasattr(request.user, 'studentprofile'):
        enrolled = Enrollment.objects.filter(student=request.user.studentprofile, course=course).exists()
        show_material = enrolled

    return render(request, 'course_detail.html', {
        'course': course,
        'enrolled': enrolled,
        'show_material': show_material,
    })
