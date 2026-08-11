import json
from xml.sax.saxutils import escape

d = json.load(open('/home/user/workspace/roadtrip/map_data_export.json'))
stops = d['stops']
outbound = d['outbound']
ret = d['ret']
alt = d['alt']
IMAGE_MAP = json.load(open('/home/user/workspace/roadtrip/image_map.json'))

def hex_to_kml_color(hexcolor, alpha="ff"):
    hexcolor = hexcolor.lstrip('#')
    r, g, b = hexcolor[0:2], hexcolor[2:4], hexcolor[4:6]
    return f"{alpha}{b}{g}{r}"

OUTBOUND_COLOR = hex_to_kml_color("b8502a")
RETURN_COLOR = hex_to_kml_color("2b6ca0")
ALT_COLOR = hex_to_kml_color("2a7f7e")

ICONS = {
    "start": "https://maps.google.com/mapfiles/kml/paddle/grn-stars.png",
    "spring": "https://maps.google.com/mapfiles/kml/paddle/blu-circle.png",
    "mid": "https://maps.google.com/mapfiles/kml/paddle/red-circle.png",
}

def coords_to_kml(coord_pairs):
    # input is [lat, lng] pairs -> KML wants "lng,lat,0"
    return " ".join(f"{lng},{lat},0" for lat, lng in coord_pairs)

def get_photo_urls(s, index):
    if s.get("gallery"):
        return [IMAGE_MAP.get(g["file"]) for g in s["gallery"] if IMAGE_MAP.get(g["file"])]
    if s.get("img"):
        url = IMAGE_MAP.get(s["img"])
        return [url] if url else []
    if s.get("role") == "start":
        return []
    default_key = f"img/stop-{index}.jpg"
    url = IMAGE_MAP.get(default_key)
    return [url] if url else []

def build_description(s, index):
    parts = []
    photos = get_photo_urls(s, index)
    for url in photos:
        parts.append(f'<img src="{escape(url)}" style="width:100%;max-width:320px;border-radius:6px;margin-bottom:8px" />')
    if s.get("tag"):
        parts.append(f'<div style="color:#666;font-size:12px;margin-bottom:6px">{escape(s["tag"])}</div>')
    note = s.get("note") or s.get("desc") or ""
    if note:
        parts.append(f'<p style="margin:0 0 10px 0">{escape(note)}</p>')
    if s.get("address"):
        parts.append(f'<div style="margin-bottom:8px"><b>Address:</b> {escape(s["address"])}</div>')
    dining = s.get("dining")
    if dining:
        parts.append('<div style="margin-top:8px"><b>Nearby dining</b><ul style="margin:4px 0 0 0;padding-left:18px">')
        for item in dining:
            name = escape(item.get("name", ""))
            desc = escape(item.get("desc", ""))
            credit = item.get("credit")
            credit_url = item.get("creditUrl")
            line = f'<li><b>{name}</b> &mdash; {desc}'
            if credit and credit_url:
                line += f' <a href="{escape(credit_url)}" target="_blank">({escape(credit)})</a>'
            line += '</li>'
            parts.append(line)
        parts.append('</ul></div>')
    credit = s.get("credit")
    credit_url = s.get("creditUrl")
    if credit and credit_url and not dining:
        parts.append(f'<div style="margin-top:8px;font-size:11px;color:#888">Photo reference: <a href="{escape(credit_url)}" target="_blank">{escape(credit)}</a></div>')
    return "".join(parts)

placemarks = []
for i, s in enumerate(stops):
    style = "start" if s.get("role") == "start" else ("spring" if s.get("pinStyle") == "spring" else "mid")
    num_label = "S" if s.get("role") == "start" else str(i)
    label = f"{num_label} \u00b7 {s['name']}"
    desc_html = build_description(s, i)
    placemarks.append(f"""
    <Placemark>
      <name>{escape(label)}</name>
      <styleUrl>#{style}Pin</styleUrl>
      <description><![CDATA[{desc_html}]]></description>
      <Point><coordinates>{s['lng']},{s['lat']},0</coordinates></Point>
    </Placemark>""")

route_placemarks = f"""
    <Placemark>
      <name>Outbound route (Murray to Lava Hot Springs)</name>
      <styleUrl>#outboundLine</styleUrl>
      <LineString><tessellate>1</tessellate><coordinates>{coords_to_kml(outbound)}</coordinates></LineString>
    </Placemark>
    <Placemark>
      <name>Return route (via Preston &amp; Logan)</name>
      <styleUrl>#returnLine</styleUrl>
      <LineString><tessellate>1</tessellate><coordinates>{coords_to_kml(ret)}</coordinates></LineString>
    </Placemark>
    <Placemark>
      <name>Alternate return (via Bear Lake)</name>
      <styleUrl>#altLine</styleUrl>
      <LineString><tessellate>1</tessellate><coordinates>{coords_to_kml(alt)}</coordinates></LineString>
    </Placemark>"""

MAP_DESCRIPTION = (
    "Utah \u00b7 Idaho \u2014 Sunday Drive. North on I-15 through Malad and McCammon to the hot pools, "
    "then home by Soda Springs, Preston, and Logan \u2014 Sunday, August 16. Gold-marked stops are soaking springs. "
    "15 stops \u00b7 161.7 mi outbound \u00b7 202.7 mi return \u00b7 ~7h 30m total drive time."
)

kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Saltas Family August "SPRING" Break \u2014 Murray to Lava Hot Springs Road Trip</name>
  <description><![CDATA[{MAP_DESCRIPTION}]]></description>
  <Style id="startPin"><IconStyle><Icon><href>{ICONS['start']}</href></Icon></IconStyle></Style>
  <Style id="springPin"><IconStyle><Icon><href>{ICONS['spring']}</href></Icon></IconStyle></Style>
  <Style id="midPin"><IconStyle><Icon><href>{ICONS['mid']}</href></Icon></IconStyle></Style>
  <Style id="outboundLine"><LineStyle><color>{OUTBOUND_COLOR}</color><width>4</width></LineStyle></Style>
  <Style id="returnLine"><LineStyle><color>{RETURN_COLOR}</color><width>4</width></LineStyle></Style>
  <Style id="altLine"><LineStyle><color>{ALT_COLOR}</color><width>3</width></LineStyle></Style>

  <Folder>
    <name>Stops</name>
    {"".join(placemarks)}
  </Folder>
  <Folder>
    <name>Routes</name>
    {route_placemarks}
  </Folder>
</Document>
</kml>
"""

out_path = "/home/user/workspace/roadtrip/Saltas_Spring_Break_Road_Trip.kml"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(kml)
print("wrote", out_path, len(kml), "bytes")

# Stops-only variant (no route lines) for Google My Maps import as a single layer of pins/photos.
kml_stops_only = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Saltas Spring Break \u2014 Stops with Photos</name>
  <description><![CDATA[{MAP_DESCRIPTION}]]></description>
  <Style id="startPin"><IconStyle><Icon><href>{ICONS['start']}</href></Icon></IconStyle></Style>
  <Style id="springPin"><IconStyle><Icon><href>{ICONS['spring']}</href></Icon></IconStyle></Style>
  <Style id="midPin"><IconStyle><Icon><href>{ICONS['mid']}</href></Icon></IconStyle></Style>

  {"".join(placemarks)}
</Document>
</kml>
"""

out_path2 = "/home/user/workspace/roadtrip/Saltas_Spring_Break_Stops_With_Photos.kml"
with open(out_path2, "w", encoding="utf-8") as f:
    f.write(kml_stops_only)
print("wrote", out_path2, len(kml_stops_only), "bytes")
