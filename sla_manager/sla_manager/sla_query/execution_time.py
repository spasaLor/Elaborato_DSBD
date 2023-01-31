import sys
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter('ignore', ConvergenceWarning)
import time


client = PrometheusConnect(url='http://15.160.61.227:29090',disable_ssl=True)
label_config = {'job': 'host'}
start_time = parse_datetime(sys.argv[2])
#start_time = parse_datetime("12h")
end_time = parse_datetime("now")
start = time.time()
metric_data = client.get_metric_range_data(
    metric_name=sys.argv[1],
    #metric_name="node_memory_MemAvailable_bytes",
    label_config=label_config,
    start_time=start_time,
    end_time=end_time,
)
end = time.time()
print(end - start)