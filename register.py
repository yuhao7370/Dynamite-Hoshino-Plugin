import requests

bomb = "http://43.142.173.63:10483/graphql"

def make_query(query, variables, url):
    """
    Make query response
    """
    request = requests.post(url, json={'query': query, 'variables': variables},verify = False)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

# query = """
# mutation { registerUser(username: "Official_test", password: "123") { _id } }
# mutation { registerUser(username: 'Official_test', password: '123') { _id } }
# """

# {'data': {'registerUser': {'_id': '06f4141a-587c-43e9-8c5c-042fe95496f3'}}}

def register(username, password):
    query = 'mutation { registerUser(username: "' + username + '", password: "' + password +'") { _id } }'
    # print(query)
    variables = {}
    get = make_query(query, variables, bomb)
    try:
        id = get["data"]["registerUser"]["_id"]
        return True, id
    except:
        error = get["errors"][0]["message"]
        return False, error

# register("Official_test", "123")
