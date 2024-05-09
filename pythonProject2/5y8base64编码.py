import base64

username = "deyuTech"
password = "deyuES%"
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
print(encoded_credentials)