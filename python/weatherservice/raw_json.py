try:
    import urllib2
    PYTHON_3 = False
except:
    import urllib.request as request
    PYTHON_3 = True
import json
import threading
from weatherservice._cache import _recursively_convert_unicode_to_str, lookup
from weatherservice.report import Report
import weatherservice._cache as cache
_using_cache = False

def get(url):
    if PYTHON_3:
        response = request.urlopen(url)
        return response.read()
    else:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()

def connect():
    """
    Connect to the online data source in order to get up-to-date information.
    
    :returns: void
    """
    global _using_cache
    cache.load()
    _using_cache = True

def disconnect():
    """
    Connect to the local cache, so no internet connection is required.
    
    :returns: void
    """
    global _using_cache
    cache.unload()
    _using_cache = False

def get_report(latitude, longitude):
    """
    Gets a report on the current weather, forecast, and more detailed information about the location.
    
    :param latitude: The latitude (up-down) of the location to get information about.
    :type latitude: float
    :param longitude: The longitude (left-right) of the location to get information about.
    :type longitude: float
    :returns: string
    """
    if _using_cache:
        result = cache.lookup(("http://forecast.weather.gov/MapClick.php") + "%{lat=" + str(latitude)+ "}""%{lon=" + str(longitude)+ "}")
        return result
    else:
        result = get("http://forecast.weather.gov/MapClick.php?FcstType=json&lat={}&lon={}".format(str(latitude),str(longitude)))
        return result

def get_report_async(callback, error_callback, latitude, longitude):
    """
    Asynchronous version of get_report
    
    :param callback: Function that consumes the data (string) returned on success.
    :type callback: function
    :param error_callback: Function that consumes the exception returned on failure.
    :type error_callback: function
    :param latitude: The latitude (up-down) of the location to get information about.
    :type latitude: float
    :param longitude: The longitude (left-right) of the location to get information about.
    :type longitude: float
    :returns: void
    """
    def server_call(callback, error_callback, latitude, longitude):
        """
        Internal closure to thread this call.
        
        :param callback: Function that consumes the data (string) returned on success.
        :type callback: function
        :param error_callback: Function that consumes the exception returned on failure.
        :type error_callback: function
        :param latitude: The latitude (up-down) of the location to get information about.
        :type latitude: float
        :param longitude: The longitude (left-right) of the location to get information about.
        :type longitude: float
        :returns: void
        """
        try:
            callback(get_report(latitude, longitude))
        except Exception as e:
            error_callback(e)
    threading.Thread(target=server_call, args = (latitude, longitude)).start()
