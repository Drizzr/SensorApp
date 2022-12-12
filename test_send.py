import requests
data = {"password": "dialvdmgm", "email": "samuelfriese@gmx.net", "timestamp": "2022-09-28T15:15:02.081027", "values": {"Temperatur": 30, "Luftfeuchtigkeit": 40}}
header = {'x-access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwdWJsaWNfaWQiOiJmNWQ5M2I2Yi1lZGEzLTRjZTgtOWFhMS1iMjJlNGM5ZDRhYzMiLCJleHAiOjE2NjQzODM5NDR9.klcn4nza7HyA6tfbobJIaPW25jTkcFZLBD20hUvvzwk', 'x-refresh-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwdWJsaWNfaWQiOiJmNWQ5M2I2Yi1lZGEzLTRjZTgtOWFhMS1iMjJlNGM5ZDRhYzMiLCJleHAiOjE2NjY5NjUxNDR9.UOnoaKd8IXtbS58mTTMShkxXKPT4NMPvT_7-vRS6q10'}

#sensor/5e40f64dd4ed3257/update
response = requests.post("http://192.168.178.109:5000/api/sensor/8c35f9a0c4f0f9cf/update", json=data, headers=header)

print(response.json())