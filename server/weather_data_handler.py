import os.path
import json
from datetime import date
from datetime import datetime
from datetime import timedelta
import copy

class Forecast:
    '''
    Class for arbitrary weather
    '''
    def __init__(self, weatherInfo):
        '''
        Construct a Forecast object
        Parameters:
            weatherInfo (tuple):
                a tuple of 4 values: <weather:str> <temperatur:float> <humidity:float> <wind_speed:float>
                humidity must be between 0 and 1, if fails, raises an ValueError
                wind_speed must be positive
        Raises:
            ValueError: when a weatherInfo value is not in appropriate range
        '''
        try:
            assert weatherInfo[0] in ["Sunny", "Cloudy", "Sunny + Cloudy", "Rainy", "Stormy", "Lightning"], "Invalid weather type"
            self.weather = weatherInfo[0]
            self.temperature = weatherInfo[1]
            assert weatherInfo[2] >= 0 and weatherInfo[2] <= 1, "Invalid humidity value"
            self.humidity = weatherInfo[2]
            assert weatherInfo[3] >= 0, "Invalid wind speed value"
            self.wind_speed = weatherInfo[3]
        except AssertionError as e:
            raise ValueError(e)

    @staticmethod
    def FromDict(adict):
        '''
        Converts a dictionary with appropriate keys into a Forecast object
        
        Parameters:
            adict (dict):
                A Dictionary with at least these 4 keys: 'weather', 'temperature', 'humidity', 'wind_speed'
        Returns:
            a Forecast object
        Raises:
            ValueError if a weatherInfo value is not in appropriate range
            Any errors an errorneous action on a dictionary may invoke
        '''
        return Forecast((adict['weather'], adict['temperature'],adict['humidity'], adict['wind_speed']))

    def ToDict(self):
        '''
        Retrieves a dictionary with 4 keys corresponding to each object member
        Returns:
            dict (dict):
                A dictionary
        '''
        return { 'weather': self.weather, 'temperature': self.temperature, 'humidity': self.humidity, 'wind_speed': self.wind_speed}

    def Info(self):
        return (self.weather, self.temperature, self.humidity, self.wind_speed)

class City:
    '''
    Class for city
    '''
    def __init__(self, name, id:int):
        '''
        Construct a city object
        The constructor needs a manual id
        Parameters:
            name (str):
                The name of the city
            id (int):
                City's id
        '''
        self.id = id
        self.name = name
        self.date_weather = dict()
        pass

    @staticmethod
    def FromDict(adict):
        '''
        '''
        temp = City(adict['city_name'], adict['city_id'])
        for item in adict['date_weather']:
            temp.AddForecast(datetime.strptime(item['date'], '%Y/%m/%d').date(), Forecast.FromDict(item['info']), errorOnDuplicate=False, override=False)
        return temp

    def ToDict(self):
        '''
        '''
        adict = dict()
        adict['city_id'] = self.id
        adict['city_name'] = self.name
        adict['date_weather'] = [{'date': x.strftime('%Y/%m/%d'), 'info': self.date_weather[x].ToDict()} for x in self.date_weather]
        return adict

    def AddForecast(self, date:date, dateWeatherForecast:Forecast, errorOnDuplicate=False, override=True):
        '''
        Add a forecast of weather for a date
        Parameters:
            date: (datetime.date):
                a date object
            dateWeatherForecast (DateWeatherForecast):
                a DateWeatherForecast object
            errorOnDuplicate (bool): default is False
                if True, the method raises a AssertionException if an old forecast exists for the date.
            override (bool): default is True
                if True: override if an old forecast for the same date exists.
                Otherwise, keep the old forecast.
                Only in effect if errorOnDuplicate is set to False
        Returns:
            state (bool):
                True if successfully, else false
        '''
        try:
            if date in self.date_weather:
                if errorOnDuplicate:
                    raise AssertionError('Duplicate exists for parameter date')
                if not override:
                    return False
                    
            self.date_weather[date] = dateWeatherForecast
            return True
        except Exception as e:
            print(e)
            return False

    def RemoveForecast(self, date:date):
        '''
        Remove the forecast of weather for a date
        Parameters:
            date: (datetime.date):
                a date object
        '''
        self.date_weather.pop(date)

    def FetchForecast(self, date:date):
        '''
        Retrieve the forecast of weather for a date
        Parameters:
            date: (datetime.date):
                a date object
        Returns:
            forecast (Forecast | None):
                The corresponding Forecast object or None if there is not one
        '''
        return self.date_weather[date] if date in self.date_weather else None

class WeatherDataHandler:
    MAXCITY = 65536
    def __init__(self, jsonPath:str):
        '''
        Create a weather data handler for the weather database
        Parameters:
            jsonPath (str):
                file path to the database, in json format
        '''
        self.datafilepath = jsonPath
        self.id_lookup = dict()
        self.city_list = []

    def LoadDatabase(self):
        '''
        Load the database into memory, saves it as an object's member
        Returns:
            status (bool):
                True if database is loaded and ready to use
                False otherwise
        '''
        loaded = False
        try:
            self.city_list = []
            self.id_lookup = dict()
            fromjson = None
            i = 0
            if not os.path.isfile(self.datafilepath):
                return True
            with open(self.datafilepath, 'r') as fp:
                fromjson = json.load(fp)
            for citydict in fromjson:
                new_city = City.FromDict(citydict)
                self.city_list.append(new_city)
                self.id_lookup[new_city.id] = i
                i += 1
                loaded = True
        except Exception as e:
            print(e)
            
        return loaded

    def FetchAllCitiesByDate(self, adate:date=None):
        '''
        Retrive a list of essential weather data of every city in the database in primitives, if any is found
        Parameters:
            adate (datetime.date | None): default is None:
                A date object to fetch forecasts of. If None, fetch today's forecasts (of the client's system time)
        Returns:
            weatherdata (list):
                A list of tuples in form of (city_id, city_name, weather, temperature, humidity, wind_speed)
                If a forecast does not exists, relevant infos are replaced by None
        '''
        try:
            if not adate:
                adate = date.today()
            weatherList = []
            for city in self.city_list:
                forecast = city.FetchForecast(adate)
                if not forecast:
                    weatherList.append((city.id, city.name, None, None, None, None))
                else:
                    t1, t2, t3, t4 = forecast.Info()
                    weatherList.append((city.id, city.name, t1, t2, t3, t4))
            return weatherList
        except Exception as e:
            print(e)
            return []

    def FetchForcastsByCity(self, city_id:int, fromDate:date=None, count=7):
        '''
        Retrive a dictionary of weather forecasts of a city in the database in primitives, if any is found
        Parameters:
            city_id (int):
                The city_id of the city to fetch forecasts
            fromDate (datetime.date | None): Default is None
                The date from which forecasts are retrieved (not including itself).
                If None is passed, fetch from tomorrow (of client's system time)
            count (int): Default is 7
                How many dates prior to mostRecentDates to fetch forecasts of
        Returns:
            status (bool):
                True: a city is found
                False: no cities are found, the other return is None
            info: tuple of (name, weatherdata (dictionary)) or None:
                A dictionary (date (str) : forecast) with forecast is a tuple of (weather, temperature, humidity, wind_speed) for count date up to mostRecentDate
                If a forecast does not exists, relevant infos are replaced by None
        '''
        city = None
        try:
            city = self.city_list[self.id_lookup[city_id]]
        except:
            city = None
            pass

        if city:
            if not fromDate:
                fromDate = date.today()

            weatherinfo = dict()
            for dateDelta in range(1, count+1):
                day = fromDate + timedelta(days=dateDelta)
                info = city.FetchForecast(day)
                if not info:
                    info = (None, None, None, None)
                else:
                    info = info.Info()
                weatherinfo[day.strftime('%Y/%m/%d')] = info

            return True, (city.name, weatherinfo)
        return False, None

class WeatherDataModifier(WeatherDataHandler):
    class JSONEncoder(json.JSONEncoder):
        def default(self, o):
            if type(o) == Forecast:
                return o.ToDict()
            elif type(o) == City:
                return o.ToDict()
            else:
                return super().default(o)

    def __init__(self, jsonPath):
        super().__init__(jsonPath)
        self.changed = False

    def __del__(self):
        pass

    def LoadDatabase(self):
        '''
        Load the database into memory and create a backup copy
        If no database exists, creates an empty one
        Returns:
            status (bool):
                True if database is loaded and ready to use
                False if a new database is created and not yet saved to disk
        '''
        self.backup_dict = None
        if super().LoadDatabase():
            self.backup_dict = copy.deepcopy(self.city_list)
            self.changed = False
            return True
        else:
            self.city_list = []
            self.id_lookup = dict()
            return False
    
    def SaveDatabase(self):
        '''
        Save the database from memory, and make a backup of the old
        Returns:
            status (bool):
                True if database is loaded and ready to use
                False otherwise
        '''
        try:
            #backupPath = self.datafilepath + datetime.today().strftime('%Y%m%d_%H%M%S') + '.BAK'
            backupPath = self.datafilepath + '.BAK'
            if self.backup_dict:
                with open(backupPath, "w") as bfp:
                    json.dump(self.backup_dict, bfp, indent='\t', cls=WeatherDataModifier.JSONEncoder)
            with open(self.datafilepath, "w") as fp:
                json.dump(self.city_list, fp, indent='\t', cls=WeatherDataModifier.JSONEncoder)
            self.changed = False
            return True
        except Exception as e:
            print(e)
            return False

    def AddCity(self, city_name:str):
        '''
        Add a city to the database
        Parameters:
            city_name (str)
        Returns:
            status (bool): 
                whether the city is added
            id (int | None):
                id assigned to the city
        '''
        try:
            new_city = City(city_name,self.IdGetter(city_name))
            self.city_list.append(new_city)
            self.id_lookup[new_city.id] = len(self.city_list) - 1
            self.changed = True
            return True, new_city.id
        except:
            return False, None

    def AddForecastForCity(self, cityid, date:date, forecast:Forecast): 
        '''
        Add a forecast for a certain date to a city having cityid
        Parameters:
            cityid (int)
            date (datetime.date)
            forecast (Forecast)
        Returns:
            status (bool):
                True if successfully added
                False if the city does not exists or a weather already exists
        '''
        try:
            city = self.city_list[self.id_lookup[cityid]]
            city.AddForecast(date, forecast, errorOnDuplicate=False, override=True)
            self.changed = True
            return True
        except KeyError as e:
            print('City does not exists')
            return False
        except AssertionError as e:
            print(e)
            return False
        except Exception as e:
            print(e)
            return False

    def AddForecastByValues(self, cityid, date:date, weatherInfoTuple):
        '''
        Add a forecast in form of a 4-tuple for a certain date to a city having cityid
        Parameters:
            cityid (int)
            date (datetime.date)
            weatherInfoTuple (tuple)
        Returns:
            status (bool):
                True if successfully added
                False if the city does not exists or a weather already exists
        '''
        try:
            forecast = Forecast(weatherInfoTuple)
            self.changed = True
            return self.AddForecastForCity(cityid, date, forecast)
        except Exception as e:
            print(e)
            return False

    def RemoveForecast(self, cityid, date:date):
        '''
        Removes existing forecast (if any) from a city with cityid
        Parameters:
            cityid (int)
            date (datetime.date)
        '''
        try:
            city = self.city_list[self.id_lookup[cityid]]
            city.RemoveForecast(date)
            self.changed = True
            return True
        except:
            return False

    def RemoveCity(self, cityid):
        '''
        Removes a city from the database
        Parameters:
            cityid (int)
        Returns:
            status (bool):
                True if city is removed
                False if any complications arised or the city does not exists
        '''
        try:
            cityindex = self.id_lookup[cityid]
            self.city_list.pop(cityindex)
            
            # Fix id_lookup
            for i in range(cityindex, len(self.city_list)):
                self.id_lookup[self.city_list[i].id] = i

            self.changed = True
            return True
        except KeyError as e:
            print("The city does not exists")
            return False
        except Exception as e:
            print(e)
            return False
        pass

    def IdGetter(self, name):
        '''
        '''
        seed = sum([ord(x) for x in name])
        t = 0
        for l in name:
            t += t * seed + ord(l)
        t = t % WeatherDataHandler.MAXCITY

        for i in range(WeatherDataHandler.MAXCITY):
            res = (t + i) % WeatherDataHandler.MAXCITY
            try:
                self.id_lookup[res]
            except:
                return res

        raise RuntimeError('Cannot assign an id. The number of city reached maximal.')


if __name__ == '__main__':
    from pathlib import Path
    JSON_PATH = os.path.join(Path(__file__).parent.absolute(),"data\\weather_data.json")

    a = WeatherDataModifier(JSON_PATH)
    a.LoadDatabase()
    a.AddForecastByValues(8548, date(2021,5,30), ("Sunny", 99,0.99,99))
    a.SaveDatabase()
