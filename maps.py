import requests, os, sys, json
import datetime, pytz

HERE_ID=os.environ['HERE_APP_ID']
HERE_CODE=os.environ['HERE_APP_CODE']

SF = (37.7905419,-122.3956178)
PA = (37.4436798,-122.1630251)
MV = (37.3980360,-122.0895727)
RD = (37.434661,-122.3301351)

def dist(a, b):
    """ a and b should be (lat,lon) tuples
    """
    base_url="https://route.api.here.com/routing/7.2/calculateroute.json?"
    payload = {'app_id':HERE_ID, 
               'app_code':HERE_CODE,
               'waypoint0':'geo!'+','.join([str(i) for i in a]),
               'waypoint1':'geo!'+','.join([str(i) for i in b]),
               'mode':'fastest;car;traffic:disabled',
              }
    resp = requests.get(base_url, params=payload)
    data = json.loads(resp.content)
    #import ipdb; ipdb.set_trace()
    summary = data['response']['route'][0]['summary']
    return {"distance" : summary['distance'], 
            "trafficTime" : summary["trafficTime"],
            "baseTime" : summary["baseTime"]}

def via_dist(src, dst, pitstops):
    base_url="https://wse.api.here.com/2/findsequence.json"
    payload = {'app_id':HERE_ID, 
               'app_code':HERE_CODE,
	       'start':','.join([str(src[0]),str(src[1])]),
	       'end':','.join([str(dst[0]),str(dst[1])]),
               'mode':'fastest;car',
               'departure':datetime.datetime.now(pytz.utc).isoformat()+'Z'
               }
    for i,stop in enumerate(pitstops):
        payload['destination'+str(i+1)] = ','.join([str(stop[0]),str(stop[1])])
    resp = requests.get(base_url, params=payload)
    data = json.loads(resp.content)
    print(data)
    import ipdb; ipdb.set_trace()
    summary = data['response']['route'][0]['summary']
    print(summary)

def detour(src, dst, pitstop):
    """
    given s, d and p find an x, such that
    s-x-d + 2*p-x is the smallest
    ...
    brute force it!
    """
    options = on_path([src, dst],query='shell gas station', size=10,urgency=0)
    ret = []
    for place in options:
        title = place['title']
        x = place['latlon']
        addr = place['address']
        A_X = dist(src, x); X_B = dist(x, dst)
        consumer_dist = A_X['distance'] + X_B['distance']
        tour_time = A_X['trafficTime']+X_B['trafficTime']
        last_mile_dist = 2*dist(pitstop, x)['distance']
        total_trip_dist = consumer_dist + last_mile_dist
        carbon_print = total_trip_dist/(1e3 * .621 * .70548)
        ret.append({"distance" : consumer_dist,
                    "latlon" : x,
                    "title" : title,
                    "time" : tour_time,
                    "address" : addr,
                    "carbon" : carbon_print})
        ret = sorted(ret, key=lambda loc: loc.get('distance'))
        #print(total_trip_dist, consumer_dist, last_mile_dist)

    # worst carbon
    consumer_dist = dist(src, dst)['distance']
    last_mile_dist = 2*dist(pitstop, dst)['distance']
    total_trip_dist = consumer_dist + last_mile_dist
    carbon_print = total_trip_dist/(1e3 * .621 * .70548)
    #print(total_trip_dist, consumer_dist, last_mile_dist)

    # worst case time A - C - B
    A_C = dist(src, pitstop)
    C_B = dist(pitstop, dst)
    total_time = A_C['trafficTime'] + C_B['trafficTime']
    return {"meetpoints" : ret, 'worst_time' : total_time, "worst_carbon" : carbon_print}

def route(a, b):
    url="https://route.api.here.com/routing/7.2/calculateroute.json?app_id="+HERE_ID+"&app_code="+HERE_CODE
    url+="&waypoint0=geo!"+','.join([str(i) for i in a])
    url+="&waypoint1=geo!"+','.join([str(i) for i in b])
    url+="&mode=fastest;car;traffic:disabled"
    resp = requests.get(url)
    data = json.loads(resp.content)
    print(json.dumps(data))

def on_path(route, query, urgency=1, close_to=None,size=20):
    """
    --data-urlencode 'at=37.5943,-122.2426' \
    --data-urlencode 'q=gas station' \
    --data-urlencode 'route=[37.7905419,-122.3956178|37.4436798,-122.1630251|37.3980360,-122.0895727]' \
    --data-urlencode 'urgency=1'
    """

    base_url='https://places.cit.api.here.com/places/v1/browse'
    #import ipdb; ipdb.set_trace()
    route_str = '['+str('|'.join([','.join([str(i[0]),str(i[1])]) for i in route]))+']'
    payload = {'app_id':HERE_ID, 
               'app_code':HERE_CODE,
               'q':query,
               'route':route_str,
               'urgency':urgency,
               'size':size}
    resp = requests.get(base_url, params=payload)
    data = json.loads(resp.content)
    results = data['results']['items']
    ret = []
    for loc in results:
        ret.append({'title'  : loc['title'],
                    'latlon' : loc['position'],
                    'address': loc['vicinity']})
    return ret

def in_area(center, query, radius=20000, size=20):
    #--data-urlencode 'in=37.5525143,-122.3291306;r=20000' \
    #--data-urlencode 'q=shell gas station'

    base_url='https://places.cit.api.here.com/places/v1/browse'
    in_str = ','.join([str(center[0]),str(center[1])])+';r='+str(radius)
    payload = {'app_id':HERE_ID, 
               'app_code':HERE_CODE,
               'q':query,
               'in': in_str,
               'size':size,
	      }
    resp = requests.get(base_url, params=payload)
    data = json.loads(resp.content)
    results = data['results']['items']
    ret = []
    for loc in results:
        ret.append({'title'  : loc['title'],
                    'latlon' : loc['position'],
                    'address': loc['vicinity']})
    return ret

if __name__ == "__main__":
    route = [SF,PA,MV]
    #print(via_dist(SF, MV, [RD, PA]))
    print(dist(SF, MV))
    #print(on_path(route, 'restaurants'))
    #print(in_area(SF, 'shell gas stations'))

    print(detour(SF, MV, RD))
    #stop_locations = [1,2,3,4,5]
    #for i in range(len(stop_locations)):
    #    for j in range(i+1,len(stop_locations)):
    #        print(stop_locations[i],stop_locations[j])
    #print(dist(SF, PA))
