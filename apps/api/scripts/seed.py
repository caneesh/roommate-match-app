"""
Seed script to populate database with sample data
Run with: python scripts/seed.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import SessionLocal, engine
from auth import get_password_hash
import models
from sqlalchemy.orm import Session


def seed_database():
    """Seed the database with sample data"""
    db = SessionLocal()

    try:
        print("🌱 Starting database seed...")

        # Create admin user
        admin = models.User(
            email="admin@leasepeace.com",
            hashed_password=get_password_hash("admin123"),
            name="Admin User",
            role=models.UserRole.ADMIN
        )
        db.add(admin)
        db.flush()
        print("✓ Created admin user")

        # Create operator org
        operator_org = models.OperatorOrg(
            name="Downtown Co-Living",
            contact_email="ops@downtowncoliving.com",
            subscription_tier="pilot"
        )
        db.add(operator_org)
        db.flush()
        print("✓ Created operator org")

        # Create operator user
        operator_user = models.User(
            email="operator@downtowncoliving.com",
            hashed_password=get_password_hash("operator123"),
            name="Jane Operator",
            role=models.UserRole.OPERATOR
        )
        db.add(operator_user)
        db.flush()

        # Link operator to org
        operator_member = models.OperatorMember(
            org_id=operator_org.id,
            user_id=operator_user.id,
            role="owner"
        )
        db.add(operator_member)
        print("✓ Created operator user")

        # Create property
        property_obj = models.Property(
            operator_org_id=operator_org.id,
            name="Downtown Commons",
            address="123 Main Street",
            city="San Francisco",
            state="CA",
            zip_code="94102",
            total_units=2
        )
        db.add(property_obj)
        db.flush()
        print("✓ Created property")

        # Create units
        unit1 = models.Unit(
            property_id=property_obj.id,
            unit_number="101",
            total_rooms=2,
            total_beds=4
        )
        db.add(unit1)
        db.flush()

        # Create rooms
        room1 = models.Room(
            unit_id=unit1.id,
            room_number="A",
            total_beds=2
        )
        room2 = models.Room(
            unit_id=unit1.id,
            room_number="B",
            total_beds=2
        )
        db.add_all([room1, room2])
        db.flush()

        # Create beds
        beds = [
            models.Bed(room_id=room1.id, bed_number="1"),
            models.Bed(room_id=room1.id, bed_number="2"),
            models.Bed(room_id=room2.id, bed_number="1"),
            models.Bed(room_id=room2.id, bed_number="2"),
        ]
        db.add_all(beds)
        db.flush()
        print("✓ Created units, rooms, and beds")

        # Create resident users with profiles
        residents_data = [
            {
                "email": "alice@example.com",
                "name": "Alice Johnson",
                "bio": "Software engineer who loves cooking and hiking",
                "questionnaire": {
                    "sleep_schedule_weekday": 3,  # Early bird
                    "sleep_schedule_weekend": 4,
                    "light_sensitivity": 6,
                    "noise_tolerance": 4,  # Prefers quiet
                    "quiet_hours_importance": 8,
                    "cleanliness_kitchen": 8,  # Very clean
                    "cleanliness_bathroom": 8,
                    "cleanliness_common": 7,
                    "chore_frequency": 5,
                    "clutter_tolerance": 3,
                    "guests_overnight_per_week": 1,
                    "partner_frequency": 3,
                    "party_frequency": 1,
                    "social_level_home": 4,
                    "introvert_extrovert": 3,  # Introvert
                    "thermostat_preference": 68,
                    "thermostat_flexibility": 6,
                    "wfh_frequency": 5,
                    "shared_space_work_need": 7,
                    "food_sharing_comfort": 3,
                    "toiletries_sharing_comfort": 2,
                    "borrowing_comfort": 4,
                    "has_pets": False,
                    "pet_types": [],
                    "has_allergies": True,
                    "allergy_details": ["cats"],
                    "smoking_tolerance": 0,
                    "vaping_tolerance": 0,
                    "drug_tolerance": 0,
                    "alcohol_comfort": 6,
                    "communication_directness": 8,
                    "communication_channel": "text",
                    "response_time_expectation": 12,
                    "conflict_style": "collaborative",
                    "budget_stress": 6,
                    "expense_splitting_preference": "equal",
                    "spirituality_importance": 3,
                    "political_discussion_comfort": 5,
                    "sustainability_importance": 8,
                    "dealbreakers": ["no_smoking", "no_pets"],
                    "flexible_on": ["thermostat", "guest_schedule"],
                }
            },
            {
                "email": "bob@example.com",
                "name": "Bob Smith",
                "bio": "Designer and musician, night owl",
                "questionnaire": {
                    "sleep_schedule_weekday": 8,  # Night owl
                    "sleep_schedule_weekend": 9,
                    "light_sensitivity": 3,
                    "noise_tolerance": 8,  # Tolerates noise
                    "quiet_hours_importance": 4,
                    "cleanliness_kitchen": 5,  # Moderate
                    "cleanliness_bathroom": 6,
                    "cleanliness_common": 5,
                    "chore_frequency": 3,
                    "clutter_tolerance": 7,
                    "guests_overnight_per_week": 3,
                    "partner_frequency": 7,
                    "party_frequency": 5,
                    "social_level_home": 8,
                    "introvert_extrovert": 8,  # Extrovert
                    "thermostat_preference": 72,
                    "thermostat_flexibility": 7,
                    "wfh_frequency": 2,
                    "shared_space_work_need": 4,
                    "food_sharing_comfort": 7,
                    "toiletries_sharing_comfort": 5,
                    "borrowing_comfort": 8,
                    "has_pets": False,
                    "pet_types": [],
                    "has_allergies": False,
                    "allergy_details": [],
                    "smoking_tolerance": 3,
                    "vaping_tolerance": 4,
                    "drug_tolerance": 2,
                    "alcohol_comfort": 9,
                    "communication_directness": 6,
                    "communication_channel": "any",
                    "response_time_expectation": 48,
                    "conflict_style": "compromising",
                    "budget_stress": 4,
                    "expense_splitting_preference": "flexible",
                    "spirituality_importance": 2,
                    "political_discussion_comfort": 7,
                    "sustainability_importance": 5,
                    "dealbreakers": [],
                    "flexible_on": ["cleanliness", "noise", "guests"],
                }
            },
            {
                "email": "carol@example.com",
                "name": "Carol Davis",
                "bio": "Teacher who values quiet and cleanliness",
                "questionnaire": {
                    "sleep_schedule_weekday": 2,  # Very early bird
                    "sleep_schedule_weekend": 3,
                    "light_sensitivity": 8,
                    "noise_tolerance": 2,  # Very quiet
                    "quiet_hours_importance": 9,
                    "cleanliness_kitchen": 9,  # Very clean
                    "cleanliness_bathroom": 9,
                    "cleanliness_common": 8,
                    "chore_frequency": 6,
                    "clutter_tolerance": 2,
                    "guests_overnight_per_week": 0,
                    "partner_frequency": 2,
                    "party_frequency": 0,
                    "social_level_home": 2,
                    "introvert_extrovert": 2,  # Introvert
                    "thermostat_preference": 69,
                    "thermostat_flexibility": 4,
                    "wfh_frequency": 1,
                    "shared_space_work_need": 3,
                    "food_sharing_comfort": 2,
                    "toiletries_sharing_comfort": 1,
                    "borrowing_comfort": 3,
                    "has_pets": False,
                    "pet_types": [],
                    "has_allergies": True,
                    "allergy_details": ["dust", "cats"],
                    "smoking_tolerance": 0,
                    "vaping_tolerance": 0,
                    "drug_tolerance": 0,
                    "alcohol_comfort": 4,
                    "communication_directness": 9,
                    "communication_channel": "text",
                    "response_time_expectation": 6,
                    "conflict_style": "assertive",
                    "budget_stress": 7,
                    "expense_splitting_preference": "equal",
                    "spirituality_importance": 7,
                    "political_discussion_comfort": 3,
                    "sustainability_importance": 9,
                    "dealbreakers": ["no_smoking", "no_pets", "no_parties", "no_overnight_guests"],
                    "flexible_on": [],
                }
            },
        ]

        for data in residents_data:
            # Create user
            user = models.User(
                email=data["email"],
                hashed_password=get_password_hash("password123"),
                name=data["name"],
                role=models.UserRole.RESIDENT
            )
            db.add(user)
            db.flush()

            # Create profile
            profile = models.ResidentProfile(
                user_id=user.id,
                bio=data["bio"],
                profile_complete=True,
                questionnaire_completed=True
            )
            db.add(profile)
            db.flush()

            # Create questionnaire
            questionnaire = models.QuestionnaireAnswers(
                resident_id=profile.id,
                **data["questionnaire"]
            )
            db.add(questionnaire)

            # Add to applicant pool
            applicant = models.ApplicantPool(
                resident_id=profile.id,
                property_id=property_obj.id,
                status="approved"
            )
            db.add(applicant)

        print("✓ Created 3 resident users with profiles and questionnaires")

        db.commit()
        print("\n✅ Database seeded successfully!")
        print("\n📝 Login credentials:")
        print("   Admin: admin@leasepeace.com / admin123")
        print("   Operator: operator@downtowncoliving.com / operator123")
        print("   Resident 1: alice@example.com / password123")
        print("   Resident 2: bob@example.com / password123")
        print("   Resident 3: carol@example.com / password123")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    seed_database()
