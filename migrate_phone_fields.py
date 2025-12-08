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
        # Add phone column to donors table if it doesn't exist
        db.session.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='donors' AND column_name='phone'
                ) THEN
                    ALTER TABLE donors ADD COLUMN phone VARCHAR(20);
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
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='patients' AND column_name='pincode'
                ) THEN
                    ALTER TABLE patients ADD COLUMN pincode VARCHAR(10);
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
                END IF;
            END $$;
        """)
        
        db.session.commit()
        print("✅ Database migration completed successfully!")
        print("✅ Added phone field to donors and patients")
        print("✅ Removed address field from donors")
        print("✅ Removed location field from patients")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Migration failed: {e}")
        print("Note: If tables don't exist yet, this is normal for first deployment")
