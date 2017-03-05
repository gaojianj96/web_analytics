import requests
import json

from  Chatbot_Keys import google_key as  google_API_key

def get_coord(str_location):
    baseurl="https://maps.googleapis.com/maps/api/geocode/json?address={}&region=us&key="+google_API_key

    loc=json.loads(requests.get(baseurl.format(str_location)).text)["results"][0]["geometry"]["location"]

    return loc["lng"],loc["lat"]
