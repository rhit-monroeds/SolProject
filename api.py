import requests

url = "https://pro-api.solscan.io/v2.0/account/transfer?address=BUqVWGnrHj92Ej5qZkyMUy47EFvnVW1B4BzdMDNpux4J&page=1&page_size=100"

headers = {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MjMxNzE0NTQ0MjgsImVtYWlsIjoiZGVhbm1vbnJvZTI4QGdtYWlsLmNvbSIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOiJ2MiIsImlhdCI6MTcyMzE3MTQ1NH0.CbKikRboPJ8jgkLPskpAOGpOQ2nuppiXyRcQ7oWln-8"}

response = requests.get(url, headers=headers)

print(response.text)

