import requests

def fetch_air_quality(api_key, location, target_date):
    """
    Fetch historical air quality data for a given location and date from WeatherAPI.
    
    Parameters:
        api_key (str): Your WeatherAPI key.
        location (str): Location query (city name, postal code, latitude/longitude, etc.).
        target_date (str): The target date in the format 'yyyy-MM-dd'.
    
    Returns:
        dict: A dictionary with air quality data (PM10, NO2, SO2) or an error message.
    """
    # Define the API endpoint and query parameters
    url = f"http://api.weatherapi.com/v1/history.json"
    querystring = {
        "key": api_key,
        "q": location,
        "dt": target_date,
        "aqi": "yes"  # Include air quality data in the response
    }

    try:
        # Send the GET request to the API
        response = requests.get(url, params=querystring)

        # Check for HTTP errors
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Extract air quality information
        if "forecast" in data and "forecastday" in data["forecast"]:
            air_quality = data["forecast"]["forecastday"][0]["day"]["air_quality"]

            # Extract PM10, NO2, SO2
            pm10 = air_quality.get("pm10", "N/A")
            no2 = air_quality.get("no2", "N/A")
            so2 = air_quality.get("so2", "N/A")

            return {
                "PM10": pm10,
                "NO2": no2,
                "SO2": so2
            }
        else:
            return {"error": "Air quality data not available for the specified date and location."}

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}


# Example usage
if __name__ == "__main__":
    # Replace with your WeatherAPI key
    api_key = "your_weatherapi_key_here"
    location = "New Delhi"
    target_date = "2023-11-01"

    result = fetch_air_quality(api_key, location, target_date)
    print(result)
