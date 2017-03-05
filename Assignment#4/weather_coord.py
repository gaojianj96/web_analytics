import json,urllib2,urllib
import copy
import dateutil.parser as dateparser
import Locate_google as Locate
from Chatbot_Keys import google_key as  google_API_key
from Chatbot_Keys import openweathermap_key as whether_app_key

def get_wether(location):
    print "GET Weather AT "+location
    #units=imperial refers to F,units=metric refers to C
    lng, lat = Locate.get_coord(location)
    query_url="http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&units=imperial&appid={}".format(lat,lng,whether_app_key)
    forecast_url="http://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&cnt=1&units=imperial&cnt=7&appid={}".format(lat,lng,whether_app_key)
    baseurl_weather_icon="http://openweathermap.org/img/w/{}.png"
    # baseurl_location_street_view="https://maps.googleapis.com/maps/api/streetview?size=400x400&location={},{}&fov=90&heading=235&pitch=10&key={}".format(google_API_key)
    base_url_staticmap="https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom=15&size=640x400&key={}"
    response_text=""

    print  query_url
    print forecast_url
    print base_url_staticmap
    result = urllib2.urlopen(query_url).read()
    result_forecast=urllib2.urlopen(forecast_url).read()
    data = json.loads(result)
    data_forecast=json.loads(result_forecast)
    response_field = [{"pretext": "Current Weather","fields": []},{"pretext": "Weather Forecast","fields": []},
                      {"pretext": "Location map view", "image_url": ""}]
    template_field = {"title": "", "value": "", "short": True}

    city_name=["City",data["name"],True]
    city_country=["Country",data["sys"]["country"],True]
    temprature = ["Temperature", str(data["main"]["temp"])+u"\u00b0F", True]
    wind_speed = ["Wind Speed", str(data["wind"]["speed"]) + " m/s", True]
    response_field[0].update({"thumb_url": baseurl_weather_icon.format(data["weather"][0]["icon"])})

    #forecast
    weather_forecast_json=data_forecast["list"][0]
    print weather_forecast_json
    forecast_date=["Forecast Date",dateparser.parse(weather_forecast_json["dt_txt"]).strftime('%b %d, %Y'),True]
    forecast_temp=["Forecast Temperature",str(weather_forecast_json["main"]["temp_min"])+u'\u00b0'+"F/"+str(weather_forecast_json["main"]["temp_max"])+u"\u00b0F",True]
    # forecast_temp_max = ["Max Temperature", weather_forecast_json["main"]["temp_max"], True]
    forecast_weather=["Forecast Weather","",True]
    response_field[1].update({ "thumb_url":baseurl_weather_icon.format(weather_forecast_json["weather"][0]["icon"])})
    print "Forecast Date:"+weather_forecast_json["dt_txt"]


    weathers_json = data["weather"]
    weathers_conds=""
    for weather_tmp in weathers_json:
        weathers_conds+=weather_tmp["description"]+"\n"
    weather=["Weather", weathers_conds, True]

    weather_json_forecast = weather_forecast_json["weather"]
    weathers_conds = ""
    for weather_tmp in weather_json_forecast:
        weathers_conds += weather_tmp["description"] + "\n"
    forecast_weather = ["Forecast Weather", weathers_conds, True]

    response_field[2]["image_url"]=base_url_staticmap.format(lat,lng,google_API_key)

    list_weather_current = [city_name,city_country,temprature, wind_speed,weather]
    list_weather_forecast=[forecast_date,forecast_weather,forecast_temp]


    for item in list_weather_current:
        ret_field = copy.copy(template_field)
        ret_field["title"] = item[0]
        ret_field["value"] = item[1]
        ret_field["short"] = item[2]
        response_field[0]["fields"].append(ret_field)
    for item in list_weather_forecast:
        ret_field = copy.copy(template_field)
        ret_field["title"] = item[0]
        ret_field["value"] = item[1]
        ret_field["short"] = item[2]
        response_field[1]["fields"].append(ret_field)

    return response_text,response_field