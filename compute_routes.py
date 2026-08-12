import json, urllib.request, urllib.parse

POINTS = {
    "home": (40.667194, -111.875831),
    "farmington_bay": (40.9614844, -111.9287645),
    "antelope_island": (41.0893447, -112.1131350),
    "bear_river_refuge": (41.5076743, -112.0690714),
    "crystal": (41.6590, -112.0880),
    "malad": (42.186055, -112.246200),
    "devil_creek": (42.299400, -112.204022),
    "mccammon": (42.650472, -112.193022),
    "lava": (42.619220, -112.005689),
    "soda_springs": (42.653575, -111.600674),
    "hooper_springs": (42.672109, -111.594120),
    "niter_ice_cave": (42.53333, -111.73278),
    "bear_river_massacre": (42.110151, -111.877719),
    "preston": (42.095438, -111.876716),
    "bear_river_hs": (42.164460, -111.837770),
    "maple_grove": (42.309060, -111.707924),
    "franklin": (42.0171679, -111.7994599),
    "logan": (41.732420, -111.834766),
    "brigham_city": (41.505424, -112.014901),
    "ogden": (41.22083, -111.97972),
    "lagoon": (40.9859653, -111.8927528),
    "eaglewood": (40.831940, -111.888103),
}

def osrm_route(names):
    coords = ";".join(f"{POINTS[n][1]},{POINTS[n][0]}" for n in names)
    url = f"https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson&steps=false"
    with urllib.request.urlopen(url, timeout=30) as r:
        data = json.load(r)
    route = data["routes"][0]
    legs = route["legs"]
    geometry = route["geometry"]["coordinates"]  # [lng,lat] pairs
    latlng_geometry = [[round(lat,5), round(lng,5)] for lng, lat in geometry]
    leg_info = [{"from": names[i], "to": names[i+1], "distance_mi": round(l["distance"]/1609.34,1)} for i,l in enumerate(legs)]
    total_mi = round(route["distance"]/1609.34,1)
    return {"legs": leg_info, "geometry": latlng_geometry, "total_mi": total_mi}

outbound_names = ["home","farmington_bay","antelope_island","bear_river_refuge","crystal","malad","devil_creek","mccammon","lava"]
return_names = ["lava","soda_springs","hooper_springs","niter_ice_cave","bear_river_massacre","preston","bear_river_hs","maple_grove","franklin","logan","brigham_city","ogden","lagoon","eaglewood","home"]

outbound = osrm_route(outbound_names)
return_r = osrm_route(return_names)

result = {"outbound": outbound, "return": return_r}
with open("/home/user/workspace/roadtrip/route_calc.json","w") as f:
    json.dump(result, f, indent=2)

print("OUTBOUND legs:")
for l in outbound["legs"]:
    print(f"  {l['from']} -> {l['to']}: {l['distance_mi']} mi")
print("OUTBOUND total:", outbound["total_mi"], "mi")
print()
print("RETURN legs:")
for l in return_r["legs"]:
    print(f"  {l['from']} -> {l['to']}: {l['distance_mi']} mi")
print("RETURN total:", return_r["total_mi"], "mi")
