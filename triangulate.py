# coding=UTF-8
import math
import random

earth_radians = 6378.1
timeinterval = 5
timeintervalsec = timeinterval * 60
# define Op Area in Decimal degrees (Random place in the Norwegian Sea)
latmin = 62.50
latmax = 63.50
longmin = 0.5
longmax = 4.35

boundries = {"min": 8 * 1.852 * 1000, "max": 12 * 1.852 * 1000}

Uboat = {}


def randomGeo(centre, radius):
    y0 = centre.position["latitude"]
    x0 = centre.position["longitude"]
    rd = radius / 111300

    u = random.random()
    v = random.random()

    w = rd * math.sqrt(u)
    t = 2 * math.pi * v
    x = w * math.cos(t)
    y = w * math.sin(t)

    xp = x / math.cos(y0)

    return {"latitude": y + y0, "longitude": xp + x0}


def generate_location(centre, boundries):
    oy = centre.position["latitude"]
    ox = centre.position["longitude"]

    eqdegrees = earth_radians * 2 * math.pi / 360 * 1000
    r = ((boundries['max'] - boundries['min'] + 1) * random.random())
    # Random Angle
    theta = random.random() * 2 * math.pi

    dy = r * math.sin(theta)
    dx = r * math.cos(theta)

    return {
        "latitude": oy + dy / eqdegrees,
        "longitude": ox + dx / (eqdegrees * math.cos(math.radians(oy)))
    }


def get_compass_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    # if (type(pointA) != tuple) or (type(pointB) != tuple):
    #    raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA["latitude"])
    lat2 = math.radians(pointB["latitude"])

    diffLong = math.radians(pointB["longitude"] - pointA["longitude"])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (
        math.sin(lat1) * math.cos(lat2) * math.cos(diffLong)
    )

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return round(compass_bearing)


class boat:
    def __init__(self, name):
        self.name = name
        self.position = {}

    def generate_position(self):
        if self.name == "Uboat":
            self.position["latitude"] = random.uniform(latmin, latmax)
            self.position["longitude"] = random.uniform(longmin, longmax)
        else:
            self.position = generate_location(uboat, boundries)

    def set_speed(self, speed=None):
        if speed is not None:
            self.speed = speed
        else:
            self.speed = round(random.uniform(3, 6) * 2) / 2

    def set_heading(self, heading=None):
        if heading is None:
            self.heading = random.randint(0, 359)
        else:
            self.heading = heading

    def move_boat(self):
        bearing_radians = math.radians(self.heading)
        speedms = self.speed * 0.51444444444
        distancekm = speedms * timeintervalsec / 1000

        origin_lat_radians = math.radians(self.position["latitude"])
        origin_lon_radians = math.radians(self.position["longitude"])

        dest_lat_radians = math.asin(
            math.sin(origin_lat_radians) * math.cos(distancekm / earth_radians)
            + math.cos(origin_lat_radians)
            * math.sin(distancekm / earth_radians)
            * math.cos(bearing_radians)
        )

        dest_lon_radians = origin_lon_radians + math.atan2(
            math.sin(bearing_radians)
            * math.sin(distancekm / earth_radians)
            * math.cos(origin_lat_radians),
            math.cos(distancekm / earth_radians)
            - math.sin(origin_lat_radians) * math.sin(dest_lat_radians),
        )

        self.position = {
            "latitude": math.degrees(dest_lat_radians),
            "longitude": math.degrees(dest_lon_radians),
        }


# Spawn boat in a random position with a random heading travelling at 9 knots
uboat = boat("Uboat")
uboat.generate_position()
uboat.set_heading()
uboat.set_speed(9)

# Spawn Convoy at a random position between 'Boundries' distance of boat,
# travelling in a random direction at between 3 and 6 kts
convoy = boat("Convoy")
convoy.generate_position()
convoy.set_heading()
convoy.set_speed()

bearings = 1
while bearings <= 4:
    try:
        newspeed = input("Set UBoat Speed (%s)" % uboat.speed)
    except SyntaxError:
        newspeed = uboat.speed

    try:
        newheading = input("Set Uboat Heading (%s)" % uboat.heading)
    except SyntaxError:
        newheading = uboat.heading

    uboat.set_speed(speed=newspeed)
    uboat.set_heading(heading=newheading)
    uboat.move_boat()
    convoy.move_boat()
    print(
        "Boat Position - Lat: %s Lon: %s Heading: %s Speed: %s"
        % (
            uboat.position['latitude'],
            uboat.position['longitude'],
            uboat.heading,
            uboat.speed
        )
    )

    print(
        "Convoy Position - Lat: %s Lon: %s Bearing: %s Speed: %s"
        % (
            convoy.position["latitude"],
            convoy.position["longitude"],
            get_compass_bearing(uboat.position, convoy.position),
            convoy.speed
        )
    )
    bearings = bearings + 1
