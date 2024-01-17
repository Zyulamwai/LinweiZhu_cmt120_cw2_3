import requests
from datetime import datetime

def get_cardiff_weather(api_key):
    # The latitude and longitude of Cardiff
    lat = 51.481583
    lon = -3.179090

    # Build request URL
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=hourly,minutely,alerts,daily&units=metric&appid={api_key}"

    # request
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        day_data = data["current"]
        # Used to store simplified weather data.
        simple_weather_data = {}
        # Convert Unix timestamp to date.
        date = datetime.utcfromtimestamp(day_data["dt"]).strftime('%Y-%m-%d')
        temp = day_data["temp"]

        # weather_description = day_data["weather"][0]["description"]
        icon = f"https://openweathermap.org/img/wn/{day_data['weather'][0]['icon']}.png"
        weather_main = day_data["weather"][0]["main"]

        simple_weather_data = {
            "date": date,
            "temp": temp,
            "icon": icon,
            "weather_main": weather_main
        }
        return simple_weather_data
    else:
        print("Error: Unable to fetch weather data")
        return False

if __name__ == "__main__":
    # API key
    api_key = "2e08607733b93dc21cb624c61b75aad8"
    weather_data = get_cardiff_weather(api_key)

    print(weather_data)