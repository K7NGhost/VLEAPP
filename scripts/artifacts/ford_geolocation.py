__artifacts_v2__ = {
    "geolocation_data": {
        "name": "Geolocation data",
        "description": "Scrapes the geolocation data from ford vehicles",
        "author": "@K7NGhost",
        "version": "0.1", 
        "date": "2024-6-16", 
        "requirements": "none",
        "category": "Ford Vehicles",
        "notes": "",
        "paths": ('*/*fdplog.np.txt*', '*/deleted_*'),
        "function": "get_geolocation_data"
    }
}

import datetime
import os
import re
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, logdevinfo, is_platform_windows

def get_geolocation_data(files_found, report_folder, seeker, wrap_text, time_offset):
        # 1st method variables
        timestamp_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)')
        coord_pattern = re.compile(r"lat=([-\d.]+),\s*lon=([-\d.]+),\s*alt=([-\d.]+)")
        trimble_output = []
        trimble_file_paths = []
        
        # 2nd method variables
        pattern = r'"altitude"\s*:\s*(-?[\d.]+)\s*,\s*"heading_angle"\s*:\s*(-?[\d.]+)\s*,\s*"lat"\s*:\s*(-?[\d.]+)\s*,\s*"lon"\s*:\s*(-?[\d.]+)\s*,\s*"speed"\s*:\s*(-?[\d.]+)\s*,\s*"timestamp"\s*:\s*(-?[\d.]+)'
        geolocation_data = []
        geolocation_file_paths = []
        
        # 3rd method variables
        points = []
        points_file_paths = []
        
        for file_path in files_found:
            try:
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                        for line in file:
                            # 1st method
                            try:
                                if "Trimble Output" in line:
                                    timestamp_match = timestamp_pattern.search(line)
                                    match = coord_pattern.search(line)
                                    if match and timestamp_match:
                                        timestamp = timestamp_match.group(1)
                                        dt = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                                        lat, lon, alt = map(float, match.groups())
                                        trimble_output.append((dt, lat, lon, alt))
                                        trimble_file_paths.append(file_path)
                            except Exception as e:
                                print(e)
                            
                            # 2nd Method
                            try:
                                matches = re.findall(pattern, line)
                                if matches:
                                    for altitude, heading_angle, lat, lon, speed, timestamp in matches:
                                        #print(float(altitude), float(heading_angle), float(lat), float(lon), float(speed), float(timestamp))
                                        geolocation_data.append((altitude, heading_angle, lat, lon, speed, timestamp))
                                        geolocation_file_paths.append(file_path)
                            except Exception as e:
                                print(e)
                    # 3rd Method
                    with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                        text = file.read()
                        point_pattern = r'points\s*{\s*lat:\s*(-?[\d.]+)\s*lon:\s*(-?[\d.]+)'

                        point_matches = re.findall(point_pattern, text, re.DOTALL)
                        if point_matches: 
                            for lat, lon in point_matches:
                                points.append((lat, lon))
                            points_file_paths.append(file_path)
                            

                            
            except Exception as e:
                print(e)

        if len(trimble_output) > 0:
            report = ArtifactHtmlReport('Geolocation Data')
            report.start_artifact_report(report_folder, 'geolocation data')
            report.add_script()
            data_headers = ("Timestamp", "Latitude", "Longitude", "Altitude")
            report.write_artifact_data_table(data_headers, trimble_output, trimble_file_paths)
            report.end_artifact_report()
            tsvname = f'geolocation data'
            tsv(report_folder, data_headers, trimble_output, tsvname)
        else:
            logfunc(f'no geolocation found')
        
        if len(geolocation_data) > 0:
            report = ArtifactHtmlReport('Deleted Geolocation Data')
            report.start_artifact_report(report_folder, 'deleted geolocation data')
            report.add_script()
            data_headers = ("Altitude", "Heading_Angle", "Latitude", "Longitude", "Speed", "Timestamp")
            report.write_artifact_data_table(data_headers, geolocation_data, geolocation_file_paths)
            report.end_artifact_report()
            tsvname = f'deleted geolocation data'
            tsv(report_folder, data_headers, geolocation_data, tsvname)
        else:
            logfunc(f'no deleted geolocation found')
            
        if len(points) > 0:
            report = ArtifactHtmlReport('Geolocation Point Data')
            report.start_artifact_report(report_folder, 'geolocation point data')
            report.add_script()
            data_headers = ("Latitude", "Longitude")
            report.write_artifact_data_table(data_headers, points, points_file_paths)
            report.end_artifact_report()
            tsvname = f'geolocation point data'
            tsv(report_folder, data_headers, points, tsvname)
        else:
            logfunc(f'no geolocation point found')
            
            
                            