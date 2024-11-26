from datetime import datetime
from data_fetcher import fetcher

def main():
    try:
        # Initialize the fetcher instance
        print("Initializing fetcher...")
        fetcher_instance = fetcher()
        print("Fetcher initialized successfully!")
        
        # Define the target date for fetching data
        target_date = "20.11.2024"
        print(f"Fetching data for {target_date}...")
        
        # Fetch the data
        data = fetcher_instance.get(target_date)
        print("Data fetched successfully!")
        
        # Print the data
        print("Fetched Data:")
        for key, value in data.items():
            print(f"{key}: {value}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Ensure the driver is closed properly
        if 'fetcher_instance' in locals() and hasattr(fetcher_instance, 'close'):
            print("Closing the driver...")
            fetcher_instance.close()
            print("Driver closed.")

if __name__ == "__main__":
    main()
