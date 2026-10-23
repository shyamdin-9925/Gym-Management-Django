import os
import django
import random
from datetime import datetime, timedelta, time

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymManagementDjango.settings')
django.setup()

from django.contrib.auth.models import User
from gym.models import Attendance, Member
from django.utils import timezone

def create_attendance_record(member, date, check_in, check_out, note="Regular workout"):
    """Create an attendance record for a member."""
    try:
        # Check if record already exists
        existing_record = Attendance.objects.filter(
            member=member, 
            date=date
        ).first()
        
        if existing_record:
            print(f"Attendance record for {member.name} on {date} already exists.")
            return existing_record
        
        # Create new attendance record
        record = Attendance.objects.create(
            member=member,
            date=date,
            check_in=check_in,
            check_out=check_out,
            note=note
        )
        print(f"Created attendance record for {member.name} on {date}")
        return record
    except Exception as e:
        print(f"Error creating attendance record for {member.name}: {e}")
        return None

def generate_random_time(start_hour=6, end_hour=22):
    """Generate a random time between start_hour and end_hour."""
    hour = random.randint(start_hour, end_hour)
    minute = random.randint(0, 59)
    return time(hour, minute)

def create_month_attendance(member, start_date, days=30):
    """Create attendance records for a member for a month."""
    current_date = start_date
    
    # Simulate realistic attendance patterns
    for day in range(days):
        # Randomly skip some days (30% chance)
        if random.random() < 0.3:
            current_date += timedelta(days=1)
            continue
            
        check_in = generate_random_time(6, 18)  # Check in between 6 AM and 6 PM
        
        # Calculate checkout time (1-3 hours after check in)
        hours_stayed = random.randint(1, 3)
        check_out_hour = min(check_in.hour + hours_stayed, 22)  # Gym closes at 10 PM
        check_out = time(check_out_hour, random.randint(0, 59))
        
        # Generate a realistic note
        workout_types = ["Cardio", "Weight Training", "Yoga", "CrossFit", "HIIT", "Swimming", "Zumba"]
        notes = [
            f"Regular {random.choice(workout_types)} session",
            "Personal training session",
            "Group class attendance",
            "Used the pool",
            "Used the sauna",
            "Fitness assessment",
            ""
        ]
        
        note = random.choice(notes)
            
        create_attendance_record(
            member=member,
            date=current_date,
            check_in=check_in,
            check_out=check_out,
            note=note
        )
        
        current_date += timedelta(days=1)

# Get all members
members = Member.objects.all()

if not members:
    print("No members found in the database. Please add members first.")
else:
    # Create attendance for the last month for each member
    today = timezone.now().date()
    start_date = today - timedelta(days=30)  # Start from 30 days ago
    
    for member in members:
        print(f"Creating attendance records for {member.name}...")
        create_month_attendance(member, start_date)

print("All example attendance records have been created successfully!") 