from smartapi import SmartConnect
import pyotp

def login_angelone(api_key: str, client_code: str, password: str, totp_secret: str):
    """Angel One SmartAPI में लॉगिन करें और ऑब्जेक्ट लौटाएं"""
    obj = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(totp_secret).now()
    data = obj.generateSession(client_code, password, totp)
    if data and data.get("status"):
        return obj
    else:
        raise Exception(f"Login failed: {data}")
