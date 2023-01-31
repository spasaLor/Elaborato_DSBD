import sys
from prometheus_api_client import PrometheusConnect,MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime
import json


client = PrometheusConnect(url='http://15.160.61.227:29090',disable_ssl=True)
label_config = {'job': 'host'}
start_time = parse_datetime(sys.argv[4])
#start_time = parse_datetime("1h")
end_time = parse_datetime("now")
metric_data = client.get_metric_range_data(
    metric_name=sys.argv[1],
    #metric_name="node_memory_MemAvailable_bytes",
    label_config=label_config,
    start_time=start_time,
    end_time=end_time,
)
metric_df = MetricRangeDataFrame(metric_data)
if sys.argv[1] == 'node_filesystem_avail_bytes' or sys.argv[1] == 'node_filesystem_free_bytes':
    data = metric_df.loc[metric_df['device']=='/dev/sda2', ['value']]
else:
    data = metric_df.loc[:, ['value']]
    
sampled_metrica = data.resample('T').mean()
sampled_metrica = sampled_metrica.reset_index()
sampled_metrica = sampled_metrica.applymap(str)
sampled_metrica_dict = sampled_metrica.to_dict(orient='index')
max_value=float(sys.argv[2])
min_value=float(sys.argv[3])
interval=int(sys.argv[5])
#max_value=32000000000
#min_value=21840000000
for i in range (interval):
#for i in range (60):
    current_value = float(sampled_metrica_dict[i]['value'])
    if current_value < max_value and current_value > min_value:
        del sampled_metrica_dict[i]

json_object = json.dumps(sampled_metrica_dict) 
print(json_object)