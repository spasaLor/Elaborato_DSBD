import sys
from prometheus_api_client import PrometheusConnect,MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.filters.hp_filter import hpfilter
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import acf
import numpy as np
import json
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter('ignore', ConvergenceWarning)


client = PrometheusConnect(url='http://15.160.61.227:29090',disable_ssl=True)
label_config = {'job': 'host'}
start_time = parse_datetime(sys.argv[4])
#start_time = parse_datetime("1d")
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

isStationary=False
critValues=[]
metrics_data={}
cyclical_component={}
seasonal_component={}
trend_component={}

#Augmented dickey fuller test per valutare la staticità
result_adf = adfuller(data,maxlag=3)
out = pd.Series(result_adf[0:4],index=['ADF test statistic','p-value','# lags used','# observations'])
if result_adf[1] <0.05:
    isStationary=True

for key,val in result_adf[4].items():
    critValues.append(val)

#filtro hodrick-prescott per prendere informazioni sulla ciclicità
cyclical, trend = hpfilter(data, lamb=1600)
cyclical.keys=cyclical.keys().strftime('%Y-%m-%d %H:%M:%S')

#Autocorrelazione
result_acf= acf(data)
np.nan_to_num(result_acf,copy=False)

#seasonal decompose per prendere info su trend e stagionalità
result_decompose = seasonal_decompose(data,model='additive', period=320)
np.nan_to_num(result_decompose.trend.values,copy=False)
result_decompose.seasonal.keys=result_decompose.seasonal.keys().strftime('%Y-%m-%d %H:%M:%S')
result_decompose.trend.keys=result_decompose.trend.keys().strftime('%Y-%m-%d %H:%M:%S')
campioni = int(sys.argv[5])
#for i in range (1440):
for i in range (campioni):
    seasonal_component[result_decompose.seasonal.keys[i]]=result_decompose.seasonal.values[i]
    trend_component[result_decompose.trend.keys[i]]=result_decompose.trend.values[i]
    cyclical_component[cyclical.keys[i]]=cyclical.values[i]

tsr = trend.resample(rule='1T').mean()

#predizione delle metriche per i prox 10 min
tsmodel = ExponentialSmoothing(tsr, trend='mul', seasonal='add',seasonal_periods=550).fit()
minuti_previsione = int(sys.argv[6])
prediction = tsmodel.forecast(minuti_previsione)
#prediction = tsmodel.forecast(10)

sampled_metrica = prediction.resample('T').mean()
sampled_metrica = sampled_metrica.reset_index()
sampled_metrica = sampled_metrica.applymap(str)
sampled_metrica_dict = sampled_metrica.to_dict(orient='index')

max_value=float(sys.argv[2])
min_value=float(sys.argv[3])
#max_value=32000000000
#min_value=22764000000
for i in range (minuti_previsione):
#for i in range (10):
    current_value = float(sampled_metrica_dict[i][0])
    if current_value < max_value and current_value > min_value:
        del sampled_metrica_dict[i]
json_object = json.dumps(sampled_metrica_dict) 
print(json_object)
