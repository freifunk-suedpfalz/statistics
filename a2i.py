#!/usr/bin/env python3
import argparse

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
import datetime
from datetime import timezone
import time
import json

def main(file, hostname='localhost', port=8086, username='user', password='pass', database='freifunk'):
    jsondata = {}
    jsondata=read_jsonfile(file)
    series=create_series(jsondata)

    client = InfluxDBClient(hostname, port, username, password, database)

    print("Create database: " + database)
    try:
        client.create_database(database)
    except InfluxDBClientError:
        print("Database already existing, skipping creation")
        pass

    print("Create a retention policy")
    try:
        retention_policy = 'freifunk_policy'
        client.create_retention_policy(retention_policy, '3d', 1, default=True)
    except InfluxDBClientError:
        print("Retention policy existing, skipping creation")
        pass
    client.write_points(series, retention_policy=retention_policy)
    print("Data written to influxdb!")

def read_jsonfile(file):
    jsondata = {}
    try:
        with open(file) as data_file:
            jsondata = json.load(data_file)
    except:
        print("Couldn't read json file: ")
    return jsondata

def create_series(jsondata):
    series=[]
    now = datetime.datetime.now(timezone.utc)
    print(now)
    for node in jsondata['nodes']:
        data={}
        keys={'loadavg','uptime','memory_usage','rootfs_usage','clients','traffic'}
        #Use node object / mac address as default tag
        mac = node
        #Read all keys
        for key in keys:
            try:
                data[key] = jsondata['nodes'][node]['statistics'][key]
            except KeyError:
                pass
        #Create series online
        try:
            pointValues = {}
            pointValues['fields'] = {}
            pointValues['tags'] = {}
            pointValues['time'] = now
            pointValues['measurement'] = 'online'
            pointValues['fields']['value'] = jsondata['nodes'][node]['flags']['online']
            pointValues['tags']['mac'] = mac
            #Append additional tags if existing
            try:
                pointValues['tags']['hostname'] = jsondata['nodes'][node]['nodeinfo']['hostname']
            except:
                pass
            try:
                pointValues['tags']['nodeid'] = jsondata['nodes'][node]['nodeinfo']['node_id']
            except:
                pass
            series.append(pointValues)
        except KeyError:
            pass
        
        #Create series for idletime, loadavg, rootfs_usage and uptime
        for metric in ['loadavg','rootfs_usage','uptime']:
            try:
                pointValues = {}
                pointValues['fields'] = {}
                pointValues['tags'] = {}
                pointValues['time'] = now
                pointValues['measurement'] = metric
                pointValues['fields']['value'] = float(data[metric])
                pointValues['tags']['mac'] = mac
                #Append additional tags if existing
                try:
                    pointValues['tags']['hostname'] = jsondata['nodes'][node]['nodeinfo']['hostname']
                except:
                    pass
                try:
                    pointValues['tags']['nodeid'] = jsondata['nodes'][node]['nodeinfo']['node_id']
                except:
                    pass
                #************************************************************************************
                try:
                    pointValues['tags']['site_code'] = jsondata['nodes'][node]['nodeinfo']['system']['site_code']
                except:
                    pass
                try:
                    pointValues['tags']['batman_compat'] = jsondata['nodes'][node]['nodeinfo']['software']['batman-adv']['compat']
                except:
                    pass
                try:
                    pointValues['tags']['batman_version'] = jsondata['nodes'][node]['nodeinfo']['software']['batman-adv']['version']
                except:
                    pass
                try:
                    pointValues['tags']['autoupdater_enabled'] = jsondata['nodes'][node]['nodeinfo']['software']['autoupdater']['enabled']
                except:
                    pass
                try:
                    pointValues['tags']['autoupdater_branch'] = jsondata['nodes'][node]['nodeinfo']['software']['autoupdater']['branch']
                except:
                    pass
                try:
                    pointValues['tags']['fastd_enableed'] = jsondata['nodes'][node]['nodeinfo']['software']['fastd']['enabled']
                except:
                    pass
                try:
                    pointValues['tags']['fastd_version'] = jsondata['nodes'][node]['nodeinfo']['software']['fastd']['version']
                except:
                    pass
                try:
                    pointValues['tags']['firmware_base'] = jsondata['nodes'][node]['nodeinfo']['software']['firmware']['base']
                except:
                    pass
                try:
                    pointValues['tags']['firmware_release'] = jsondata['nodes'][node]['nodeinfo']['software']['firmware']['release']
                except:
                    pass
                try:
                    pointValues['tags']['hardware_model'] = jsondata['nodes'][node]['nodeinfo']['hardware']['model']
                except:
                    pass
                try:
                    pointValues['tags']['hardware_nproc'] = jsondata['nodes'][node]['nodeinfo']['hardware']['nproc']
                except:
                    pass
                try:
                    pointValues['tags']['owner_contact'] = jsondata['nodes'][node]['nodeinfo']['owner']['contact']
                except:
                    pass
                try:
                    pointValues['tags']['online'] = jsondata['nodes'][node]['flags']['online']
                except:
                    pass
                #*************************************************************************************
                series.append(pointValues)
            except KeyError:
                pass

        #Create series for traffic
        try:
            for type_instance in data['traffic']:
                for type in data['traffic'][type_instance]:
                    pointValues = {}
                    pointValues['fields'] = {}
                    pointValues['tags'] = {}
                    pointValues['time'] = now
                    pointValues['measurement'] = 'traffic'
                    pointValues['fields']['value'] = int(data['traffic'][type_instance][type])
                    pointValues['tags']['type'] = type
                    pointValues['tags']['type_instance'] = type_instance
                    pointValues['tags']['mac'] = mac
                    #Append additional tags if existing
                    try:
                        pointValues['tags']['hostname'] = jsondata['nodes'][node]['nodeinfo']['hostname']
                    except:
                        pass
                    try:
                        pointValues['tags']['nodeid'] = jsondata['nodes'][node]['nodeinfo']['node_id']
                    except:
                        pass
                    #************************************************************************************
                    try:
                        pointValues['tags']['site_code'] = jsondata['nodes'][node]['nodeinfo']['system']['site_code']
                    except:
                        pass
                    try:
                        pointValues['tags']['batman_compat'] = jsondata['nodes'][node]['nodeinfo']['software']['batman-adv']['compat']
                    except:
                        pass
                    try:
                        pointValues['tags']['batman_version'] = jsondata['nodes'][node]['nodeinfo']['software']['batman-adv']['version']
                    except:
                        pass
                    try:
                        pointValues['tags']['autoupdater_enabled'] = jsondata['nodes'][node]['nodeinfo']['software']['autoupdater']['enabled']
                    except:
                        pass
                    try:
                        pointValues['tags']['autoupdater_branch'] = jsondata['nodes'][node]['nodeinfo']['software']['autoupdater']['branch']
                    except:
                        pass
                    try:
                        pointValues['tags']['fastd_enableed'] = jsondata['nodes'][node]['nodeinfo']['software']['fastd']['enabled']
                    except:
                        pass
                    try:
                        pointValues['tags']['fastd_version'] = jsondata['nodes'][node]['nodeinfo']['software']['fastd']['version']
                    except:
                        pass
                    try:
                        pointValues['tags']['firmware_base'] = jsondata['nodes'][node]['nodeinfo']['software']['firmware']['base']
                    except:
                        pass
                    try:
                        pointValues['tags']['firmware_release'] = jsondata['nodes'][node]['nodeinfo']['software']['firmware']['release']
                    except:
                        pass
                    try:
                        pointValues['tags']['hardware_model'] = jsondata['nodes'][node]['nodeinfo']['hardware']['model']
                    except:
                        pass
                    try:
                        pointValues['tags']['hardware_nproc'] = jsondata['nodes'][node]['nodeinfo']['hardware']['nproc']
                    except:
                        pass
                    try:
                        pointValues['tags']['owner_contact'] = jsondata['nodes'][node]['nodeinfo']['owner']['contact']
                    except:
                        pass
                    try:
                        pointValues['tags']['online'] = jsondata['nodes'][node]['flags']['online']
                    except:
                        pass
                    #*************************************************************************************
                    series.append(pointValues)
        except KeyError:
            pass
    return series

def parse_args():
    parser = argparse.ArgumentParser(
        description='export alfred data to influxdb')
    parser.add_argument('--hostname', type=str, required=False, default='localhost',
                        help='hostname of influxdb http API')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of influxdb http API')
    parser.add_argument('--username', type=str, required=False, default='user',
                        help='username of influxdb http API')
    parser.add_argument('--password', type=str, required=False, default='pass',
                        help='password of influxdb http API')
    parser.add_argument('--database', type=str, required=False, default='freifunk',
                        help='influxdb database to write to')
    parser.add_argument('--file', type=str, required=False, default='',
                        help='alfred data file to read')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(hostname=args.hostname, port=args.port, file=args.file, username=args.username, password=args.password, database=args.database)
