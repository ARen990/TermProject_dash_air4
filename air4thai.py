import requests
from pprint import pformat

station_id = "44t"
param = "PM25,PM10,O3,CO,NO2,SO2,WS,TEMP,RH,WD"
data_type = "hr"
start_date = "2023-09-20"
end_date = "2024-02-20"
start_time = "00"
end_time = "23"
#http://air4thai.com/forweb/getHistoryData.php?stationID=44t&param=PM25,PM10,O3,CO,NO2,SO2,WS,TEMP,RH,WD&type=hr&sdate=2024-02-19&edate=2024-02-20&stime=00&etime=23
url = f"http://air4thai.com/forweb/getHistoryData.php?stationID={station_id}&param={param}&type={data_type}&sdate={start_date}&edate={end_date}&stime={start_time}&etime={end_time}"
response = requests.get(url)
response_json = response.json()
# print(pformat(response_json))

import pandas as pd

pd_from_dict = pd.DataFrame.from_dict(response_json["stations"][0]["data"])
print(pformat(pd_from_dict))
pd_from_dict.to_csv(f"air4thai_data.csv")

#pd_from_dict.to_csv(f"air4thai_{station_id}_{start_date}_{end_date}.csv")
