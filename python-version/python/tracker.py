from google.transit import gtfs_realtime_pb2
import requests
import time
import argparse


NORTH = 'N'
SOUTH = 'S'
DEFAULT_STATION = 'G28'
DEFAULT_TRAIN_URL  = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g'



# Gets the arrival times of the next trains
# Gets the north direction and the south direction
# Station is a string, a station from https://data.ny.gov/Transportation/MTA-Subway-Stations/39hk-dx4f/data_preview
def get_next_arrivals(url: str, station: str) -> tuple[list[int], list[int]]:
    northbound = []
    southbound = []
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(url)
    feed.ParseFromString(response.content)
    trip_updates = map(lambda x: x.trip_update, filter(lambda entity: True if entity.HasField('trip_update') else False, feed.entity))
    for trip_update in trip_updates:
        if trip_update.StopTimeUpdate:
            for stop_time_update in trip_update.stop_time_update:
                if stop_time_update.stop_id == station+NORTH:
                    northbound.append(stop_time_update.departure.time)
                elif stop_time_update.stop_id ==station+SOUTH:
                    southbound.append(stop_time_update.departure.time)
    return (sorted(northbound), sorted(southbound))


def print_help():
    print("""
required: -u, --url String for URL of the GTFS data
required: -s, --station String for Station ID https://data.ny.gov/Transportation/MTA-Subway-Stations/39hk-dx4f/data_preview
""")

def main():
  while True:
    parser = argparse.ArgumentParser(
                    prog='SubwayTracker',
                    description='Acquires the data for subways at a given station. Needs to give an exact station/line',
                    usage='%(prog)s [options]')
    parser.add_argument('-u', '--url', help='GTFS api endpoint')
    parser.add_argument('-s', '--station', help='Station ID from https://data.ny.gov/Transportation/MTA-Subway-Stations/39hk-dx4f/data_preview')
    args = parser.parse_args()

    station = DEFAULT_STATION
    train_url = DEFAULT_TRAIN_URL
    if args.station:
        station = args.station
    if args.url:
        train_url = args.url


    northbound, southbound = get_next_arrivals(train_url, station)
    next_northbound = min(northbound)
    next_southbound = min(southbound)
    now = time.time()

    print((next_northbound - now) // 60)
    print((next_southbound - now) // 60)
    time.sleep(60)


if __name__ == "__main__":
    main()





