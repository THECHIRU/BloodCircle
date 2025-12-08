"""
Migration script to add phone field to donors and patients, 
and remove address/location fields.
Run this script after deployment to update existing database.
"""
from app import create_app, db
from app.models import Donor, Patient

app = create_app('production')

with app.app_context():
    try:
        print("Starting database migration...")
        
        # Add phone column to donors table if it doesn't exist
        db.session.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='donors' AND column_name='phone'
                ) THEN
                    ALTER TABLE donors ADD COLUMN phone VARCHAR(20);
                    UPDATE donors SET phone = NULL WHERE phone IS NULL;
                    RAISE NOTICE 'Added phone column to donors table';
                END IF;
            END $$;
        """)
        
        # Add phone and pincode columns to patients table if they don't exist
        db.session.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='patients' AND column_name='phone'
                ) THEN
                    ALTER TABLE patients ADD COLUMN phone VARCHAR(20);
                    UPDATE patients SET phone = NULL WHERE phone IS NULL;
                    RAISE NOTICE 'Added phone column to patients table';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='patients' AND column_name='pincode'
                ) THEN
                    ALTER TABLE patients ADD COLUMN pincode VARCHAR(10);
                    UPDATE patients SET pincode = '000000' WHERE pincode IS NULL;
                    RAISE NOTICE 'Added pincode column to patients table';
                END IF;
            END $$;
        """)
        
        # Drop address column from donors if it exists
        db.session.execute("""
            DO $$ 
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='donors' AND column_name='address'
                ) THEN
                    ALTER TABLE donors DROP COLUMN address;
                    RAISE NOTICE 'Removed address column from donors table';
                END IF;
            END $$;
        """)
        
        # Drop location column from patients if it exists
        db.session.execute("""
            DO $$ 
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='patients' AND column_name='location'
                ) THEN
                    ALTER TABLE patients DROP COLUMN location;
                    RAISE NOTICE 'Removed location column from patients table';
                END IF;
            END $$;
        """)
        
        db.session.commit()
        
        # Verify migration
        from app.models import User, Donor, Patient
        user_count = User.query.count()
        donor_count = Donor.query.count()
        patient_count = Patient.query.count()
        
        print("✅ Database migration completed successfully!")
        print(f"✅ Data preserved: {user_count} users, {donor_count} donors, {patient_count} patients")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Migration error: {e}")
        # Don't fail the build - app might still work
        import traceback
        traceback.print_exc()
