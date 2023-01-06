from prometheus_api_client import PrometheusConnect,MetricsList,MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.filters.hp_filter import hpfilter
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.ar_model import AutoReg,ARResults
import pandas as pd
import matplotlib.pyplot as plt

# Create a PrometheusClient to retrieve data from the server
client = PrometheusConnect(url='http://15.160.61.227:29090',disable_ssl=True)

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
# Seasonal decomposition per prendere info su trand,stagionalità e residuo
# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore

cyclicals=[]
trends=[]
seasonalResults=[]
hourlyDatas = []
threeHourlyDatas=[]
twelveHourlyDatas=[]

for sub in subsets:
    cyclical,trend=hpfilter(sub, lamb=1600)
    cyclicals.append(cyclical)
    trends.append(trend)
    result = seasonal_decompose(sub,model='additive', period=320)
    seasonalResults.append(result)
    hourly_data = sub.resample('1H').last().agg(['max', 'min', 'mean','std'])
    three_hourly_data = sub.resample('3H').last().agg(['max', 'min', 'mean','std'])
    twelve_hourly_data = sub.resample('12H').last().agg(['max', 'min', 'mean','std'])
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
result = adfuller(memFreeData,maxlag=3)
out = pd.Series(result[0:4],index=['ADF test statistic','p-value','# lags used','# observations'])

for key,val in result[4].items():
    out[f'critical value ({key})']=val
print(out)

# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
memFree_cyclical, memFree_trend = hpfilter(memFreeData, lamb=1600)

# Seasonal decomposition per prendere info su trand,stagionalità e residuo
memFreeResult = seasonal_decompose(memFreeData,model='additive', period=320)

# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
mem_hourly_data = memFreeData.resample('1H').last().agg(['max', 'min', 'mean','std'])
mem_three_hourly_data = memFreeData.resample('3H').last().agg(['max', 'min', 'mean','std'])
mem_twelve_hourly_data =memFreeData.resample('12H').last().agg(['max', 'min', 'mean','std'])

# Predizione dei valori max,min,media nei prox 10 minuti
tsr = memFreeData.resample(rule='1T').mean()
tsmodel = ExponentialSmoothing(tsr, trend='mul', seasonal='add',seasonal_periods=550).fit()
prediction = tsmodel.forecast(10)
memFreePred=prediction.agg(['max','min','mean'])

plt.ylabel('Values', fontsize=14)
plt.xlabel('Time', fontsize=14)
plt.title('Values over time', fontsize=16)
plt.plot(tsr, "-", label = 'real')
plt.plot(prediction,"--", label = 'pred')
plt.legend()



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
result = adfuller(memAvailData,maxlag=3)
out = pd.Series(result[0:4],index=['ADF test statistic','p-value','# lags used','# observations'])

for key,val in result[4].items():
    out[f'critical value ({key})']=val
print(out)

# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
memAvail_cyclical, memAvail_trend = hpfilter(memAvailData, lamb=1600)
# Seasonal decomposition per prendere info su trand,stagionalità e residuo
memAvailResult = seasonal_decompose(memAvailData,model='additive', period=320)
# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
memAvail_hourly_data = memAvailData.resample('1H').last().agg(['max', 'min', 'mean','std'])
memAvail_three_hourly_data = memAvailData.resample('3H').last().agg(['max', 'min', 'mean','std'])
memAvail_twelve_hourly_data = memAvailData.resample('12H').last().agg(['max', 'min', 'mean','std'])

# Predizione dei valori max,min,media nei prox 10 minuti
tsr = memAvail_trend.resample(rule='1T').mean()
tsmodel = ExponentialSmoothing(tsr, trend='mul', seasonal='mul',seasonal_periods=650).fit()
prediction = tsmodel.forecast(steps=10)
memAvailPred=prediction.agg(['max','min','mean'])

plt.ylabel('Values', fontsize=14)
plt.xlabel('Time', fontsize=14)
plt.title('Values over time', fontsize=16)
plt.plot(tsr, "-", label = 'real')
plt.plot(prediction,"--", label = 'pred')
plt.legend()

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
dfDiskFree=[]
diskFreeData1= metric_df.loc[metric_df['device']=='/dev/sda2', ['value']]
diskFreeData2= metric_df.loc[metric_df['device']=='tmpfs', ['value']]
dfDiskFree.append(diskFreeData1)
dfDiskFree.append(diskFreeData2)

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
    print(out)

# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
disk_cyclical1, disk_trend1 = hpfilter(diskFreeData1, lamb=1600)
disk_cyclical2, disk_trend2 = hpfilter(diskFreeData2, lamb=1600)

# Seasonal decomposition per prendere info su trand,stagionalità e residuo
disk_result1 = seasonal_decompose(diskFreeData1,model='additive', period=320)
disk_result2 = seasonal_decompose(diskFreeData2,model='additive', period=320)

# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
disk_hourly_data1 = diskFreeData1.resample('1H').last().agg(['max', 'min', 'mean','std'])
disk_three_hourly_data1 = diskFreeData1.resample('3H').last().agg(['max', 'min', 'mean','std'])
disk_twelve_hourly_data1 = diskFreeData1.resample('12H').last().agg(['max', 'min', 'mean','std'])

disk_hourly_data2 = diskFreeData2.resample('1H').last().agg(['max', 'min', 'mean','std'])
disk_three_hourly_data2 = diskFreeData2.resample('3H').last().agg(['max', 'min', 'mean','std'])
disk_twelve_hourly_data2 = diskFreeData2.resample('12H').last().agg(['max', 'min', 'mean','std'])

# Predizione dei valori max,min,media nei prox 10 minuti
predDiskFree=[]
for d in dfDiskFree:
    tsr = d.resample(rule='1T').mean()
    tsmodel = ExponentialSmoothing(tsr, trend='add', seasonal='mul',seasonal_periods=450).fit()
    prediction = tsmodel.forecast(steps=10)

    plt.ylabel('Values', fontsize=14)
    plt.xlabel('Time', fontsize=14)
    plt.title('Values over time', fontsize=16)
    plt.plot(tsr, "-", label = 'real')
    plt.plot(prediction,"--", label = 'pred')
    plt.legend()
    predDiskFree.append(prediction.agg(['max','min','mean']))



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
dfDiskAvail=[]
diskAvailData1= metric_df.loc[metric_df['device']=='/dev/sda2', ['value']]
diskAvailData2= metric_df.loc[metric_df['device']=='tmpfs', ['value']]
dfDiskAvail.append(diskAvailData1)
dfDiskAvail.append(diskAvailData2)

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
    print(out)

# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
diskAv_cyclical1, diskAv_trend1 = hpfilter(diskAvailData1, lamb=1600)
diskAv_cyclical2, diskAv_trend2 = hpfilter(diskAvailData2, lamb=1600)

# Seasonal decomposition per prendere info su trand,stagionalità e residuo
diskAv_result1 = seasonal_decompose(diskAvailData1,model='additive', period=320)
diskAv_result2 = seasonal_decompose(diskAvailData2,model='additive', period=320)

# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
diskAv_hourly_data1 = diskAvailData1.resample('1H').last().agg(['max', 'min', 'mean','std'])
diskAv_three_hourly_data1 = diskAvailData1.resample('3H').last().agg(['max', 'min', 'mean','std'])
diskAv_twelve_hourly_data1 = diskAvailData1.resample('12H').last().agg(['max', 'min', 'mean','std'])

diskAv_hourly_data2 = diskAvailData2.resample('1H').last().agg(['max', 'min', 'mean','std'])
diskAv_three_hourly_data2 = diskAvailData2.resample('3H').last().agg(['max', 'min', 'mean','std'])
diskAv_twelve_hourly_data2 = diskAvailData2.resample('12H').last().agg(['max', 'min', 'mean','std'])

# Predizione dei valori max,min,media nei prox 10 minuti
predDiskAvail=[]
for d in dfDiskAvail:
    tsr = d.resample(rule='1T').mean()
    tsmodel = ExponentialSmoothing(tsr, trend='add', seasonal='mul',seasonal_periods=450).fit()
    prediction = tsmodel.forecast(steps=10)

    plt.ylabel('Values', fontsize=14)
    plt.xlabel('Time', fontsize=14)
    plt.title('Values over time', fontsize=16)
    plt.plot(tsr, "-", label = 'real')
    plt.plot(prediction,"--", label = 'pred')
    plt.legend()
    predDiskAvail.append(prediction.agg(['max','min','mean']))


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
print(out)

# Applico Hoodrick-Prescott per prendere info su ciclicità e trend
recBytes_cyclical, recBytes_trend = hpfilter(recBytesData, lamb=1600)

# Seasonal decomposition per prendere info su trand,stagionalità e residuo
recBytesResult = seasonal_decompose(recBytesData,model='additive', period=320)

# Calcolo max,min,media e dev std nell'ultima ora, 3 ore, 12 ore
recBytes_hourly_data = recBytesData.resample('1H').last().agg(['max', 'min', 'mean','std'])
recBytes_three_hourly_data = recBytesData.resample('3H').last().agg(['max', 'min', 'mean','std'])
recBytes_twelve_hourly_data =recBytesData.resample('12H').last().agg(['max', 'min', 'mean','std'])

# Predizione dei valori max,min,media nei prox 10 minuti
tsr = recBytesData.resample(rule='1T').mean()
tsmodel = ExponentialSmoothing(tsr, trend='add', seasonal='add',seasonal_periods=720).fit()
prediction = tsmodel.forecast(steps=10)
predNetwork=prediction.agg(['max','min','mean'])

plt.ylabel('Values', fontsize=14)
plt.xlabel('Time', fontsize=14)
plt.title('Values over time', fontsize=16)
plt.plot(tsr, "-", label = 'real')
plt.plot(prediction,"--",label = 'pred')
plt.legend(title='Series')

