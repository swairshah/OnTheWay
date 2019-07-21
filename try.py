import requests, os, sys, json

HERE_ID=os.environ['HERE_APP_ID']
HERE_CODE=os.environ['HERE_APP_CODE']

url="https://route.api.here.com/routing/7.2/calculateroute.json?app_id="+HERE_ID+"&app_code="+HERE_CODE+"&waypoint0=geo!52.5,13.4&waypoint1=geo!52.5,13.45&mode=fastest;car;traffic:disabled"
resp = requests.get(url)
data = json.loads(resp.content)
print(json.dumps(data))

# pickup query
"""
curl "https://wse.api.here.com/2/findpickups.json?mode=fastest;car;traffic:disabled&start=waypoint0;50.115620,8.631210&departure=2016-10-14T07:30:00+02:00&vehicleCost=0.29&driverCost=20&maxDetour=60&restTimes=disabled&end=waypoint3;50.132540,8.649280&destination0=waypoint1;50.122540,8.631070;pickup:LOAD2&destination1=waypoint2;50.128920,8.629830;drop:LOAD2,value:200&app_id=j4v3GnGNQNr6OQEWeMaV&app_code=A_w_5ugF64DW8KgbRbryhQ"
"""

# optimized waypoint query
"""
https://wse.api.here.com/2/findsequence.json?start=Berlin-Main-Station;52.52282,13.37011&destination1=East-Side-Gallery;52.50341,13.44429&destination2=Olympiastadion;52.51293,13.24021&end=HERE-Berlin-Campus;52.53066,13.38511&mode=fastest;car&app_id=j4v3GnGNQNr6OQEWeMaV&app_code=A_w_5ugF64DW8KgbRbryhQ"
"""
