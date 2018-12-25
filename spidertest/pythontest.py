import requests

url = "http://www.emailcamel.com/api/batch/validate"

data = {
    "usr": "wuzeronger@163.com",
    "pwd": "wuzeronger123",
    "emailaddresslist": "administrator@petshopboys-forum.com"
}
response = requests.post(url=url, data=data)

print(response.text)
