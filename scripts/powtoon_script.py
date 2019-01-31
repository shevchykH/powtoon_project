import requests
from rest_framework.utils import json

AUTH_ENDPOINT = "http://127.0.0.1:8000/api-auth/jwt/"
REFRESH_ENDPOINT = AUTH_ENDPOINT + "refresh/"
ENDPOINT = "http://127.0.0.1:8000/powtoons/"



headers = {
    "Content-Type": "application/json"
}


data = {
    "username": "user2",
    "password": "Welcome!@"
}

r = requests.post(AUTH_ENDPOINT, data=json.dumps(data), headers=headers)
token = r.json()["token"]
print r.json()
print token


refresh_data = {
    "token": token
}

# r2 = requests.post(REFRESH_ENDPOINT, data=json.dumps(refresh_data), headers=headers)
# print r2.json()


print "GET POWTOONS"
headers["Authorization"] = "JWT " + token
r = requests.get(ENDPOINT, headers=headers)
for p in r.json():
    print p

print "SHARE POWTOON TO USER WITH PK "
post_data = json.dumps({"user_id": 3})
new_r = requests.post(ENDPOINT + str(9) + "/share/", data=post_data, headers=headers)
print new_r.text


