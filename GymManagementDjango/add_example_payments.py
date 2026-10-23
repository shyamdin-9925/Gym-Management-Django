import os
import django
import random
import string
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymManagementDjango.settings')
django.setup()

from gym.models import Payment, Member, MembershipPlan
from django.utils import timezone
from decimal import Decimal

def generate_reference_number(length=10):
    """Generate a random alphanumeric reference number."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_payment_record(member, amount, payment_date, payment_method, reference_number=None, notes=None):
    """Create a payment record for a member."""
    try:
        if not reference_number and payment_method != 'cash':
            reference_number = generate_reference_number()
            
        # Create payment record
        payment = Payment.objects.create(
            member=member,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes
        )
        
        print(f"Created payment record for {member.name}: ₹{amount} on {payment_date} ({payment_method})")
        return payment
    except Exception as e:
        print(f"Error creating payment record for {member.name}: {e}")
        return None

# Map our payment methods to model's choices
PAYMENT_METHOD_MAP = {
    "Cash": "cash",
    "Credit Card": "credit_card",
    "Debit Card": "debit_card",
    "UPI": "online",
    "Net Banking": "bank_transfer"
}

# Get all members and plans
members = Member.objects.all()
plans = list(MembershipPlan.objects.all())

if not members:
    print("No members found in the database. Please add members first.")
elif not plans:
    print("No membership plans found in the database. Please add plans first.")
else:
    # Current date
    today = timezone.now().date()
    
    # Create payment records for each member
    for member in members:
        # Initial plan info
        plan_name = member.plan if hasattr(member, 'plan') and member.plan else None
        
        # Try to find matching plan or choose a random one
        plan = None
        if plan_name:
            matching_plans = [p for p in plans if p.name == plan_name]
            if matching_plans:
                plan = matching_plans[0]
                
        if not plan and plans:
            plan = random.choice(plans)
            
        if not plan:
            print(f"No plans available for {member.name}, skipping...")
            continue
            
        # Get join date from member or generate one
        join_date = member.joindate if hasattr(member, 'joindate') and member.joindate else today - timedelta(days=random.randint(30, 180))
        
        # Create an initial membership payment
        payment_method = random.choice(list(PAYMENT_METHOD_MAP.keys()))
        mapped_method = PAYMENT_METHOD_MAP[payment_method]
        
        reference = None
        if mapped_method != 'cash':
            reference = generate_reference_number()
            
        notes = f"Initial {plan.name} membership payment"
        
        try:
            # Try to use initial amount from member record
            if hasattr(member, 'initamount') and member.initamount:
                initial_amount = Decimal(member.initamount)
            else:
                initial_amount = plan.price
                
            create_payment_record(
                member=member,
                amount=initial_amount,
                payment_date=join_date,
                payment_method=mapped_method,
                reference_number=reference,
                notes=notes
            )
        except Exception as e:
            print(f"Error processing initial payment for {member.name}: {e}")
            continue
        
        # Add monthly payments if they've been a member for more than a month
        payment_date = join_date + timedelta(days=30)
        
        # Add up to 6 monthly payments
        for month in range(6):
            if payment_date >= today:
                break
                
            # Generate payment details
            payment_method = random.choice(list(PAYMENT_METHOD_MAP.keys()))
            mapped_method = PAYMENT_METHOD_MAP[payment_method]
            
            reference = None
            if mapped_method != 'cash':
                reference = generate_reference_number()
                
            # Sometimes apply a discount or late fee
            if random.random() < 0.1:
                discount = round(plan.price * Decimal('0.1'))  # 10% discount
                amount = plan.price - discount
                notes = f"Month {month+1} payment with loyalty discount"
            elif random.random() < 0.05:
                fee = round(plan.price * Decimal('0.05'))  # 5% late fee
                amount = plan.price + fee
                notes = f"Month {month+1} payment with late fee"
            else:
                amount = plan.price
                notes = f"Month {month+1} regular payment"
                
            create_payment_record(
                member=member,
                amount=amount,
                payment_date=payment_date,
                payment_method=mapped_method,
                reference_number=reference,
                notes=notes
            )
            
            payment_date += timedelta(days=30)  # Next month's payment
            
print("All example payment records have been created successfully!") 