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
        error = decode_json(response.text)["error"]
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
        return decode_json(self.get_content(f"{self.api_url}/set/{set_id}"))

    def get_set_by_name(self, music_name):
        return decode_json(self.post_content(f"{self.api_url}/set/by-name", json_data=music_name))

    def get_set_by_chart_id(self, chart_id):
        return decode_json(self.post_content(f"{self.api_url}/set/by-chart", json_data=chart_id))

    def get_chart(self, chart_id):
        return decode_json(self.get_content(f"{self.api_url}/chart/{chart_id}"))

    def get_user(self, user_id):
        return decode_json(self.get_content(f"{self.api_url}/user/{user_id}"))

    def get_user_by_name(self, username):
        return decode_json(self.post_content(f"{self.api_url}/user/by-name", json_data=username))

    def get_user_best_records_score(self, user_id):
        return decode_json(self.get_content(f"{self.api_url}/user/{user_id}/best20/s"))

    def get_user_best_records_r_value(self, user_id):
        return decode_json(self.get_content(f"{self.api_url}/user/{user_id}/best20/r"))

    def register_user(self, username, password):
        return decode_json(self.post_content(f"{self.api_url}/management/user/register",
                                             json_data={"username": username, "password": password}))

    def get_user_details(self, user_id):
        return decode_json(self.get_content(f"{self.api_url}/management/user/{user_id}"))

    def get_set_details(self, set_id):
        return decode_json(self.get_content(f"{self.api_url}/management/set/{set_id}"))

    def get_chart_details(self, chart_id):
        return decode_json(self.get_content(f"{self.api_url}/management/set/{chart_id}"))

    def get_reviews(self):
        return decode_json(self.get_content(f"{self.api_url}/set/reviews"))

    def add_review(self, set_id, status: bool, evaluation=None):
        return decode_json(self.post_content(f"{self.api_url}/set/{set_id}/review",
                                             json_data={"status": status, "evaluation": evaluation}))

    def start_review(self, set_id, status):
        return decode_json(self.post_content(f"{self.api_url}/set/{set_id}/review/start", json_data={"status": status}))

    def end_review(self, set_id, status: bool):
        return decode_json(self.post_content(f"{self.api_url}/set/{set_id}/review/end", json_data={"status": status}))


if __name__ == '__main__':
    example_user_id = "27c479a9-28eb-4b8e-990f-71f790ee02b2"
    example_set_id = "0nz4pnpk1u64phyhqvyh1gi6"
    example_chart_id = "ki1ck8wqlntsyl48688e0159"

    api = BombApi("http://localhost:10443/v1", username="Taskeren", password="123456")

    print(api.get_set(example_set_id))
    # print(api.get_set_by_name("Intel Sound Logo"))
    print(api.get_chart(example_chart_id))
    # print(api.get_user(example_user_id))
    # print(api.get_user_by_name("Taskeren"))
    # print(api.get_user_best_records_score(example_user_id))
    print(api.get_user_best_records_r_value(example_user_id))
    # print(api.get_set_by_chart_id(example_chart_id))
    # print(api.ping_auth())
    # print(api.register_user("Taskeren-Bot", "1024"))
    # print(api.get_user_details(example_user_id))
    # print(api.start_review("n07f8mbyk262p70x3xregl2b", "RANKED"))
    # print(api.get_reviews())
    # print(api.end_review("n07f8mbyk262p70x3xregl2b", True))
