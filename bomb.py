import json

import requests


class BombException(RuntimeError):
    pass


def decode_json(content):
    try:
        return json.loads(content)
    except Exception as e:
        print(f"Exception on encoding JSON: {e}")
        print(f"Raw content: {content}")


def get_error_message_or_none(response: requests.Response):
    try:
        error = decode_json(response.text)["message"]
        return f"({response.status_code}) {error}"
    except Exception as ex:  # catch JSON serialization caused exceptions
        print(f"({response.status_code}) {response.text}")  # print the raw response text
        raise ex  # throw the exception again


class BombApi:

    def __init__(self, api_url, username=None, password=None):
        self.api_url = api_url
        self.username = username
        self.password = password

    def setup_authentication(self, username, password):
        self.username = username
        self.password = password

    def get_content(self, url):
        response = requests.get(url, auth=(self.username, self.password))
        if response.status_code == 200:
            return response.text
        else:
            raise BombException(get_error_message_or_none(response))

    def post_content(self, url, data=None, json_data=None):
        response = requests.post(url, data=data, json=json_data, auth=(self.username, self.password))
        if response.ok:
            return response.text
        else:
            raise BombException(get_error_message_or_none(response))

    def ping(self):
        return decode_json(self.get_content(f"{self.api_url}"))

    def ping_auth(self):
        return decode_json(self.get_content(f"{self.api_url}/management"))

    def get_set(self, set_id):
        return decode_json(self.get_content(f"{self.api_url}/set/{set_id}"))["data"]

    def get_set_by_name(self, musicName):
        return decode_json(self.post_content(f"{self.api_url}/set/by-name", json_data=musicName))

    def get_set_by_chartId(self, chartId):
        return decode_json(self.post_content(f"{self.api_url}/set/by-chart", json_data=chartId))

    def get_chart(self, chartId):
        return decode_json(self.get_content(f"{self.api_url}/chart/{chartId}"))["data"]

    def get_user(self, user_id):
        return decode_json(self.get_content(f"{self.api_url}/user/{user_id}"))["data"]

    def get_user_by_name(self, username):
        return decode_json(self.post_content(f"{self.api_url}/user/by-name", json_data=username))

    def get_user_best_records_score(self, user_id):
        return decode_json(self.get_content(f"{self.api_url}/user/{user_id}/best20/s"))["data"]

    def get_user_best_records_r_value(self, user_id):
        return decode_json(self.get_content(f"{self.api_url}/user/{user_id}/best"))["data"]

    def get_user_recent_records(self, user_id):
        return decode_json(self.get_content(f"{self.api_url}/user/{user_id}/last20"))

    def register_user(self, username, password):
        return decode_json(self.post_content(f"{self.api_url}/management/user/register",
                                             json_data={"username": username, "password": password}))

    def get_user_details(self, user_id):
        return decode_json(self.get_content(f"{self.api_url}/management/user/{user_id}"))

    def get_set_details(self, set_id):
        return decode_json(self.get_content(f"{self.api_url}/management/set/{set_id}"))

    def get_chart_details(self, chartId):
        return decode_json(self.get_content(f"{self.api_url}/management/set/{chartId}"))

    def get_reviews(self):
        return decode_json(self.get_content(f"{self.api_url}/set/reviews"))

    def add_review(self, set_id, status: bool, evaluation=None):
        return decode_json(self.post_content(f"{self.api_url}/set/{set_id}/review",
                                             json_data={"status": status, "evaluation": evaluation}))

    def start_review(self, set_id, status):
        return decode_json(self.post_content(f"{self.api_url}/set/{set_id}/review/start", json_data={"status": status}))

    def end_review(self, set_id, status: bool):
        return decode_json(self.post_content(f"{self.api_url}/set/{set_id}/review/end", json_data={"status": status}))


bomb = BombApi("http://43.142.173.63:10483/bomb/v2")

if __name__ == "__main__":
    # print(bomb.get_content("http://43.142.173.63:10483/bomb/v2/set/5fb517cf2496ed90dd81a0f1"))
    # print(bomb.get_user("dbef7e85-0d5b-416a-82d0-fbffb420588e"))
    print(bomb.get_user_best_records_r_value("dbef7e85-0d5b-416a-82d0-fbffb420588e"))
    #test
    # print(api.get_set(example_set_id))
    # print(api.get_set_by_name("Intel Sound Logo"))
    # print(api.get_chart(example_chartId))
    # print(api.get_user(example_user_id))
    # print(api.get_user_by_name("Taskeren"))
    # print(api.get_user_best_records_score(example_user_id))
    # print(api.get_user_best_records_r_value(example_user_id))
    # print(api.get_set_by_chartId(example_chartId))
    # print(api.ping_auth())
    # print(api.register_user("Taskeren-Bot", "1024"))
    # print(api.get_user_details(example_user_id))
    # print(api.start_review("n07f8mbyk262p70x3xregl2b", "RANKED"))
    # print(api.get_reviews())
    # print(api.end_review("n07f8mbyk262p70x3xregl2b", True))
