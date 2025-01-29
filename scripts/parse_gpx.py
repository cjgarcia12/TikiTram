import xml.etree.ElementTree as ET

def parse_gpx(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

    # Extract waypoints
    waypoints = []
    for wpt in root.findall('gpx:wpt', ns):
        lat = float(wpt.get('lat'))
        lon = float(wpt.get('lon'))
        name = wpt.find('./gpx:name', ns).text if wpt.find('./gpx:name', ns) is not None else "None"
        desc = wpt.find('./gpx:desc', ns).text if wpt.find('./gpx:desc', ns) is not None else "None"

        waypoints.append({
            'lat': lat,
            'lon': lon,
            'name': name,
            'desc': desc
        })

    # Extract track points
    track_points = []
    for trkpt in root.findall(".//gpx:trkpt", ns):
        lat = float(trkpt.get('lat'))
        lon = float(trkpt.get('lon'))
        time = trkpt.find('./gpx:time', ns).text if trkpt.find('./gpx:time', ns) is not None else None

        track_points.append({
            'lat': lat,
            'lon': lon,
            'time': time
        })

    return {
        'waypoints': waypoints,
        'track_points': track_points
    }
