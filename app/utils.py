import csv
from sqlalchemy.orm import Session
from app.models import Business, Symptom, BusinessSymptom
from app.database import engine  # Assuming you have a configured SQLAlchemy engine
from sqlalchemy.exc import SQLAlchemyError



def import_csv(file_path: str):
    session = Session(bind=engine)

    try:
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Validate required fields
                if not row.get("Business ID") or not row.get("Symptom Code"):
                    raise ValueError("Missing required fields: 'Business ID' or 'Symptom Code'")

                # Add or get Business
                business = session.query(Business).filter_by(business_id=row["Business ID"]).first()
                if not business:
                    business = Business(
                        business_id=row["Business ID"],
                        business_name=row["Business Name"]
                    )
                    session.add(business)
                    session.flush()

                # Add or get Symptom
                symptom = session.query(Symptom).filter_by(symptom_code=row["Symptom Code"]).first()
                if not symptom:
                    symptom = Symptom(
                        symptom_code=row["Symptom Code"],
                        symptom_name=row["Symptom Name"]
                    )
                    session.add(symptom)
                    session.flush()

                # Add Relationship
                business_symptom = BusinessSymptom(
                    business_id=business.business_id,
                    symptom_code=symptom.symptom_code,
                    symptom_diagnostic=row["Symptom Diagnostic"].strip().lower() in ["true", "yes"]
                )
                session.add(business_symptom)

            # Commit the transaction
            session.commit()
        print("CSV data imported successfully!")

    except FileNotFoundError as fnf_error:
        print(f"File not found: {fnf_error}")
        raise ValueError("The specified file could not be found.") from fnf_error
    except ValueError as val_error:
        print(f"Value error: {val_error}")
        session.rollback()
        raise ValueError(f"Invalid data: {val_error}") from val_error
    except SQLAlchemyError as db_error:
        print(f"Database error: {db_error}")
        session.rollback()
        raise RuntimeError("An error occurred while interacting with the database.") from db_error
    except Exception as e:
        print(f"Unexpected error: {e}")
        session.rollback()
        raise RuntimeError("An unexpected error occurred while importing the CSV.") from e
    finally:
        # Ensure the session is closed
        session.close()


# def import_csv(file_path: str):
#     print("Saving CSV data")
#     session = Session(bind=engine)
#     with open(file_path, "r") as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             # Check if the business exists
#             business = session.query(Business).filter_by(name=row["Business Name"]).first()
#             if not business:
#                 business = Business(name=row["Business Name"])
#                 session.add(business)
#                 session.flush()  # Ensure `business.id` is available

#             # Check if the symptom exists
#             symptom = session.query(Symptom).filter_by(code=row["Symptom Code"]).first()
#             if not symptom:
#                 symptom = Symptom(
#                     code=row["Symptom Code"],
#                     name=row["Symptom Name"],
#                     diagnostic=row["Symptom Diagnostic"].strip().lower() == "true"
#                 )
#                 session.add(symptom)
#                 session.flush()  # Ensure `symptom.id` is available

#             # Create relationship
#             relationship = BusinessSymptom(business_id=business.id, symptom_id=symptom.id)
#             session.add(relationship)

#         session.commit()
#     print("CSV data imported successfully!")
