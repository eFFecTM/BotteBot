import pyowm

from constants import open_weather_key


def get_weather_message():
    """Get the current weather at a given location. Default location is Antwerp."""
    owm = pyowm.OWM(open_weather_key)
    location = None
    if location is None:
        location = 'Antwerp'  # Default location
    observation = owm.weather_at_place(location)
    w = observation.get_weather()
    status = w.get_detailed_status()
    temperature = w.get_temperature('celsius')
    wind = w.get_wind()
    sunrise = w.get_sunrise_time('iso')
    sunset = w.get_sunset_time('iso')

    msg = "Current status in {}: {} :thermometer: {}°C (min = {}°C, max = {}°C) :tornado_cloud: {} km/h\n" \
          "Sunrise :sunrise: is at {}, sunset :city_sunset: is at {}. ".format(location, status, temperature['temp'],
                                                                               temperature['temp_min'],
                                                                               temperature['temp_max'], wind['speed'],
                                                                               sunrise, sunset)
    return msg
