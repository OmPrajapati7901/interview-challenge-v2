import csv
import os
from sqlalchemy.orm import Session
from app.models import Business, Symptom, BusinessSymptom
from app.database import engine, get_db  
from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import boto3

required_columns = {"Business ID", "Business Name", "Symptom Code", "Symptom Name", "Symptom Diagnostic"}

# AWS S3 Configuration
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")  
AWS_S3_REGION = os.getenv("AWS_S3_REGION")  
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")  
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")  


#as requeted in challenge
def import_csv(file_path: str,db :Session=Depends(get_db)):
    
    # session = Session(bind=engine)

    try:
        
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            
            validate_required_columns(reader.fieldnames, required_columns)
            
            for row in reader:

                validate_csv_row(row, required_columns)
                # Add Business
                business = db.query(Business).filter_by(business_id=row["Business ID"]).first()
                if not business:
                    business = Business(
                        business_id=row["Business ID"],
                        business_name=row["Business Name"]
                    )
                    db.add(business)
                    db.flush()

                # Add Symptom
                symptom = db.query(Symptom).filter_by(symptom_code=row["Symptom Code"]).first()
                if not symptom:
                    symptom = Symptom(
                        symptom_code=row["Symptom Code"],
                        symptom_name=row["Symptom Name"]
                    )
                    db.add(symptom)
                    db.flush()

                # Add Relationship
                business_symptom = BusinessSymptom(
                    business_id=business.business_id,
                    symptom_code=symptom.symptom_code,
                    symptom_diagnostic=row["Symptom Diagnostic"].strip().lower() in ["true", "yes"]
                )
                db.add(business_symptom)

            db.commit()

    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Invalid data: Duplicate entry detected") from e
    except FileNotFoundError as fnf_error:
        raise ValueError("The specified file could not be found.") from fnf_error
    except ValueError as val_error:
        db.rollback()
        raise ValueError(f"Invalid data: {val_error}") from val_error
    except SQLAlchemyError as db_error:
        db.rollback()
        raise RuntimeError("An error occurred while interacting with the database.") from db_error
    except Exception as e:
        # print("from Exception in utils", str(e))
        db.rollback()
        raise RuntimeError("An unexpected error occurred while importing the CSV.") from e
    finally:
        db.close()


# # if you want rejection specific to record

def import_csv_per_record(file_path: str, db: Session = Depends(get_db)):
    # session = Session(bind=engine)

    #output file path
    output_dir = os.path.join(os.path.dirname(file_path), "output")
    os.makedirs(output_dir, exist_ok=True)  
    output_path = os.path.join(output_dir, os.path.basename(file_path))


    output_rows = []

    try:
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            
            validate_required_columns(reader.fieldnames, required_columns)

            fieldnames = reader.fieldnames + ["Result"]
            
            for row in reader:
                try:
                   
                    validate_csv_row(row, required_columns)

                    # Add or get Business
                    business = db.query(Business).filter_by(business_id=row["Business ID"]).first()
                    if not business:
                        business = Business(
                            business_id=row["Business ID"],
                            business_name=row["Business Name"]
                        )
                        db.add(business)
                        db.flush()

                    # Add or get Symptom
                    symptom = db.query(Symptom).filter_by(symptom_code=row["Symptom Code"]).first()
                    if not symptom:
                        symptom = Symptom(
                            symptom_code=row["Symptom Code"],
                            symptom_name=row["Symptom Name"]
                        )
                        db.add(symptom)
                        db.flush()

                    # Add Relationship
                    business_symptom = BusinessSymptom(
                        business_id=business.business_id,
                        symptom_code=symptom.symptom_code,
                        symptom_diagnostic=row["Symptom Diagnostic"].strip().lower() in ["true", "yes"]
                    )
                    db.add(business_symptom)

                    # Commit after each row for partial updates
                    db.commit()

                    # Append success result
                    row["Result"] = "Success"
                except IntegrityError as e:
                    db.rollback()
                    row["Result"] = f"Error: Duplicate entry"
                except ValueError as val_err:
                    row["Result"] = f"Error: Validation"
                except SQLAlchemyError as db_err:
                    db.rollback()
                    row["Result"] = f"Error: Database"
                except Exception as ex:
                    db.rollback()
                    row["Result"] = f"Error: Unexpected"

                # Append row to output list
                output_rows.append(row)

        
        with open(output_path, "w", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
        
        object_name = f"output/{os.path.basename(output_path)}"  # S3 key (folder path + file name)
        s3_url = upload_to_s3(output_path, AWS_S3_BUCKET, object_name)
        print(f"Output file uploaded to S3: {s3_url}")

        return {"message": "CSV processed successfully!", "s3_url": s3_url}


    except FileNotFoundError as fnf_error:
        raise ValueError("The specified file could not be found.") from fnf_error
    except ValueError as val_error:
        raise ValueError(f"Invalid data: {val_error}") from val_error
    except Exception as e:
        print("from Exception in utils", str(e))
        raise RuntimeError("An unexpected error occurred while processing the CSV.") from e
    # finally:
    #     session.close()



def validate_csv_row(row, required_columns):
    missing_fields = [col for col in required_columns if not row.get(col)]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    
    if not row["Business ID"].isdigit():
        raise ValueError(f"Invalid 'Business ID': {row['Business ID']} (must be an integer)")

    
    if row["Symptom Diagnostic"].strip().lower() not in ["true", "false", "yes", "no"]:
        raise ValueError(
            f"Invalid 'Symptom Diagnostic': {row['Symptom Diagnostic']} (must be TRUE/FALSE or YES/NO)"
        )



def validate_required_columns(fieldnames, required_columns):
    missing_columns = required_columns - set(fieldnames)
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    

def upload_to_s3(file_path, bucket_name, object_name):
    """
    Uploads a file to an S3 bucket.

    :param file_path: Path to the file to upload
    :param bucket_name: Name of the S3 bucket
    :param object_name: S3 object name (key)
    :return: S3 URL of the uploaded file
    """
    s3_client = boto3.client(
        's3',
        region_name=AWS_S3_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    try:
        # Upload the file
        s3_client.upload_file(file_path, bucket_name, object_name)
        s3_url = f"https://{bucket_name}.s3.{AWS_S3_REGION}.amazonaws.com/{object_name}"
        print(s3_url)
        print(f"File uploaded to S3: {s3_url}")
        return s3_url
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        raise RuntimeError("Failed to upload the file to S3.")