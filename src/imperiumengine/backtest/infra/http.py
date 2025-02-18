from traceback import format_exc
import requests

class HttpHelper:

    def __init__(self, user=None, password=None):
        self.user = user
        self.password = password


    def get(self, url):
        try:
            response = requests.get(url)
            status_code = response.status_code
            body = response.json()
            if(status_code != 200 and status_code != 201):
                raise Exception(f"Problem with request - statusCode: {status_code}")
            return {"success":True, "data": body}

        except Exception as e:
            print(format_exc())
            return {"success":False, "data": f'{e}'}

    def post(self, url, body, headers={}):
        try:
            response = requests.post(url,json=body,headers=headers)
            status_code = response.status_code
            response = response.json()
            if(status_code != 200 and status_code != 201):
                print(response)
                raise Exception(f"Problem with request - statusCode: {status_code}")
            return {"success":True, "data": response}

        except Exception as e:
            print(format_exc())
            return {"success":False, "data": f'{e}'}
