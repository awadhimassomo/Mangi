from django.http import JsonResponse
import http.client
import json
import base64

import http.client

def send_message(request):
    username="massomo"
    password="e#h%f3+Hr3rGVJy"
    auth_encoded = base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
    try:
        conn = http.client.HTTPSConnection("mp5vn2.api.infobip.com")
        payload = json.dumps({
            "messages": [
                {
                    "destinations": [{"to":"255742178726"}],
                    "from": "255687046323",
                    "text": "Congratulations on sending your first message.\nGo ahead and check the delivery report in the next step."
                }
            ]
        })
        headers = {
            'Authorization': f'Basic {auth_encoded}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        conn.request("POST", "/sms/2/text/advanced", payload, headers)
        res = conn.getresponse()
        data = res.read()
        return JsonResponse(data.decode("utf-8"), safe=False)
    except Exception as e:
        return JsonResponse({"error":str(e)}, safe=False)


   