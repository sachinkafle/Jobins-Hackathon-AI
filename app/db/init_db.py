import asyncio
from sqlalchemy import text
from app.db.database import engine, Base
from app.models.db_models import CandidatePool, Job, SelectionHistory

async def init_models():
    async with engine.begin() as conn:
        # 1. Create missing tables
        print("Creating missing tables...")
        await conn.run_sync(Base.metadata.create_all)
        
        # 2. Add 'embedding' column to pb_job if it doesn't exist
        print("Checking for missing columns...")
        try:
            # Check if embedding column exists in pb_job
            result = await conn.execute(text("SHOW COLUMNS FROM pb_job LIKE 'embedding'"))
            column_exists = result.fetchone()
            
            if not column_exists:
                print("Adding 'embedding' column to pb_job...")
                await conn.execute(text("ALTER TABLE pb_job ADD COLUMN embedding JSON"))
                print("Column 'embedding' added successfully to pb_job.")
            else:
                print("Column 'embedding' already exists in pb_job.")

            # Check if embedding column exists in candidate_pool
            result2 = await conn.execute(text("SHOW COLUMNS FROM candidate_pool LIKE 'embedding'"))
            column_exists2 = result2.fetchone()
            
            if not column_exists2:
                print("Adding 'embedding' column to candidate_pool...")
                await conn.execute(text("ALTER TABLE candidate_pool ADD COLUMN embedding JSON"))
                print("Column 'embedding' added successfully to candidate_pool.")
            else:
                print("Column 'embedding' already exists in candidate_pool.")
                
        except Exception as e:
            print(f"Migration notice: {e}")
            
        print("Database is up to date!")

if __name__ == "__main__":
    asyncio.run(init_models())
