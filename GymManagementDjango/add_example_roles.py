import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymManagementDjango.settings')
django.setup()

from django.contrib.auth.models import User
from gym.models import UserRole

def create_user_if_not_exists(username, email, password, is_staff=True):
    """Create a user if it doesn't exist."""
    try:
        user = User.objects.get(username=username)
        print(f"User {username} already exists.")
        return user
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff
        )
        print(f"Created user: {username}")
        return user

def create_user_role(username, email, password, role, permissions):
    """Create a user with the specified role and permissions."""
    user = create_user_if_not_exists(username, email, password)
    
    # Check if user role already exists
    try:
        user_role = UserRole.objects.get(user=user)
        user_role.role = role
        user_role.permissions = permissions
        user_role.save()
        print(f"Updated role for {username} to {role} with permissions: {permissions}")
    except UserRole.DoesNotExist:
        UserRole.objects.create(
            user=user,
            role=role,
            permissions=permissions
        )
        print(f"Created role for {username}: {role} with permissions: {permissions}")

# Define example permissions for each role
ADMIN_PERMISSIONS = "all_access,manage_users,manage_roles,manage_finances,manage_equipment,manage_plans,view_reports"
MANAGER_PERMISSIONS = "manage_members,manage_trainers,manage_schedules,view_reports,manage_equipment,manage_plans"
TRAINER_PERMISSIONS = "view_members,view_schedules,mark_attendance,update_member_progress,create_workout_plans"
RECEPTIONIST_PERMISSIONS = "view_members,register_members,collect_payments,mark_attendance,handle_enquiries"

# Admin examples
create_user_role(
    "admin1", 
    "admin1@gym.com", 
    "admin123", 
    "admin", 
    ADMIN_PERMISSIONS
)

create_user_role(
    "admin2", 
    "admin2@gym.com", 
    "admin123", 
    "admin", 
    "all_access,manage_users,manage_roles,view_finances,manage_equipment"
)

create_user_role(
    "admin3", 
    "admin3@gym.com", 
    "admin123", 
    "admin", 
    "manage_users,manage_roles,manage_plans,view_reports,approve_memberships"
)

create_user_role(
    "admin4", 
    "admin4@gym.com", 
    "admin123", 
    "admin", 
    "manage_users,manage_equipment,manage_plans,approve_finances,view_all_reports"
)

# Manager examples
create_user_role(
    "manager1", 
    "manager1@gym.com", 
    "manager123", 
    "manager", 
    MANAGER_PERMISSIONS
)

create_user_role(
    "manager2", 
    "manager2@gym.com", 
    "manager123", 
    "manager", 
    "manage_members,manage_trainers,view_reports,handle_member_issues"
)

create_user_role(
    "manager3", 
    "manager3@gym.com", 
    "manager123", 
    "manager", 
    "manage_schedules,view_reports,manage_equipment,handle_special_events"
)

create_user_role(
    "manager4", 
    "manager4@gym.com", 
    "manager123", 
    "manager", 
    "manage_members,view_reports,manage_plans,organize_classes"
)

# Trainer examples
create_user_role(
    "trainer1", 
    "trainer1@gym.com", 
    "trainer123", 
    "trainer", 
    TRAINER_PERMISSIONS
)

create_user_role(
    "trainer2", 
    "trainer2@gym.com", 
    "trainer123", 
    "trainer", 
    "view_members,view_schedules,mark_attendance,create_nutrition_plans"
)

create_user_role(
    "trainer3", 
    "trainer3@gym.com", 
    "trainer123", 
    "trainer", 
    "view_members,mark_attendance,update_member_progress,lead_group_classes"
)

create_user_role(
    "trainer4", 
    "trainer4@gym.com", 
    "trainer123", 
    "trainer", 
    "view_schedules,mark_attendance,update_member_progress,personal_training"
)

# Receptionist examples
create_user_role(
    "receptionist1", 
    "receptionist1@gym.com", 
    "receptionist123", 
    "receptionist", 
    RECEPTIONIST_PERMISSIONS
)

create_user_role(
    "receptionist2", 
    "receptionist2@gym.com", 
    "receptionist123", 
    "receptionist", 
    "view_members,register_members,manage_locker_assignments,handle_enquiries"
)

create_user_role(
    "receptionist3", 
    "receptionist3@gym.com", 
    "receptionist123", 
    "receptionist", 
    "view_members,collect_payments,handle_phone_calls,print_member_cards"
)

create_user_role(
    "receptionist4", 
    "receptionist4@gym.com", 
    "receptionist123", 
    "receptionist", 
    "register_members,collect_payments,handle_member_complaints,schedule_appointments"
)

print("All example user roles have been created successfully!") 