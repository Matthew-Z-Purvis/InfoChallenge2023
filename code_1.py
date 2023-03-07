import pandas as pd
from arcgis.geocoding import reverse_geocode
from arcgis.geometry import Geometry
from arcgis.geocoding import geocode
from arcgis.gis import GIS
import pandas as pd
import pgeocode

#gis = GIS("http://www.arcgis.com", "Matthew_Purvis_LearnArcGIS", "InfoChallenge2023",verify_cert = False)
nomi = pgeocode.Nominatim('us')


def get_zip(df, lon_field, lat_field):
    location = reverse_geocode((Geometry({"x":float(df[lon_field]), "y":float(df[lat_field]), "spatialReference":{"wkid": 4326}})))
    print(location['address']['Postal'])
    return location['address']['Postal']

def getGeolocationFromZip(df):
    # use pgeocode to get the location
    location = nomi.query_postal_code(df["dzip"])
    # get the latitude and longitude from the location
    lat, lon = location['latitude'], location['longitude']
    print(df["par"],df["dzip"],lat,lon)
    return lat,lon

from math import radians, cos, sin, asin, sqrt
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r
   

def getCrashDistance(df):
    distance = haversine(df["driverAddressLon"],df["driverAddressLat"],df["x"],df["y"])
    return distance

#crashdf = pd.read_csv("fulldata.csv")
crashdf = pd.read_csv("fulldata.csv", sep=',', error_bad_lines=False, index_col=False, dtype='unicode')

print("Finding geolcoations...")
crashdf["driverAddressLat"], crashdf["driverAddressLon"] = zip(*crashdf.apply(getGeolocationFromZip,axis=1))
print("Finding Distances...")
crashdf["distance"] = crashdf.apply(getCrashDistance,axis=1)

print("Finding who gets into accidents locally to where they live...")
#Local: distace<=45km
localdf = crashdf[crashdf["distance"]<=45]
#Far: 45km < distance 
fardf = crashdf[(crashdf["distance"]>45)]

print((localdf.shape[0])/(crashdf.shape[0]))

#Export
localdf.to_csv('localCrashes.csv')
fardf.to_csv('nonLocalCrashes.csv')
crashdf.to_csv('crashesWithDriverGeolocation.csv')



