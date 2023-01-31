import sys
from prometheus_api_client import PrometheusConnect, MetricSnapshotDataFrame,MetricRangeDataFrame, Metric, MetricsList
from prometheus_api_client.utils import parse_datetime

    
client = PrometheusConnect(url='http://15.160.61.227:29090',disable_ssl=True)
label_config = {'job': 'host'}
metric_data = client.get_current_metric_value(
    metric_name=sys.argv[1],
    label_config=label_config,
)
metric_df  =  MetricSnapshotDataFrame ( metric_data )
metric_df.head()
value = metric_df.iloc[0]['value']
print(value)
