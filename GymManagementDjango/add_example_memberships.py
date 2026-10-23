import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymManagementDjango.settings')
django.setup()

from gym.models import MembershipPlan
from decimal import Decimal

def create_membership_plan(name, description, duration_months, price, features):
    """Create a membership plan if it doesn't already exist."""
    try:
        # Check if plan already exists with same name
        existing_plan = MembershipPlan.objects.filter(name=name).first()
        if existing_plan:
            print(f"Plan '{name}' already exists.")
            return existing_plan
        
        # Create new plan
        plan = MembershipPlan.objects.create(
            name=name,
            description=description,
            duration_months=duration_months,
            price=Decimal(price),
            features=features
        )
        print(f"Created membership plan: {name} - ₹{price} for {duration_months} months")
        return plan
    except Exception as e:
        print(f"Error creating plan '{name}': {e}")
        return None

# Example 1: Basic Plan
create_membership_plan(
    name="Basic Fitness",
    description="Our starter membership with access to basic equipment and facilities",
    duration_months=1,
    price="1499",
    features="Gym access,Basic equipment,Locker rooms,Free water"
)

# Example 2: Standard Plan
create_membership_plan(
    name="Standard Fitness",
    description="Our most popular membership with additional access to cardio classes",
    duration_months=3,
    price="3999",
    features="Gym access,All equipment,Group fitness classes,Locker rooms,Free water,Towel service"
)

# Example 3: Premium Plan
create_membership_plan(
    name="Premium Fitness",
    description="Comprehensive fitness package with all amenities and personal training sessions",
    duration_months=6,
    price="6999",
    features="24/7 Gym access,All equipment,All classes,Personal training (2 sessions),Sauna,Massage chairs,Nutrition consultation"
)

# Example 4: Elite Plan
create_membership_plan(
    name="Elite Fitness",
    description="The ultimate fitness experience with unlimited training and premium amenities",
    duration_months=12,
    price="11999",
    features="24/7 Gym access,All equipment,Unlimited classes,Personal training (5 sessions),Sauna,Swimming pool,Nutrition plan,Body composition analysis"
)

# Example 5: Student Plan
create_membership_plan(
    name="Student Special",
    description="Special discounted membership for students with valid ID",
    duration_months=3,
    price="2499",
    features="Gym access,Basic equipment,Group classes (3 per week),Valid student ID required"
)

print("All example membership plans have been created successfully!") 