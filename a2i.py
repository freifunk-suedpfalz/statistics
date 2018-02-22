#!/usr/bin/env python3

import argparse
import os.path, time
import json
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
import datetime
from datetime import timezone

# parse arguments
parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file", type=str, help="path of file")
parser.add_argument("-H", "--hostname", type=str, required=False, help="influxdb host", default='localhost')
parser.add_argument("-P", "--port", type=int, required=False, help="influxdb port", default=8086)
parser.add_argument("-u", "--user", type=str, help="influxdb user")
parser.add_argument("-p", "--password", type=str, help="influxdb password")

args = parser.parse_args()

#measurement: 
#fields:      mgmt_tx_bytes
#             mgmt_tx_packets
#             mgmt_rx_bytes
#             mgmt_rx_packets
#             tx_bytes
#             tx_packets
#             tx_dropped
#             rx_bytes
#             rx_packets
#             forward_bytes
#             forward_packets
#             loadavg
#             rootfs_usage
#             uptime
#             clients
#             memory_usage
#             firstseen
#             lastseen
#             fastd_version
#             fastd_enabled
#             firmware_base
#             firmware_release
#             batman_version
#             batman_compat
#             branch
#             autoupdate
#             latitude
#             longitude
#             gateway
#             online
#tags:        nodeid
#             hostname
#             site_code
#             model
mNodes ='nodes' 

#create client
client = InfluxDBClient(args.hostname, args.port, args.user, args.password, mNodes)

#read json
jsondata = {}
try:
    with open(args.file) as data_file:
        jsondata = json.load(data_file)
except:
    print("Couldn't read json file: ")

# check every node in json
series=[] # data written ti influx
now = datetime.datetime.now(timezone.utc)
for node in jsondata['nodes']:
    print(jsondata['nodes'][node]['nodeinfo']['hostname'].encode("utf-8"))
    try:
        pointValues = {}
        pointValues['fields'] = {}
        pointValues['tags'] = {}
        pointValues['time'] = now 
        pointValues['measurement'] = mNodes

        # adding keys
        try:
            pointValues['fields']['mgmt_tx_bytes'] = float(jsondata['nodes'][node]['statistics']['traffic']['mgmt_tx']['bytes'])
        except:
            pass
        try:
            pointValues['fields']['mgmt_tx_packets'] = float(jsondata['nodes'][node]['statistics']['traffic']['mgmt_tx']['packets'])
        except:
            pass
        try:
            pointValues['fields']['mgmt_rx_bytes'] = float(jsondata['nodes'][node]['statistics']['traffic']['mgmt_rx']['bytes'])
        except:
            pass
        try:
            pointValues['fields']['mgmt_rx_packets'] = float(jsondata['nodes'][node]['statistics']['traffic']['mgmt_rx']['packets'])
        except:
            pass
        try:
            pointValues['fields']['tx_bytes'] = float(jsondata['nodes'][node]['statistics']['traffic']['tx']['bytes'])
        except:
            pass
        try:
            pointValues['fields']['tx_packets'] = float(jsondata['nodes'][node]['statistics']['traffic']['tx']['packets'])
        except:
            pass
        try:
            pointValues['fields']['tx_dropped'] = float(jsondata['nodes'][node]['statistics']['traffic']['tx']['dropped'])
        except:
            pass
        try:
            pointValues['fields']['rx_bytes'] = float(jsondata['nodes'][node]['statistics']['traffic']['rx']['bytes'])
        except:
            pass
        try:
            pointValues['fields']['rx_packets'] = float(jsondata['nodes'][node]['statistics']['traffic']['rx']['packets'])
        except:
            pass

        try:
            pointValues['fields']['forward_bytes'] = float(jsondata['nodes'][node]['statistics']['traffic']['forward']['bytes'])
        except:
            pass
        try:
            pointValues['fields']['forward_packets'] = float(jsondata['nodes'][node]['statistics']['traffic']['forward']['packets'])
        except:
            pass

        try:
            pointValues['fields']['loadavg'] = float(jsondata['nodes'][node]['statistics']['loadavg'])
        except:
            pass
        try:
            pointValues['fields']['rootfs_usage'] = float(jsondata['nodes'][node]['statistics']['rootfs_usage'])
        except:
            pass
        try:
            pointValues['fields']['uptime'] = float(jsondata['nodes'][node]['statistics']['uptime'])
        except:
            pass
        try:
            pointValues['fields']['clients'] = float(jsondata['nodes'][node]['statistics']['clients'])
        except:
            pass
        try:
            pointValues['fields']['memory_usage'] = float(jsondata['nodes'][node]['statistics']['memory_usage'])
        except:
            pass
        try:
            pointValues['fields']['firstseen'] = jsondata['nodes'][node]['firstseen']
        except:
            pass
        try:
            pointValues['fields']['lastseen'] = jsondata['nodes'][node]['lastseen']
        except:
            pass
        try:
            pointValues['fields']['fastd_version'] = jsondata['nodes'][node]['nodeinfo']['software']['fastd']['version']
        except:
            pass
        try:
            pointValues['fields']['fastd_enabled'] = jsondata['nodes'][node]['nodeinfo']['software']['fastd']['enabled']
        except:
            pass
        try:
            pointValues['fields']['firmware_base'] = jsondata['nodes'][node]['nodeinfo']['software']['firmware']['base']
        except:
            pass
        try:
            pointValues['fields']['firmware_release'] = jsondata['nodes'][node]['nodeinfo']['software']['firmware']['release']
        except:
            pass
        try:
            pointValues['fields']['batman_version'] = jsondata['nodes'][node]['nodeinfo']['software']['batman-adv']['version']
        except:
            pass
        try:
            pointValues['fields']['batman_compat'] = str(jsondata['nodes'][node]['nodeinfo']['software']['batman-adv']['compat'])
        except:
            pass
        try:
            pointValues['fields']['branch'] = jsondata['nodes'][node]['nodeinfo']['software']['autoupdater']['branch']
        except:
            pass
        try:
            pointValues['fields']['autoupdate'] = jsondata['nodes'][node]['nodeinfo']['software']['autoupdater']['enabled']
        except:
            pass
        try:
            pointValues['fields']['latitude'] = jsondata['nodes'][node]['nodeinfo']['location']['latitude']
        except:
            pass
        try:
            pointValues['fields']['longitude'] = jsondata['nodes'][node]['nodeinfo']['location']['longitude']
        except:
            pass
        try:
            pointValues['fields']['gateway'] = jsondata['nodes'][node]['flags']['gateway']
        except:
            pass
        try:
            pointValues['fields']['online'] = jsondata['nodes'][node]['flags']['online']
        except:
            pass
        
        # adding tags
        try:
            pointValues['tags']['nodeid'] = jsondata['nodes'][node]['nodeinfo']['node_id']
        except:
            pass
        try:
            pointValues['tags']['site_code'] = jsondata['nodes'][node]['nodeinfo']['system']['site_code']
        except:
            pass
        try:
            pointValues['tags']['model'] = jsondata['nodes'][node]['nodeinfo']['hardware']['model']
        except:
            pass
        try:
            pointValues['tags']['hostname'] = jsondata['nodes'][node]['nodeinfo']['hostname']
        except:
            pass 
        series.append(pointValues)
    except KeyError:
        pass

print("Create database: " + mNodes)
try:
    client.create_database(mNodes)
except InfluxDBClientError:
    print("Database already existing, skipping creation")
pass

client.write_points(series)
print("Data written to influxdb!")
