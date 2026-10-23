from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, logout, login, update_session_auth_hash
from datetime import date, datetime, timedelta
from django.db.models import Q, Sum
from django.utils import timezone
import calendar
import json
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

# Create your views here.

@ensure_csrf_cookie
def index(request):
    return render(request,'index.html')

def admin_login(request):
    error = ""
    if request.method == 'POST':
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        try:
            if user.is_staff:
                login(request, user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
    return render(request,'admin_login.html', locals())

def _ensure_demo_member(user):
    """Demo account only: make sure admin1 has a Member profile.
    Links to an existing unlinked member (so there is real data to show), else creates one."""
    if Member.objects.filter(user=user).exists():
        return
    member = Member.objects.filter(user__isnull=True).order_by('id').first()
    if member is not None:
        member.user = user
        member.save()
    else:
        Member.objects.create(
            user=user, name='Default Member', contact='1234567890', email='admin1@gym.com',
            gender='Male', plan='Basic Plan', joindate=timezone.now().date(), initamount='0'
        )


@csrf_protect
def member_login(request):
    error = ""
    if request.method == 'POST':
        # accept either field name so a mismatched template can't crash the view
        u = (request.POST.get('uname') or request.POST.get('username') or '').strip()
        p = request.POST.get('pwd') or request.POST.get('password') or ''
        
        # First try to authenticate with the provided credentials
        user = authenticate(username=u, password=p)
        
        if user is not None and not user.is_staff:
            # If user exists and is not staff, log them in
            if user.username == 'admin1':
                _ensure_demo_member(user)
            login(request, user)
            error = "no"
            return redirect('member_dashboard')
        elif user is not None and user.is_staff:
            messages.error(request, 'This is a staff account. Please use the Admin Login page.')
            error = "yes"
        else:
            # If authentication failed, try the default credentials
            if u == 'admin1' and p == 'admin1':
                try:
                    # Get or create the default member user
                    user, created = User.objects.get_or_create(
                        username='admin1',
                        defaults={
                            'email': 'admin1@gym.com',
                            'is_staff': False
                        }
                    )
                    # always (re)set the password so admin1/admin1 works even if the user already existed
                    user.set_password('admin1')
                    user.is_staff = False
                    user.save()
                    
                    _ensure_demo_member(user)
                    
                    # Authenticate and login
                    user = authenticate(username='admin1', password='admin1')
                    if user is not None:
                        login(request, user)
                        error = "no"
                        return redirect('member_dashboard')
                except Exception as e:
                    print(e)  # For debugging
                    error = "yes"
            else:
                error = "yes"
        if error == "yes" and not list(messages.get_messages(request)):
            messages.error(request, 'Invalid username or password.')
    return render(request, 'member_login.html', locals())

def _plan_months(duration):
    """'3' -> 3, '1 Month' -> 1, '1 Year' -> 12 (first number found, default 1)."""
    import re
    text = str(duration or '')
    found = re.search(r'\d+', text)
    months = int(found.group()) if found else 1
    if 'year' in text.lower():
        months *= 12
    return months


def _duration_text(check_in, check_out):
    """Hours/minutes between two time values (or 'HH:MM' strings)."""
    try:
        if not check_in or not check_out:
            return "--"
        if isinstance(check_in, str):
            check_in = datetime.strptime(check_in[:5], '%H:%M').time()
        if isinstance(check_out, str):
            check_out = datetime.strptime(check_out[:5], '%H:%M').time()
        start = datetime.combine(date.today(), check_in)
        end = datetime.combine(date.today(), check_out)
        minutes = int((end - start).total_seconds() // 60)
        if minutes < 0:
            return "--"
        return f"{minutes // 60}h {minutes % 60}m"
    except Exception:
        return "--"


def _get_member(request):
    """Return the Member linked to the logged-in user, or None."""
    if not request.user.is_authenticated:
        return None
    return Member.objects.filter(user=request.user).first()


def _member_guard(request):
    """Return (member, redirect_response). Only non-staff users with a Member profile pass."""
    if not request.user.is_authenticated or request.user.is_staff:
        return None, redirect('member_login')
    member = _get_member(request)
    if member is None:
        logout(request)
        messages.error(request, 'No member profile is linked to this account. Please contact the gym admin.')
        return None, redirect('member_login')
    return member, None


@csrf_protect
@ensure_csrf_cookie
def member_dashboard(request):
    member, response = _member_guard(request)
    if response:
        return response

    today = timezone.now().date()
    month_start = today.replace(day=1)

    attendance_count = Attendance.objects.filter(member=member, date__gte=month_start, date__lte=today).count()
    attendance_records = list(Attendance.objects.filter(member=member).order_by('-date', '-check_in')[:10])
    for record in attendance_records:
        record.duration = _duration_text(record.check_in, record.check_out)

    payment_history = list(Payment.objects.filter(member=member).order_by('-payment_date')[:10])
    latest_payment = payment_history[0] if payment_history else None
    total_paid = Payment.objects.filter(member=member).aggregate(Sum('amount'))['amount__sum'] or 0

    # Plan details (Member.plan stores the plan name as text)
    plan = Plan.objects.filter(name=(member.plan or '').strip()).first() or Plan.objects.filter(name__iexact=(member.plan or '').strip()).first()
    expiry_date = None
    days_left = None
    if plan:
        base_date = latest_payment.payment_date if latest_payment else member.joindate
        if base_date:
            expiry_date = base_date + timedelta(days=30 * _plan_months(plan.duration))
            days_left = (expiry_date - today).days

    recent_activities = []
    for rec in attendance_records[:3]:
        recent_activities.append({'title': f'Gym check-in at {str(rec.check_in)[:5]}', 'timestamp': rec.date})
    for pay in payment_history[:3]:
        recent_activities.append({'title': f'Payment of Rs. {pay.amount} made', 'timestamp': pay.payment_date})
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)

    return render(request, 'member_dashboard.html', {
        'member': member,
        'plan': plan,
        'attendance_count': attendance_count,
        'attendance_records': attendance_records,
        'payment_history': payment_history,
        'latest_payment': latest_payment,
        'total_paid': total_paid,
        'expiry_date': expiry_date,
        'days_left': days_left,
        'today': today,
        'recent_activities': recent_activities[:5],
        'active': 'dashboard',
    })


@csrf_protect
def update_member_profile(request):
    member, response = _member_guard(request)
    if response:
        return response
    if request.method == 'POST':
        member.name = request.POST.get('name') or member.name
        member.email = request.POST.get('email') or member.email
        member.contact = request.POST.get('mobile') or member.contact
        member.gender = request.POST.get('gender') or member.gender
        member.save()
        messages.success(request, 'Profile updated successfully!')
    return redirect('member_dashboard')

def admin_home(request):
    if not request.user.is_staff:
        return redirect('admin_login')
    en = Enquiry.objects.all().count()
    eq = Equipment.objects.all().count()
    p = Plan.objects.all().count()
    m = Member.objects.all().count()

    # Count data for new features
    ur = UserRole.objects.all().count()
    mp = MembershipPlan.objects.all().count()
    
    # For monthly attendance
    today = timezone.now().date()
    month_start = today.replace(day=1)
    atd = Attendance.objects.filter(date__gte=month_start, date__lte=today).count()
    
    # For payment history
    pay = Payment.objects.all().count()

    d = {'en': en, 'eq': eq, 'p': p, 'm': m, 'ur': ur, 'mp': mp, 'atd': atd, 'pay': pay}
    return render(request,'admin_home.html', d)

def contact(request):
    error = ""
    if request.method == 'POST':
        n = request.POST['name']
        e = request.POST['emailid']
        c = request.POST['contact']
        s = request.POST['subject']
        m = request.POST['message']
        try:
            Contact.objects.create(name=n, emailid=e, contact=c, subject=s, message=m, msgdate=date.today(),
                                   isread="no")
            error = "no"
        except:
            error = "yes"
    return render(request,'contact.html', locals())

def addEnquiry(request):
    if not request.user.is_authenticated:
        return redirect(admin_login)
    error = ""
    if request.method == "POST":
        n = request.POST['name']
        m = request.POST['mobile']
        e = request.POST['email']
        a = request.POST['age']
        g = request.POST['gender']
        try:
            Enquiry.objects.create(name=n, mobile=m, email=e, age=a, gender=g)
            error = "no"
        except:
            error = "yes"
    return render(request,'addEnquiry.html', locals())

def viewEnquiry(request):
    if not request.user.is_authenticated:
        return redirect(admin_login)
    enquiry = Enquiry.objects.all()
    return render(request,'viewEnquiry.html', locals())

def edit_Enquiry(request,pid):
    error = ""
    if not request.user.is_authenticated:
        return redirect(admin_login)
    user = request.user
    enquiry = Enquiry.objects.get(id=pid)
    if request.method == "POST":
        n1 = request.POST['name']
        m1 = request.POST['mobile']
        e1 = request.POST['email']
        a1 = request.POST['age']
        g1 = request.POST['gender']

        enquiry.name = n1
        enquiry.mobile = m1
        enquiry.email = e1
        enquiry.age = a1
        enquiry.gender = g1
        try:
            enquiry.save()
            error = "no"
        except:
            error = "yes"
    return render(request,'edit_Enquiry.html', locals())

def delete_Enquiry(request,pid):
    enquiry = Enquiry.objects.get(id=pid)
    enquiry.delete()
    return redirect('viewEnquiry')

def addPlan(request):
    if not request.user.is_authenticated:
        return redirect(admin_login)
    error = ""
    if request.method == "POST":
        p = request.POST['name']
        a = request.POST['amount']
        d = request.POST['duration']
        try:
            Plan.objects.create(name=p, amount=a, duration=d)
            error = "no"
        except:
            error = "yes"
    return render(request,'addPlan.html', locals())

def viewPlan(request):
    if not request.user.is_authenticated:
        return redirect(admin_login)
    plan = Plan.objects.all()
    return render(request,'viewPlan.html', locals())

def edit_Plan(request,pid):
    error = ""
    if not request.user.is_authenticated:
        return redirect(admin_login)
    user = request.user
    plan = Plan.objects.get(id=pid)
    if request.method == "POST":
        p1 = request.POST['name']
        a1 = request.POST['amount']
        d1 = request.POST['duration']

        plan.name = p1
        plan.amount = a1
        plan.duration = d1
        try:
            plan.save()
            error = "no"
        except:
            error = "yes"
    return render(request,'edit_Plan.html', locals())

def delete_Plan(request,pid):
    plan = Plan.objects.get(id=pid)
    plan.delete()
    return redirect('viewPlan')

def addEquipment(request):
    if not request.user.is_authenticated:
        return redirect(admin_login)
    error = ""
    if request.method == "POST":
        n = request.POST['name']
        p = request.POST['price']
        u = request.POST['unit']
        pd = request.POST['purchasedate']
        d = request.POST['description']

        try:
            Equipment.objects.create(name=n, price=p, unit=u, purchasedate=pd, description=d)
            error = "no"
        except:
            error = "yes"
    return render(request,'addEquipment.html', locals())

def viewEquipment(request):
    if not request.user.is_authenticated:
        return redirect(admin_login)
    equipment = Equipment.objects.all()
    return render(request,'viewEquipment.html', locals())

def edit_Equipment(request,pid):
    error = ""
    if not request.user.is_authenticated:
        return redirect(admin_login)
    user = request.user
    equipment = Equipment.objects.get(id=pid)
    if request.method == "POST":
        n1 = request.POST['name']
        p1 = request.POST['price']
        u1 = request.POST['unit']
        d1 = request.POST['description']

        equipment.name = n1
        equipment.price = p1
        equipment.unit = u1
        equipment.description = d1
        try:
            equipment.save()
            error = "no"
        except:
            error = "yes"
    return render(request,'edit_Equipment.html', locals())

def delete_Equipment(request,pid):
    equipment = Equipment.objects.get(id=pid)
    equipment.delete()
    return redirect('viewEquipment')

def addMember(request):
    if not request.user.is_authenticated:
        return redirect(admin_login)
    error = ""
    plan1 = Plan.objects.all()
    if request.method == "POST":
        n = request.POST['name']
        c = request.POST['contact']
        e = request.POST['email']
        g = request.POST['gender']
        p = request.POST['plan']
        j = request.POST['joindate']
        i = request.POST['initamount']
        plan = Plan.objects.get(name=p)
        
        try:
            # Get or create the default member user
            default_user, created = User.objects.get_or_create(
                username='member',
                defaults={
                    'email': 'member@gym.com',
                    'is_staff': False
                }
            )
            if created:
                default_user.set_password('member123')
                default_user.save()
            
            # Create member and associate with the default user
            member = Member.objects.create(
                user=default_user,
                name=n,
                contact=c,
                email=e,
                gender=g,
                plan=plan,
                joindate=j,
                initamount=i
            )
            
            # Store the credentials to show in the template
            request.session['temp_username'] = 'member'
            request.session['temp_password'] = 'member123'
            error = "no"
        except Exception as e:
            print(e)  # For debugging
            error = "yes"
    d = {'error':error, 'plan':plan1}
    return render(request,'addMember.html', d)

def viewMember(request):
    if not request.user.is_authenticated:
        return redirect(admin_login)
    member = Member.objects.all()
    return render(request,'viewMember.html', locals())

def edit_Member(request,pid):
    if not request.user.is_authenticated:
        return redirect(admin_login)
    error = ""
    user = request.user
    member = Member.objects.get(id=pid)
    if request.method == "POST":
        n1 = request.POST['name']
        c1 = request.POST['contact']
        e1 = request.POST['email']
        g1 = request.POST['gender']
        i1 = request.POST['initamount']

        member.name = n1
        member.contact = c1
        member.email = e1
        member.gender = g1
        member.initamount = i1
        try:
            member.save()
            error = "no"
        except:
            error = "yes"
    return render(request,'edit_Member.html', locals())

def delete_Member(request,pid):
    member = Member.objects.get(id=pid)
    member.delete()
    return redirect('viewMember')

def unread_queries(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    contact = Contact.objects.filter(isread="no")
    return render(request,'unread_queries.html', locals())

def read_queries(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    contact = Contact.objects.filter(isread="yes")
    return render(request,'read_queries.html', locals())

def view_queries(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    contact = Contact.objects.get(id=pid)
    contact.isread = "yes"
    contact.save()
    return render(request,'view_queries.html', locals())

def delete_contact(request,pid):
    contact = Contact.objects.get(id=pid)
    contact.delete()
    return redirect('read_queries')

def changePassword(request):
    if not request.user.is_authenticated:
        return redirect('index')
    error = ""
    user = request.user
    if request.method == "POST":
        o = request.POST['oldpassword']
        n = request.POST['newpassword']
        try:
            u = User.objects.get(id=request.user.id)
            if user.check_password(o):
                u.set_password(n)
                u.save()
                error = "no"
            else:
                error = 'not'
        except:
            error = "yes"
    return render(request,'changePassword.html', locals())

def Logout(request):
    logout(request)
    return redirect('index')

# New views for User Roles
def addUserRole(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    error = ""
    if request.method == "POST":
        username = request.POST['username']
        role = request.POST['role']
        permissions = request.POST.get('permissions', '')
        
        try:
            # Check if user exists
            user = User.objects.get(username=username)
            
            # Check if user role already exists
            role_exists = UserRole.objects.filter(user=user).exists()
            if role_exists:
                error = "exists"
            else:
                UserRole.objects.create(user=user, role=role, permissions=permissions)
                error = "no"
        except User.DoesNotExist:
            error = "user_not_found"
        except Exception as e:
            error = "yes"
            
    return render(request, 'addUserRole.html', locals())

def viewUserRoles(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    user_roles = UserRole.objects.all()
    return render(request, 'viewUserRoles.html', locals())

def edit_UserRole(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    error = ""
    user_role = UserRole.objects.get(id=pid)
    
    if request.method == "POST":
        role = request.POST['role']
        permissions = request.POST.get('permissions', '')
        
        try:
            user_role.role = role
            user_role.permissions = permissions
            user_role.save()
            error = "no"
        except:
            error = "yes"
    
    return render(request, 'edit_UserRole.html', locals())

def delete_UserRole(request, pid):
    user_role = UserRole.objects.get(id=pid)
    user_role.delete()
    return redirect('viewUserRoles')

# Views for Membership Plans
def addMembershipPlan(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    error = ""
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['description']
        duration_months = request.POST['duration_months']
        price = request.POST['price']
        features = request.POST.get('features', '')
        
        try:
            MembershipPlan.objects.create(
                name=name,
                description=description,
                duration_months=duration_months,
                price=price,
                features=features
            )
            error = "no"
        except:
            error = "yes"
    
    return render(request, 'addMembershipPlan.html', locals())

def viewMembershipPlans(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    membership_plans = MembershipPlan.objects.all()
    return render(request, 'viewMembershipPlans.html', locals())

def edit_MembershipPlan(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    error = ""
    plan = MembershipPlan.objects.get(id=pid)
    
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['description']
        duration_months = request.POST['duration_months']
        price = request.POST['price']
        features = request.POST.get('features', '')
        
        try:
            plan.name = name
            plan.description = description
            plan.duration_months = duration_months
            plan.price = price
            plan.features = features
            plan.save()
            error = "no"
        except:
            error = "yes"
    
    return render(request, 'edit_MembershipPlan.html', locals())

def delete_MembershipPlan(request, pid):
    plan = MembershipPlan.objects.get(id=pid)
    plan.delete()
    return redirect('viewMembershipPlans')

# Views for Attendance
def markAttendance(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    error = ""
    members = Member.objects.all()
    
    if request.method == "POST":
        member_id = request.POST['member']
        attendance_date = request.POST['date']
        check_in = request.POST['check_in']
        check_out = request.POST.get('check_out', None)
        note = request.POST.get('note', '')
        
        try:
            member = Member.objects.get(id=member_id)
            
            # Check if attendance for this member on this date already exists
            exists = Attendance.objects.filter(member=member, date=attendance_date).exists()
            
            if exists:
                attendance = Attendance.objects.get(member=member, date=attendance_date)
                attendance.check_in = check_in
                if check_out:
                    attendance.check_out = check_out
                attendance.note = note
                attendance.save()
            else:
                Attendance.objects.create(
                    member=member,
                    date=attendance_date,
                    check_in=check_in,
                    check_out=check_out if check_out else None,
                    note=note
                )
            error = "no"
        except:
            error = "yes"
    
    today = timezone.now().date()
    return render(request, 'markAttendance.html', locals())

def viewAttendance(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    attendance_records = None
    selected_member = None
    selected_date = None
    
    if request.method == "POST":
        if 'member' in request.POST:
            member_id = request.POST.get('member')
            if member_id:
                selected_member = Member.objects.get(id=member_id)
                attendance_records = Attendance.objects.filter(member=selected_member).order_by('-date')
        
        if 'date' in request.POST:
            date_str = request.POST.get('date')
            if date_str:
                selected_date = date_str
                attendance_records = Attendance.objects.filter(date=selected_date).order_by('member__name')
    
    if not attendance_records:
        # Default: show current month's attendance
        today = timezone.now().date()
        month_start = today.replace(day=1)
        attendance_records = Attendance.objects.filter(date__gte=month_start, date__lte=today).order_by('-date')
    
    members = Member.objects.all()
    return render(request, 'viewAttendance.html', locals())

def edit_Attendance(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    error = ""
    attendance = Attendance.objects.get(id=pid)
    members = Member.objects.all()
    
    if request.method == "POST":
        member_id = request.POST['member']
        attendance_date = request.POST['date']
        check_in = request.POST['check_in']
        check_out = request.POST.get('check_out', None)
        note = request.POST.get('note', '')
        
        try:
            member = Member.objects.get(id=member_id)
            
            attendance.member = member
            attendance.date = attendance_date
            attendance.check_in = check_in
            attendance.check_out = check_out if check_out else None
            attendance.note = note
            attendance.save()
            error = "no"
        except:
            error = "yes"
    
    return render(request, 'edit_Attendance.html', locals())

def delete_Attendance(request, pid):
    attendance = Attendance.objects.get(id=pid)
    attendance.delete()
    return redirect('viewAttendance')

# Views for Payments
def addPayment(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    error = ""
    members = Member.objects.all()
    
    if request.method == "POST":
        member_id = request.POST['member']
        amount = request.POST['amount']
        payment_date = request.POST['payment_date']
        payment_method = request.POST['payment_method']
        reference_number = request.POST.get('reference_number', '')
        notes = request.POST.get('notes', '')
        
        try:
            member = Member.objects.get(id=member_id)
            
            Payment.objects.create(
                member=member,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method,
                reference_number=reference_number,
                notes=notes
            )
            error = "no"
        except:
            error = "yes"
    
    today = timezone.now().date()
    return render(request, 'addPayment.html', locals())

def viewPayments(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    payments = None
    selected_member = None
    
    if request.method == "POST" and 'member' in request.POST:
        member_id = request.POST.get('member')
        if member_id:
            selected_member = Member.objects.get(id=member_id)
            payments = Payment.objects.filter(member=selected_member).order_by('-payment_date')
    
    if not payments:
        payments = Payment.objects.all().order_by('-payment_date')
    
    members = Member.objects.all()
    return render(request, 'viewPayments.html', locals())

def edit_Payment(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    error = ""
    payment = Payment.objects.get(id=pid)
    members = Member.objects.all()
    
    if request.method == "POST":
        member_id = request.POST['member']
        amount = request.POST['amount']
        payment_date = request.POST['payment_date']
        payment_method = request.POST['payment_method']
        reference_number = request.POST.get('reference_number', '')
        notes = request.POST.get('notes', '')
        
        try:
            member = Member.objects.get(id=member_id)
            
            payment.member = member
            payment.amount = amount
            payment.payment_date = payment_date
            payment.payment_method = payment_method
            payment.reference_number = reference_number
            payment.notes = notes
            payment.save()
            error = "no"
        except:
            error = "yes"
    
    return render(request, 'edit_Payment.html', locals())

def delete_Payment(request, pid):
    payment = Payment.objects.get(id=pid)
    payment.delete()
    return redirect('viewPayments')

def incomeReport(request, template_name='incomeReport.html'):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    # Add debug information
    user_info = json.dumps({
        'is_authenticated': request.user.is_authenticated,
        'username': request.user.username,
        'is_staff': request.user.is_staff
    })
    
    # Get current date
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Get selected month and year from form submission
    if request.method == 'POST':
        selected_month = int(request.POST.get('month', current_month))
        selected_year = int(request.POST.get('year', current_year))
    else:
        selected_month = int(request.GET.get('month', current_month))
        selected_year = int(request.GET.get('year', current_year))
    
    # Generate list of available years (last 5 years)
    available_years = list(range(current_year - 4, current_year + 1))
    
    # Get month name
    month_name = calendar.month_name[selected_month]
    
    try:
        # Filter payments for selected month and year
        payments = Payment.objects.filter(
            payment_date__month=selected_month,
            payment_date__year=selected_year
        ).order_by('payment_date')
        
        # Calculate monthly total
        monthly_total = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calculate yearly total
        yearly_payments = Payment.objects.filter(
            payment_date__year=selected_year
        )
        yearly_total = yearly_payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Add expiry date and plan details to payments
        for payment in payments:
            # Try to find associated plan info from notes or member plan
            if payment.notes and "plan" in payment.notes.lower():
                plan_name = payment.notes.split("payment")[0].strip()
                payment.plan_name = plan_name
            else:
                payment.plan_name = payment.member.plan if hasattr(payment.member, 'plan') else "--"
            
            # Calculate expiry date based on plan duration if available
            if hasattr(payment.member, 'plan'):
                plan = Plan.objects.filter(name=payment.member.plan).first()
                if plan and plan.duration:
                    try:
                        # Parse duration (e.g., "1 Month", "3 Months")
                        duration_parts = plan.duration.split()
                        if len(duration_parts) >= 1:
                            months = int(duration_parts[0])
                            expiry_date = payment.payment_date + timedelta(days=30*months)
                            payment.expiry_date = expiry_date
                            payment.validity = f"{months} {'Month' if months == 1 else 'Months'}"
                    except:
                        payment.expiry_date = None
                        payment.validity = plan.duration
                else:
                    payment.expiry_date = None
                    payment.validity = "--"
            else:
                payment.expiry_date = None
                payment.validity = "--"
        
        debug_info = {"success": True}
    except Exception as e:
        debug_info = {"success": False, "error": str(e)}
        payments = []
        monthly_total = 0
        yearly_total = 0
    
    return render(request, template_name, locals())

@csrf_protect
@ensure_csrf_cookie
def member_attendance_history(request):
    member, response = _member_guard(request)
    if response:
        return response

    selected_date = request.POST.get('date') or request.GET.get('date') or ''
    records = Attendance.objects.filter(member=member)
    if selected_date:
        try:
            records = records.filter(date=selected_date)
        except Exception:
            selected_date = ''
    else:
        today = timezone.now().date()
        records = records.filter(date__gte=today.replace(day=1), date__lte=today)
    records = list(records.order_by('-date', '-check_in'))
    for record in records:
        record.duration = _duration_text(record.check_in, record.check_out)

    return render(request, 'member_attendance.html', {
        'member': member, 'attendance_records': records,
        'selected_date': selected_date, 'active': 'attendance',
    })


def member_payment_history(request):
    member, response = _member_guard(request)
    if response:
        return response
    payments = Payment.objects.filter(member=member).order_by('-payment_date')
    total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'member_payments.html', {
        'member': member, 'payments': payments, 'total_paid': total_paid, 'active': 'payments',
    })


def member_plan_details(request):
    member, response = _member_guard(request)
    if response:
        return response
    current_plan = Plan.objects.filter(name=(member.plan or '').strip()).first()
    all_plans = Plan.objects.all()
    feature_list = [
        "Access to gym equipment",
        "Fitness consultation",
        "Locker access",
        "Workout tracking",
        "24/7 access",
    ]
    return render(request, 'member_plan.html', {
        'member': member, 'current_plan': current_plan, 'all_plans': all_plans,
        'feature_list': feature_list, 'active': 'plan',
    })


def member_equipment_list(request):
    member, response = _member_guard(request)
    if response:
        return response
    return render(request, 'member_equipment.html', {
        'member': member, 'equipment': Equipment.objects.all(), 'active': 'equipment',
    })


@csrf_protect
def member_submit_enquiry(request):
    member, response = _member_guard(request)
    if response:
        return response
    error = ""
    if request.method == "POST":
        try:
            Contact.objects.create(
                name=member.name,
                emailid=member.email,
                contact=member.contact,
                subject=request.POST.get('subject', ''),
                message=request.POST.get('message', ''),
                msgdate=date.today(),
                isread="no"
            )
            error = "no"
        except Exception as e:
            print(e)
            error = "yes"
    return render(request, 'member_enquiry.html', {'member': member, 'error': error, 'active': 'enquiry'})


@csrf_protect
def member_change_password(request):
    member, response = _member_guard(request)
    if response:
        return response
    error = ""
    if request.method == "POST":
        old = request.POST.get('oldpassword', '')
        new = request.POST.get('newpassword', '')
        if not request.user.check_password(old):
            error = 'not'
        elif len(new) < 4:
            error = 'short'
        else:
            request.user.set_password(new)
            request.user.save()
            update_session_auth_hash(request, request.user)  # keep the member logged in
            error = "no"
    return render(request, 'member_change_password.html', {'member': member, 'error': error, 'active': 'password'})
