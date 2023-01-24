from prometheus_api_client import PrometheusConnect,MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.filters.hp_filter import hpfilter
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import acf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from kafka import KafkaProducer
import json

def elaboraMetrica(nome_metrica,metrica,partizione,producer):
    isStationary=False
    critValues=[]
    metrics_data={}
    cyclical_component={}
    seasonal_component={}
    trend_component={}

    #Augmented dickey fuller test per valutare la staticità
    result_adf = adfuller(metrica,maxlag=3)
    out = pd.Series(result_adf[0:4],index=['ADF test statistic','p-value','# lags used','# observations'])
    if result_adf[1] <0.05:
        isStationary=True

    for key,val in result_adf[4].items():
        critValues.append(val)

    #filtro hodrick-prescott per prendere informazioni sulla ciclicità
    cyclical, trend = hpfilter(metrica, lamb=1600)
    cyclical.keys=cyclical.keys().strftime('%Y-%m-%d %H:%M:%S')

    #Autocorrelazione
    result_acf= acf(metrica)
    np.nan_to_num(result_acf,copy=False)

    #seasonal decompose per prendere info su trend e stagionalità
    result_decompose = seasonal_decompose(metrica,model='additive', period=320)
    np.nan_to_num(result_decompose.trend.values,copy=False)
    result_decompose.seasonal.keys=result_decompose.seasonal.keys().strftime('%Y-%m-%d %H:%M:%S')
    result_decompose.trend.keys=result_decompose.trend.keys().strftime('%Y-%m-%d %H:%M:%S')
    sampled_metrica = metrica.resample('5T').mean()
    sampled_metrica = sampled_metrica.reset_index()
    sampled_metrica = sampled_metrica.applymap(str)
    sampled_metrica_dict = sampled_metrica.to_dict(orient='index')
    metrics_data={}
    for i in range (289):
        metrics_data[sampled_metrica_dict[i]['timestamp']]=sampled_metrica_dict[i]['value']
    

    for i in range (1440):
        seasonal_component[result_decompose.seasonal.keys[i]]=result_decompose.seasonal.values[i]
        trend_component[result_decompose.trend.keys[i]]=result_decompose.trend.values[i]
        cyclical_component[cyclical.keys[i]]=cyclical.values[i]
    
    #valutazione metriche nelle ultime 1,3,12h
    hourly_data = metrica.resample('1H').last().agg(['max', 'min', 'mean','std']).to_dict()
    three_hourly_data = metrica.resample('3H').last().agg(['max', 'min', 'mean','std']).to_dict()
    twelve_hourly_data = metrica.resample('12H').last().agg(['max', 'min', 'mean','std']).to_dict()

    tsr = trend.resample(rule='1T').mean()
    
    #predizione delle metriche per i prox 10 min
    tsmodel = ExponentialSmoothing(tsr, trend='mul', seasonal='add',seasonal_periods=550).fit()
    prediction = tsmodel.forecast(10)
    predicted_metrics=prediction.agg(['max','min','mean']).to_dict()
    
    #invio dati al broker kafka
    total_data={'metric_name':nome_metrica,partizione:{'values':metrics_data,'adfuller_statistic':result_adf[0],'adfuller_p_val':result_adf[1],
                    'adfuller_stationary':isStationary,'adfuller_critical':critValues,'acf':result_acf.tolist(),
                    'decompose_season':seasonal_component,'decompose_trend':trend_component,'cyclical_component':cyclical_component,
                    'hourly_data':hourly_data,'three_hourly_data':three_hourly_data,'twelve_hourly_data':twelve_hourly_data,
                    '10m_prediction':predicted_metrics}}

    producer.send("prometheusdata",total_data)
    producer.flush()

# Create a PrometheusClient to retrieve data from the server
client = PrometheusConnect(url='http://15.160.61.227:29090',disable_ssl=True)
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],value_serializer=lambda v: json.dumps(v).encode('utf-8'),api_version=(0,10,2))

label_config = {'job': 'host','mode':'user'}
start_time = parse_datetime("1d")
end_time = parse_datetime("now")

#Metrica1 utilizzo cpu in user mode
metric_data = client.get_metric_range_data(
    metric_name='node_cpu_seconds_total',
    label_config=label_config,
    start_time=start_time,
    end_time=end_time,
)

metric_df = MetricRangeDataFrame(metric_data)

#separo i subset relativi ad ogni core della cpu
subset1 = metric_df.loc[metric_df['cpu']=='0', ['value']]
subset2 = metric_df.loc[metric_df['cpu']=='1', ['value']]
subset3 = metric_df.loc[metric_df['cpu']=='2', ['value']]
subset4 = metric_df.loc[metric_df['cpu']=='3', ['value']]
subset5 = metric_df.loc[metric_df['cpu']=='4', ['value']]
subset6 = metric_df.loc[metric_df['cpu']=='5', ['value']]
subset7 = metric_df.loc[metric_df['cpu']=='6', ['value']]
subset8 = metric_df.loc[metric_df['cpu']=='7', ['value']]
subsets=[subset1,subset2,subset3,subset4,subset5,subset6,subset7,subset8]

# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
# Seasonal decomposition per prendere info su trend,stagionalità e residuo
# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
# ACF

cyclicals=[]
trends=[]
seasonalResults=[]
hourlyDatas = []
threeHourlyDatas=[]
twelveHourlyDatas=[]
acf_Cpu=[]

for sub in subsets:
    cyclical,trend=hpfilter(sub, lamb=1600)
    cyclicals.append(cyclical)
    trends.append(trend)
    acf_Core=acf(sub)
    acf_Cpu.append(acf_Core)
    result = seasonal_decompose(sub,model='additive', period=320)
    seasonalResults.append(result)
    hourly_data = sub.resample('1H').last().agg(['max', 'min', 'mean','std']).to_dict()
    three_hourly_data = sub.resample('3H').last().agg(['max', 'min', 'mean','std']).to_dict()
    twelve_hourly_data = sub.resample('12H').last().agg(['max', 'min', 'mean','std']).to_dict()
    hourlyDatas.append(hourly_data)
    threeHourlyDatas.append(three_hourly_data)
    twelveHourlyDatas.append(twelve_hourly_data)

#Metrica2: Byte di Memoria Liberi (non include cache e buffer)
label_config = {'job': 'host'}
metric_data = client.get_metric_range_data(
    metric_name='node_memory_MemFree_bytes',
    label_config=label_config,
    start_time=start_time,
    end_time=end_time,
)

metric_df = MetricRangeDataFrame(metric_data)
memFreeData = metric_df.loc[:, ['value']]

elaboraMetrica("memory_memFree_bytes",memFreeData,"default",producer)

#Metrica3: Memoria disponibile (include memoria cache e buffers)
label_config = {'job': 'host'}
metric_data = client.get_metric_range_data(
    metric_name='node_memory_MemAvailable_bytes',
    label_config=label_config,
    start_time=start_time,
    end_time=end_time,
)

metric_df = MetricRangeDataFrame(metric_data)
memAvailData = metric_df.loc[:, ['value']]

elaboraMetrica("memory_memAvail_bytes",memAvailData,"default",producer)

#Metrica4: Spazio libero su disco (non include memorie cache e buffers)
label_config = {'job': 'host'}
metric_data = client.get_metric_range_data(
    metric_name='node_filesystem_free_bytes',
    label_config=label_config,
    start_time=start_time,
    end_time=end_time,
)

metric_df = MetricRangeDataFrame(metric_data)

#separo i dati relativi ai 2 dischi
diskFreeData1= metric_df.loc[metric_df['device']=='/dev/sda2', ['value']]
diskFreeData2= metric_df.loc[metric_df['device']=='tmpfs', ['value']]
elaboraMetrica("filesystem_free_bytes",diskFreeData1,"/dev/sda2",producer)
elaboraMetrica("filesystem_free_bytes",diskFreeData2,"tmpfs",producer)


#Metrica5: Spazio libero su disco (include memorie cache e buffers)
label_config = {'job': 'host'}
metric_data = client.get_metric_range_data(
    metric_name='node_filesystem_avail_bytes',
    label_config=label_config,
    start_time=start_time,
    end_time=end_time,
)

metric_df = MetricRangeDataFrame(metric_data)
#separo i dati relativi ai 2 dischi
diskAvailData1= metric_df.loc[metric_df['device']=='/dev/sda2', ['value']]
diskAvailData2= metric_df.loc[metric_df['device']=='tmpfs', ['value']]
elaboraMetrica("filesystem_avail_bytes",diskAvailData1,"/dev/sda2",producer)
elaboraMetrica("filesystem_avail_bytes",diskAvailData2,"tmpfs",producer)

#Metrica6 Dati ricevuti dalla scheda di rete 
label_config = {'job': 'host','device':'eth0'}
metric_data = client.get_metric_range_data(
    metric_name='node_network_receive_bytes_total',
    label_config=label_config,
    start_time=start_time,
    end_time=end_time,
)

metric_df = MetricRangeDataFrame(metric_data)
recBytesData = metric_df.loc[:, ['value']]

#Augmented Dickey-Fuller Test per info sulla stazionarietà della metrica
result = adfuller(recBytesData)
out = pd.Series(result[0:4],index=['ADF test statistic','p-value','# lags used','# observations'])

for key,val in result[4].items():
    out[f'critical value ({key})']=val

# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
recBytes_cyclical, recBytes_trend = hpfilter(recBytesData, lamb=1600)
#ACF
acf_RecBytes = acf(recBytesData)
# Seasonal decomposition per prendere info su trend,stagionalità e residuo
recBytesResult = seasonal_decompose(recBytesData,model='additive', period=320)

# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
recBytes_hourly_data = recBytesData.resample('1H').last().agg(['max', 'min', 'mean','std'])
recBytes_three_hourly_data = recBytesData.resample('3H').last().agg(['max', 'min', 'mean','std'])
recBytes_twelve_hourly_data =recBytesData.resample('12H').last().agg(['max', 'min', 'mean','std'])

#Metrica7 numero filedescriptors allocati node_filefd_allocated
label_config = {'job': 'host'}
metric_data = client.get_metric_range_data(
    metric_name='node_filefd_allocated',
    label_config=label_config,
    start_time=start_time,
    end_time=end_time,
)

metric_df = MetricRangeDataFrame(metric_data)
fdAlloData = metric_df.loc[:, ['value']]
elaboraMetrica("filefd_allocated",fdAlloData,"default",producer)
