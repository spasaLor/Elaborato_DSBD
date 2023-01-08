from prometheus_api_client import PrometheusConnect,MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.filters.hp_filter import hpfilter
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import acf
import pandas as pd
import matplotlib.pyplot as plt
from kafka import KafkaProducer
import json

# Create a PrometheusClient to retrieve data from the server
client = PrometheusConnect(url='http://15.160.61.227:29090',disable_ssl=True)
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],value_serializer=lambda v: json.dumps(v).encode('utf-8'))

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

# Perform the Dickey-Fuller test
memFree_adf = adfuller(memFreeData,maxlag=3)
out = pd.Series(memFree_adf[0:4],index=['ADF test statistic','p-value','# lags used','# observations'])

for key,val in memFree_adf[4].items():
    out[f'critical value ({key})']=val

# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
memFree_cyclical, memFree_trend = hpfilter(memFreeData, lamb=1600)

#ACF
acf_MemAvail = acf(memFreeData)

# Seasonal decomposition per prendere info su trend,stagionalità e residuo
memFreeResult = seasonal_decompose(memFreeData,model='additive', period=320)

# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
memFree_hourly_data = memFreeData.resample('1H').last().agg(['max', 'min', 'mean','std']).to_dict()
memFree_three_hourly_data = memFreeData.resample('3H').last().agg(['max', 'min', 'mean','std']).to_dict()
memFree_twelve_hourly_data =memFreeData.resample('12H').last().agg(['max', 'min', 'mean','std']).to_dict()

# Predizione dei valori max,min,media nei prox 10 minuti
tsr = memFreeData.resample(rule='1T').mean()

tsmodel = ExponentialSmoothing(tsr, trend='mul', seasonal='add',seasonal_periods=550).fit()
prediction = tsmodel.forecast(10)
memFreePred=prediction.agg(['max','min','mean']).to_dict()

memFree_totalData={'metric_name':"memory_memFree_bytes",'default':{'adfuller':memFree_adf[1],'hourly_data':memFree_hourly_data,'three_hourly_data':memFree_three_hourly_data,
                    'twelve_hourly_data':memFree_twelve_hourly_data,'10m_prediction':memFreePred}}

producer.send('prometheusdata', memFree_totalData)

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

#Augmented Dickey-Fuller Test per info sulla stazionarietà della metrica
memAvail_adf = adfuller(memAvailData,maxlag=3)
out = pd.Series(memAvail_adf[0:4],index=['ADF test statistic','p-value','# lags used','# observations'])

for key,val in memAvail_adf[4].items():
    out[f'critical value ({key})']=val

# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
memAvail_cyclical, memAvail_trend = hpfilter(memAvailData, lamb=1600)

#ACF
acf_MemAvail = acf(memAvailData)

# Seasonal decomposition per prendere info su trend,stagionalità e residuo
memAvailResult = seasonal_decompose(memAvailData,model='additive', period=320)

# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
memAvail_hourly_data = memAvailData.resample('1H').last().agg(['max', 'min', 'mean','std']).to_dict()
memAvail_three_hourly_data = memAvailData.resample('3H').last().agg(['max', 'min', 'mean','std']).to_dict()
memAvail_twelve_hourly_data = memAvailData.resample('12H').last().agg(['max', 'min', 'mean','std']).to_dict()

# Predizione dei valori max,min,media nei prox 10 minuti
tsr = memAvail_trend.resample(rule='1T').mean()
tsmodel = ExponentialSmoothing(tsr, trend='mul', seasonal='mul',seasonal_periods=650).fit()
prediction = tsmodel.forecast(steps=10)
memAvailPred=prediction.agg(['max','min','mean']).to_dict()

memAvail_totalData={'metric_name':"memory_memAvail_bytes",'default':{'adfuller':memAvail_adf[1],'hourly_data':memAvail_hourly_data,'three_hourly_data':memAvail_three_hourly_data,
                    'twelve_hourly_data':memAvail_twelve_hourly_data,'10m_prediction':memAvailPred}}
producer.send('prometheusdata',memAvail_totalData)

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
df_DiskFree=[]
diskFreeData1= metric_df.loc[metric_df['device']=='/dev/sda2', ['value']]
diskFreeData2= metric_df.loc[metric_df['device']=='tmpfs', ['value']]
df_DiskFree.append(diskFreeData1)
df_DiskFree.append(diskFreeData2)

#Augmented Dickey-Fuller Test per info sulla stazionarietà della metrica
dFul_results=[]
result = adfuller(diskFreeData1)
dFul_results.append(result)
res=adfuller(diskFreeData2)
dFul_results.append(res)

for r in dFul_results:
    out = pd.Series(r[0:4],index=['ADF test statistic','p-value','# lags used','# observations'])

    for key,val in r[4].items():
        out[f'critical value ({key})']=val
# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
disk_cyclical1, disk_trend1 = hpfilter(diskFreeData1, lamb=1600)
disk_cyclical2, disk_trend2 = hpfilter(diskFreeData2, lamb=1600)

#ACF
acf_DiskFree=[]
for d in df_DiskFree:
    acf_values = acf(d)
    acf_DiskFree.append(acf_values)

# Seasonal decomposition per prendere info su trend,stagionalità e residuo
disk_result1 = seasonal_decompose(diskFreeData1,model='additive', period=320)
disk_result2 = seasonal_decompose(diskFreeData2,model='additive', period=320)

# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
hour_DiskFree=[]
three_hours_DiskFree=[]
twelve_hours_DiskFree=[]

for f in df_DiskFree:
    hourly_data = f.resample('1H').last().agg(['max', 'min', 'mean','std']).to_dict()
    three_hourly_data = f.resample('3H').last().agg(['max', 'min', 'mean','std']).to_dict()
    twelve_hourly_data = f.resample('12H').last().agg(['max', 'min', 'mean','std']).to_dict()
    hour_DiskFree.append(hourly_data)
    three_hours_DiskFree.append(three_hourly_data)
    twelve_hours_DiskFree.append(twelve_hourly_data)


# Predizione dei valori max,min,media nei prox 10 minuti
pred_DiskFree=[]
for d in df_DiskFree:
    tsr = d.resample(rule='1T').mean()
    tsmodel = ExponentialSmoothing(tsr, trend='add', seasonal='mul',seasonal_periods=450).fit()
    prediction = tsmodel.forecast(steps=10)
    pred_DiskFree.append(prediction.agg(['max','min','mean']).to_dict())

diskFree_totalData={'metric_name':"filesystem_free_bytes",'disk1':{'adfuller':dFul_results[0][1],'hourly_data':hour_DiskFree[0],
                    'three_hourly_data':three_hours_DiskFree[0],'twelve_hourly_data':twelve_hours_DiskFree[0],
                    '10m_prediction':pred_DiskFree[0]},
                    'disk2':{'adfuller':dFul_results[1][1],'hourly_data':hour_DiskFree[1],'three_hourly_data':three_hours_DiskFree[1],
                    'twelve_hourly_data':twelve_hours_DiskFree[1],'10m_prediction':pred_DiskFree[1]}}
producer.send('prometheusdata',diskFree_totalData)

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
df_DiskAvail=[]
diskAvailData1= metric_df.loc[metric_df['device']=='/dev/sda2', ['value']]
diskAvailData2= metric_df.loc[metric_df['device']=='tmpfs', ['value']]
df_DiskAvail.append(diskAvailData1)
df_DiskAvail.append(diskAvailData2)

#Augmented Dickey-Fuller Test per info sulla stazionarietà della metrica
results_diskAvail=[]
result = adfuller(diskAvailData1)
results_diskAvail.append(result)
res=adfuller(diskAvailData2)
results_diskAvail.append(res)

for r in results_diskAvail:
    out = pd.Series(r[0:4],index=['ADF test statistic','p-value','# lags used','# observations'])

    for key,val in r[4].items():
        out[f'critical value ({key})']=val

# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
diskAv_cyclical1, diskAv_trend1 = hpfilter(diskAvailData1, lamb=1600)
diskAv_cyclical2, diskAv_trend2 = hpfilter(diskAvailData2, lamb=1600)

#ACF
acf_DiskAvail=[]
for d in df_DiskAvail:
    acf_values = acf(d)
    acf_DiskAvail.append(acf_values)

# Seasonal decomposition per prendere info su trend,stagionalità e residuo
diskAv_result1 = seasonal_decompose(diskAvailData1,model='additive', period=320)
diskAv_result2 = seasonal_decompose(diskAvailData2,model='additive', period=320)

# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
hour_DiskAvail=[]
three_hours_DiskAvail=[]
twelve_hours_DiskAvail=[]

for f in df_DiskAvail:
    hourly_data = f.resample('1H').last().agg(['max', 'min', 'mean','std']).to_dict()
    three_hourly_data = f.resample('3H').last().agg(['max', 'min', 'mean','std']).to_dict()
    twelve_hourly_data = f.resample('12H').last().agg(['max', 'min', 'mean','std']).to_dict()
    hour_DiskAvail.append(hourly_data)
    three_hours_DiskAvail.append(three_hourly_data)
    twelve_hours_DiskAvail.append(twelve_hourly_data)

# Predizione dei valori max,min,media nei prox 10 minuti
pred_DiskAvail=[]
for d in df_DiskAvail:
    tsr = d.resample(rule='1T').mean()
    tsmodel = ExponentialSmoothing(tsr, trend='add', seasonal='mul',seasonal_periods=450).fit()
    prediction = tsmodel.forecast(steps=10)

    plt.ylabel('Values', fontsize=14)
    plt.xlabel('Time', fontsize=14)
    plt.title('Values over time', fontsize=16)
    plt.plot(tsr, "-", label = 'real')
    plt.plot(prediction,"--", label = 'pred')
    plt.legend()
    pred_DiskAvail.append(prediction.agg(['max','min','mean']).to_dict())

totalDataCollected={'metric_name':"filesystem_avail_bytes",'disk1':{'adfuller':results_diskAvail[0][1],'hourly_data':hour_DiskAvail[0],
                    'three_hourly_data':three_hours_DiskAvail[0],'twelve_hourly_data':twelve_hours_DiskAvail[0],
                    '10m_prediction':pred_DiskAvail[0]},
                    'disk2':{'adfuller':results_diskAvail[1][1],'hourly_data':hour_DiskAvail[1],'three_hourly_data':three_hours_DiskAvail[1],
                    'twelve_hourly_data':twelve_hours_DiskAvail[1],'10m_prediction':pred_DiskAvail[1]}}
producer.send('prometheusdata', totalDataCollected)

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

#Augmented Dickey-Fuller Test per info sulla stazionarietà della metrica
fdAllo_adf = adfuller(fdAlloData)
out = pd.Series(fdAllo_adf[0:4],index=['ADF test statistic','p-value','# lags used','# observations'])

for key,val in fdAllo_adf[4].items():
    out[f'critical value ({key})']=val

# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
fdAllo_cyclical, fdAllo_trend = hpfilter(fdAlloData, lamb=1600)
#ACF
acf_fdAllo = acf(fdAlloData)
# Seasonal decomposition per prendere info su trend,stagionalità e residuo
fdAlloResult = seasonal_decompose(fdAlloData,model='additive', period=320)

# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
fdAllo_hourly_data = fdAlloData.resample('1H').last().agg(['max', 'min', 'mean','std']).to_dict()
fdAllo_three_hourly_data = fdAlloData.resample('3H').last().agg(['max', 'min', 'mean','std']).to_dict()
fdAllo_twelve_hourly_data = fdAlloData.resample('12H').last().agg(['max', 'min', 'mean','std']).to_dict()

# Predizione dei valori max,min,media nei prox 10 minuti
tsr = fdAllo_trend.resample(rule='1T').mean()
tsmodel = ExponentialSmoothing(tsr, trend='add', seasonal='add',seasonal_periods=450).fit()
prediction = tsmodel.forecast(steps=10)
fdAlloPred=prediction.agg(['max','min','mean']).to_dict()

fdAllo_totalData={'metric_name':"filefd_allocated",'default':{'adfuller':fdAllo_adf[1],'hourly_data':fdAllo_hourly_data,'three_hourly_data':fdAllo_three_hourly_data,
                    'twelve_hourly_data':fdAllo_twelve_hourly_data,'10m_prediction':fdAlloPred}}
producer.send('prometheusdata',memAvail_totalData)
producer.flush()