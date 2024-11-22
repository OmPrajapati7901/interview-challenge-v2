from utils import import_csv  # Assuming `import_csv` is in a `utils.py` file

if __name__ == "__main__":
    # Path to your CSV file
    csv_path = "data/business_symptom_data.csv"
    
    try:
        # Call the function
        import_csv(csv_path)
        print("CSV data imported successfully!")
    except Exception as e:
        print(f"Error during import: {e}")
