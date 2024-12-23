from fastapi import APIRouter, UploadFile, File, Query, HTTPException, Depends
import csv
from sqlalchemy.orm import Session
from app.models import Business, Symptom, BusinessSymptom
from app.database import engine , get_db
from app.utils import import_csv ,  import_csv_per_record
import os
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

@router.post("/import-csv")
async def import_csv_endpoint(file: UploadFile = File(...) , db: Session = Depends(get_db)):
    temp_dir = None
    file_path = None

    try:

        base_dir=os.getenv("BASE_DIR")
        if not base_dir:
            raise HTTPException(status_code=500,detail="BASE_DIR is not set")
        
        temp_dir = os.path.join(base_dir, "temp") 
        os.makedirs(temp_dir, exist_ok=True)  
        # print(base_dir)
        # print(temp_dir)
        

        # Save the file in the temp directory
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Call the CSV import logic
        import_csv(file_path,db)

        # if you want rejection specific to record
        # import_csv_per_record(file_path,db)
        return {"message": "CSV imported successfully!"}

    except FileNotFoundError as fnf_error:
        raise HTTPException(status_code=500, detail="Failed to create or write to the temporary file.")
    except PermissionError as perm_error:
        raise HTTPException(status_code=500, detail="Permission error while handling the file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    finally:
        # Cleanup: Remove the temporary file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as cleanup_error:
                print(f"Error during cleanup: {cleanup_error}")


@router.get("/symptom-data")
async def get_symptom_data(
    business_id: int = Query(None),
    symptom_diagnostic: bool = Query(None),
    db: Session = Depends(get_db),

):
    # session = Session(bind=engine)

    try:
        # Base query joining the three tables
        query = db.query(
            Business.business_id,
            Business.business_name,
            Symptom.symptom_code,
            Symptom.symptom_name,
            BusinessSymptom.symptom_diagnostic
        ).join(
            BusinessSymptom, Business.business_id == BusinessSymptom.business_id
        ).join(
            Symptom, Symptom.symptom_code == BusinessSymptom.symptom_code
        ).filter(
            or_(Business.business_id == business_id, business_id is None),
            or_(BusinessSymptom.symptom_diagnostic == symptom_diagnostic, symptom_diagnostic is None),
        )

        # convert it to JSON type
        results = [
            {
                "business_id": row[0],
                "business_name": row[1],
                "symptom_code": row[2],
                "symptom_name": row[3],
                "symptom_diagnostic": row[4],
            }
            for row in query.all()
        ]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="An error occurred while querying the database.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    # finally:
    #     session.close()

    return results



@router.get('/status')
async def get_status():
    try:
        
        return {"Health OK"}

    except Exception as e:
        return {'Error: ' + str(e)}

