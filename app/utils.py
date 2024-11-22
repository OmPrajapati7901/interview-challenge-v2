import csv
import os
from sqlalchemy.orm import Session
from app.models import Business, Symptom, BusinessSymptom
from app.database import engine  # Assuming you have a configured SQLAlchemy engine
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


#as requeted in challenge
def import_csv(file_path: str):
    session = Session(bind=engine)

    try:

        
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            required_columns = {"Business ID", "Business Name", "Symptom Code", "Symptom Name", "Symptom Diagnostic"}
            missing_columns = required_columns - set(reader.fieldnames)

            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            for row in reader:

                #To Validate required fields
                if not row.get("Business ID") or not row.get("Symptom Code"):
                    raise ValueError("Missing required fields: 'Business ID' or 'Symptom Code'")
                
                # Validate field types
                if not row["Business ID"].isdigit():
                    raise ValueError(f"Invalid 'Business ID': {row['Business ID']} (must be an integer) in row: {row}")

                if row["Symptom Diagnostic"].strip().lower() not in ["true", "false", "yes", "no"]:
                    raise ValueError(
                        f"Invalid 'Symptom Diagnostic': {row['Symptom Diagnostic']} (must be TRUE/FALSE or YES/NO) in row: {row}"
                    )    

                # Add Business
                business = session.query(Business).filter_by(business_id=row["Business ID"]).first()
                if not business:
                    business = Business(
                        business_id=row["Business ID"],
                        business_name=row["Business Name"]
                    )
                    session.add(business)
                    session.flush()

                # Add Symptom
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

    except IntegrityError as e:
        print(f"Duplicate entry detected: {e}")
        session.rollback()
        raise ValueError(f"Invalid data: {e}") from e
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


#if you want rejection specific to record
# def import_csv(file_path: str):
#     session = Session(bind=engine)

#     # Prepare output file path
#     output_dir = os.path.join(os.path.dirname(file_path), "output")
#     os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it doesn't exist
#     output_path = os.path.join(output_dir, os.path.basename(file_path))

#     # To store rows with their results
#     output_rows = []

#     try:
#         with open(file_path, "r") as file:
#             reader = csv.DictReader(file)

#             # Validate columns
#             required_columns = {"Business ID", "Business Name", "Symptom Code", "Symptom Name", "Symptom Diagnostic"}
#             missing_columns = required_columns - set(reader.fieldnames)
#             if missing_columns:
#                 raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

#             # Prepare output CSV
#             fieldnames = reader.fieldnames + ["Result"]
            
#             for row in reader:
#                 try:
#                     # Validate required fields
#                     if not row.get("Business ID") or not row.get("Symptom Code"):
#                         raise ValueError("Missing required fields: 'Business ID' or 'Symptom Code'")
                    
#                     # Validate field types
#                     if not row["Business ID"].isdigit():
#                         raise ValueError(f"Invalid 'Business ID': {row['Business ID']} (must be an integer)")

#                     if row["Symptom Diagnostic"].strip().lower() not in ["true", "false", "yes", "no"]:
#                         raise ValueError(
#                             f"Invalid 'Symptom Diagnostic': {row['Symptom Diagnostic']} (must be TRUE/FALSE or YES/NO)"
#                         )

#                     # Add or get Business
#                     business = session.query(Business).filter_by(business_id=row["Business ID"]).first()
#                     if not business:
#                         business = Business(
#                             business_id=row["Business ID"],
#                             business_name=row["Business Name"]
#                         )
#                         session.add(business)
#                         session.flush()

#                     # Add or get Symptom
#                     symptom = session.query(Symptom).filter_by(symptom_code=row["Symptom Code"]).first()
#                     if not symptom:
#                         symptom = Symptom(
#                             symptom_code=row["Symptom Code"],
#                             symptom_name=row["Symptom Name"]
#                         )
#                         session.add(symptom)
#                         session.flush()

#                     # Add Relationship
#                     business_symptom = BusinessSymptom(
#                         business_id=business.business_id,
#                         symptom_code=symptom.symptom_code,
#                         symptom_diagnostic=row["Symptom Diagnostic"].strip().lower() in ["true", "yes"]
#                     )
#                     session.add(business_symptom)

#                     # Commit after each row for partial updates
#                     session.commit()

#                     # Append success result
#                     row["Result"] = "Success"
#                 except IntegrityError as e:
#                     session.rollback()
#                     row["Result"] = f"Error: Duplicate entry - {str(e)}"
#                 except ValueError as val_err:
#                     row["Result"] = f"Error: Validation - {str(val_err)}"
#                 except SQLAlchemyError as db_err:
#                     session.rollback()
#                     row["Result"] = f"Error: Database - {str(db_err)}"
#                 except Exception as ex:
#                     session.rollback()
#                     row["Result"] = f"Error: Unexpected - {str(ex)}"

#                 # Append row to output list
#                 output_rows.append(row)

#         # Write output CSV with results
#         with open(output_path, "w", newline="") as output_file:
#             writer = csv.DictWriter(output_file, fieldnames=fieldnames)
#             writer.writeheader()
#             writer.writerows(output_rows)

#         print(f"CSV data processed. Results written to: {output_path}")

#     except FileNotFoundError as fnf_error:
#         print(f"File not found: {fnf_error}")
#         raise ValueError("The specified file could not be found.") from fnf_error
#     except ValueError as val_error:
#         print(f"Value error: {val_error}")
#         raise ValueError(f"Invalid data: {val_error}") from val_error
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         raise RuntimeError("An unexpected error occurred while processing the CSV.") from e
#     finally:
#         session.close()