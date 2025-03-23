import requests, json, datetime
import glob


class Prometheus:

    ################################################
    def __init__(self):

        import secrets_ak

        self.prom_url = secrets_ak.PROM_URL
        self.influx_url = secrets_ak.INFLUX_URL
        self.user = secrets_ak.PROM_USER_ID
        self.read_key = secrets_ak.READ_KEY
        self.write_key = secrets_ak.WRITE_KEY
    ################################################
    def get(self, query):

        query = self.prom_url + '?query=' + query

        try: 
            response = requests.get(url=query,
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                    auth = (self.user, self.read_key)
            )
        except OSError as e:
            print(e)
            return None
                
        status_code = response.status_code
        if status_code != 200:
            print('Error:', status_code)
            return {}

        return response.text
    ################################################
    def put(self, values):

        body = 'RPi,bar_label=RPi,source=RPi '+values
        print(body)

        try: 
            response = requests.post(self.influx_url,
                                headers = {'Content-Type': 'text/plain'},
                                data = str(body),
                                auth = (self.user, self.write_key))
        except OSError as e:
            print(e)
            return None
        
        if response.status_code != 204:
            print('Error:', response.status_code)

        return response.status_code
    ################################################