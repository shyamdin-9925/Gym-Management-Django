import os
import django
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymManagementDjango.settings')
django.setup()

from gym.models import Member, Plan
from django.utils import timezone

def create_member(name, contact, email, gender, plan_name, join_date, initial_amount):
    """Create a member if they don't already exist."""
    try:
        # Check if member already exists
        existing_member = Member.objects.filter(email=email).first()
        if existing_member:
            print(f"Member with email {email} already exists.")
            return existing_member
        
        # Create new member
        member = Member.objects.create(
            name=name,
            contact=contact,
            email=email,
            gender=gender,
            plan=plan_name,
            joindate=join_date,
            initamount=initial_amount
        )
        print(f"Created member: {name} ({gender}) - Plan: {plan_name}")
        return member
    except Exception as e:
        print(f"Error creating member {name}: {e}")
        return None

# Get available plans
plans = list(Plan.objects.all())
if not plans:
    print("No plans found. Creating a default plan.")
    default_plan = Plan.objects.create(
        name="Basic Plan",
        amount="1500",
        duration="1 Month"
    )
    plans = [default_plan]

# List of member data with Indian names
members_data = [
    {
        "name": "Rajesh Kumar",
        "contact": "9876543210",
        "email": "rajesh.kumar@example.com",
        "gender": "Male",
        "join_date": timezone.now().date() - timedelta(days=random.randint(30, 180))
    },
    {
        "name": "Priya Sharma",
        "contact": "9876543211",
        "email": "priya.sharma@example.com",
        "gender": "Female",
        "join_date": timezone.now().date() - timedelta(days=random.randint(30, 180))
    },
    {
        "name": "Amit Patel",
        "contact": "9876543212",
        "email": "amit.patel@example.com",
        "gender": "Male",
        "join_date": timezone.now().date() - timedelta(days=random.randint(30, 180))
    },
    {
        "name": "Neha Singh",
        "contact": "9876543213",
        "email": "neha.singh@example.com",
        "gender": "Female",
        "join_date": timezone.now().date() - timedelta(days=random.randint(30, 180))
    },
    {
        "name": "Vijay Malhotra",
        "contact": "9876543214",
        "email": "vijay.malhotra@example.com",
        "gender": "Male",
        "join_date": timezone.now().date() - timedelta(days=random.randint(30, 180))
    },
    {
        "name": "Deepika Verma",
        "contact": "9876543215",
        "email": "deepika.verma@example.com",
        "gender": "Female",
        "join_date": timezone.now().date() - timedelta(days=random.randint(30, 180))
    },
    {
        "name": "Manish Joshi",
        "contact": "9876543216",
        "email": "manish.joshi@example.com",
        "gender": "Male",
        "join_date": timezone.now().date() - timedelta(days=random.randint(30, 180))
    },
    {
        "name": "Anjali Gupta",
        "contact": "9876543217",
        "email": "anjali.gupta@example.com",
        "gender": "Female",
        "join_date": timezone.now().date() - timedelta(days=random.randint(30, 180))
    },
    {
        "name": "Rahul Mehra",
        "contact": "9876543218",
        "email": "rahul.mehra@example.com",
        "gender": "Male",
        "join_date": timezone.now().date() - timedelta(days=random.randint(30, 180))
    },
    {
        "name": "Pooja Reddy",
        "contact": "9876543219",
        "email": "pooja.reddy@example.com",
        "gender": "Female",
        "join_date": timezone.now().date() - timedelta(days=random.randint(30, 180))
    }
]

# Create members
for member_data in members_data:
    # Choose a random plan
    plan = random.choice(plans)
    plan_name = plan.name
    
    # Generate a random initial amount (±10% of plan amount)
    base_amount = int(plan.amount)
    variation = random.uniform(0.9, 1.1)
    initial_amount = str(int(base_amount * variation))
    
    create_member(
        name=member_data["name"],
        contact=member_data["contact"],
        email=member_data["email"],
        gender=member_data["gender"],
        plan_name=plan_name,
        join_date=member_data["join_date"],
        initial_amount=initial_amount
    )

print("All example members have been created successfully!") 