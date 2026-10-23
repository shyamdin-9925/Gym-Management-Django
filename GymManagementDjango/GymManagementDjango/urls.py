"""GymManagementDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from gym.views import *
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('admin_login', admin_login, name='admin_login'),
    path('admin_home', admin_home, name='admin_home'),
    path('logout/', Logout, name='logout'),
    path('changePassword', changePassword, name='changePassword'),
    
    # Member URLs
    path('member_login', member_login, name='member_login'),
    path('member_dashboard', member_dashboard, name='member_dashboard'),
    path('update_member_profile', update_member_profile, name='update_member_profile'),
    path('member_attendance_history', member_attendance_history, name='member_attendance_history'),
    path('member_payment_history', member_payment_history, name='member_payment_history'),
    path('member_plan_details', member_plan_details, name='member_plan_details'),
    path('member_equipment_list', member_equipment_list, name='member_equipment_list'),
    path('member_submit_enquiry', member_submit_enquiry, name='member_submit_enquiry'),
    path('member_change_password', member_change_password, name='member_change_password'),
    
    path('addEnquiry', addEnquiry, name='addEnquiry'),
    path('viewEnquiry', viewEnquiry, name='viewEnquiry'),
    path('edit_Enquiry/<int:pid>', edit_Enquiry, name='edit_Enquiry'),
    path('delete_Enquiry/<int:pid>', delete_Enquiry, name='delete_Enquiry'),
    
    path('addPlan', addPlan, name='addPlan'),
    path('viewPlan', viewPlan, name='viewPlan'),
    path('edit_Plan/<int:pid>', edit_Plan, name='edit_Plan'),
    path('delete_Plan/<int:pid>', delete_Plan, name='delete_Plan'),
    
    path('addEquipment', addEquipment, name='addEquipment'),
    path('viewEquipment', viewEquipment, name='viewEquipment'),
    path('edit_Equipment/<int:pid>', edit_Equipment, name='edit_Equipment'),
    path('delete_Equipment/<int:pid>', delete_Equipment, name='delete_Equipment'),
    
    path('addMember', addMember, name='addMember'),
    path('viewMember', viewMember, name='viewMember'),
    path('edit_Member/<int:pid>', edit_Member, name='edit_Member'),
    path('delete_Member/<int:pid>', delete_Member, name='delete_Member'),
    
    path('contact', contact, name='contact'),
    path('unread_queries', unread_queries, name='unread_queries'),
    path('read_queries', read_queries, name='read_queries'),
    path('view_queries/<int:pid>', view_queries, name='view_queries'),
    path('delete_contact/<int:pid>', delete_contact, name='delete_contact'),
    
    # New URL Patterns for User Roles
    path('addUserRole', addUserRole, name='addUserRole'),
    path('viewUserRoles', viewUserRoles, name='viewUserRoles'),
    path('edit_UserRole/<int:pid>', edit_UserRole, name='edit_UserRole'),
    path('delete_UserRole/<int:pid>', delete_UserRole, name='delete_UserRole'),
    
    # New URL Patterns for Membership Plans
    path('addMembershipPlan', addMembershipPlan, name='addMembershipPlan'),
    path('viewMembershipPlans', viewMembershipPlans, name='viewMembershipPlans'),
    path('edit_MembershipPlan/<int:pid>', edit_MembershipPlan, name='edit_MembershipPlan'),
    path('delete_MembershipPlan/<int:pid>', delete_MembershipPlan, name='delete_MembershipPlan'),
    
    # New URL Patterns for Attendance
    path('markAttendance', markAttendance, name='markAttendance'),
    path('viewAttendance', viewAttendance, name='viewAttendance'),
    path('edit_Attendance/<int:pid>', edit_Attendance, name='edit_Attendance'),
    path('delete_Attendance/<int:pid>', delete_Attendance, name='delete_Attendance'),
    
    # New URL Patterns for Payments
    path('addPayment', addPayment, name='addPayment'),
    path('viewPayments', viewPayments, name='viewPayments'),
    path('edit_Payment/<int:pid>', edit_Payment, name='edit_Payment'),
    path('delete_Payment/<int:pid>', delete_Payment, name='delete_Payment'),
    
    # New URL Pattern for Reports
    path('incomeReport', incomeReport, name='incomeReport'),
    
    # Debug routes
    path('test_income', lambda request: render(request, 'test_income.html'), name='test_income'),
    path('simple_income', lambda request: incomeReport(request, template_name='simple_income_report.html'), name='simple_income'),
]
