import json
from websocket import create_connection
import requests
import uuid
api_key="z307734GALvx"
myboatapikey="Clé API"
username="Addresse email"
password="Mot de passe"
device_id=str(uuid.uuid4())
requestidnum=0
def requestid():
    global requestidnum
    requestold=requestidnum
    requestidnum += 1
    return  requestold

def myboatvro(nonce):
    response = requests.get('https://myboatvro.000webhostapp.com/update.php?apikey='+myboatapikey+"&nonce="+nonce, verify=False)
    print(response.text)
    data=json.loads(response.text)
    if(data["error"]=="None"):
        return data["key"]
    else:
        print(data["error"])
def returnurl():
    global urlconnect
    ws = create_connection(
        "wss://live-" + api_key + ".ws.gamesparks.net/ws/device/" + api_key + "?deviceOS=WEBGL&deviceID=" + device_id + "&SDK=Unity")
    ws.send("")

    results = ws.recv()
    loaded = json.loads(results)
    ws.close()
    urlconnect = loaded["connectUrl"]
    print("Connection url is '%s'" % urlconnect)


def authwss():
    if (urlconnect):
        ws = create_connection(urlconnect)
        authrep = ws.recv()
        authreploaded = json.loads(authrep)
        print(authreploaded)
        authsend = {"@class": ".AuthenticatedConnectRequest", "hmac": myboatvro(authreploaded["nonce"]), "os": "WEBGL",
                    "platform": "WebGLPlayer", "deviceId": device_id}

        print(json.dumps(authsend))
        ws.send(json.dumps(authsend))
        logrep=json.loads(ws.recv())
        print(logrep)
        authask={"@class": ".AuthenticationRequest", "userName":username , "password":password ,
         "requestId": "646212512120000_"+str(requestid())}
        ws.send(json.dumps(authask))
        logrep=json.loads(ws.recv())
        print(logrep)
    else:
        return 0
    return ws
def requestdata(request):
    if(ws):
        getdata = json.dumps(request)
        ws.send(getdata)
        data = json.loads(ws.recv())
        if(data["@class"]==".ScriptMessage"):
            data = json.loads(ws.recv())
        return data
    else:
        return 0
returnurl()
ws = authwss()
user={"@class":".AccountDetailsRequest","requestId":"63744542013080000_"+str(requestid())}
print(requestdata(user))
ws.close()
