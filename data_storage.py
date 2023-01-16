from kafka import KafkaConsumer
import json
import mysql.connector

# Connect to the MySQL database
cnx = mysql.connector.connect(user='root', password='Lorenzo99',host='localhost', database='test_dsbd')
cursor = cnx.cursor()

consumer=KafkaConsumer(bootstrap_servers='localhost:9092')
consumer.subscribe(['prometheusdata'])

# Read data from kafka
for message in consumer:
     data=json.loads(message[6])
     metric_name=data['metric_name']
     for disk, values in data.items():
          if disk == 'metric_name':
               continue
          adfuller_statistic = values['adfuller_statistic']
          adfuller_p_value = values['adfuller_p_val']
          adfuller_stationary = values['adfuller_stationary']
          adfuller_critical= values['adfuller_critical']

          acf= values['acf']

          decompose_season = values['decompose_season']
          decompose_trend = values ['decompose_trend']
          cyclical_component = values['cyclical_component']

          hourly_data = values['hourly_data']
          hourly_max=str(hourly_data['value']['max'])
          hourly_min= str(hourly_data['value']['min'])
          hourly_mean=str(hourly_data['value']['mean'])
          hourly_std= str(hourly_data['value']['std'])

          three_hourly_data = values['three_hourly_data']
          three_hourly_max= str(three_hourly_data['value']['max'])
          three_hourly_min= str(three_hourly_data['value']['min'])
          three_hourly_mean=str(three_hourly_data['value']['mean'])
          three_hourly_std= str(three_hourly_data['value']['std'])

          twelve_hourly_data = values['twelve_hourly_data']
          twelve_hourly_max= str(twelve_hourly_data['value']['max'])
          twelve_hourly_min= str(twelve_hourly_data['value']['min'])
          twelve_hourly_mean=str(twelve_hourly_data['value']['mean'])
          twelve_hourly_std= str(twelve_hourly_data['value']['std'])

          prediction = values['10m_prediction']
          prediction_max= str(prediction['max'])
          prediction_min= str(prediction['min'])
          prediction_mean=str(prediction['mean'])

          query="INSERT INTO metrics(nome,partizione) VALUES (%s,%s)"
          values=(metric_name,disk)
          cursor.execute(query, values)
          cnx.commit()
          
          for key,value in decompose_season.items():
               values2=(metric_name,disk,key,'seasonal',value)
               query2="INSERT INTO decomposition(nome,partizione,timestamp,tipologia,value) VALUES(%s,%s,%s,%s,%s)"
               cursor.execute(query2,values2)
               cnx.commit()
          for key,value in decompose_trend.items():
               values3=(metric_name,disk,key,'trend',value)
               query3="INSERT INTO decomposition(nome,partizione,timestamp,tipologia,value) VALUES(%s,%s,%s,%s,%s)"
               cursor.execute(query3,values3)
               cnx.commit()
          
          for key,value in cyclical_component.items():
               values3=(metric_name,disk,key,value)
               query3="INSERT INTO hodrick_prescott(nome,partizione,timestamp,value) VALUES(%s,%s,%s,%s)"
               cursor.execute(query3,values3)
               cnx.commit()
          
          
          query4="INSERT INTO dickey_fuller(nome,partizione,test_statistic,p_value,is_stationary,crit_value_1,crit_value_5,crit_value_10) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
          values4=(metric_name,disk,adfuller_statistic,adfuller_p_value,adfuller_stationary,adfuller_critical[0],adfuller_critical[1],adfuller_critical[2])
          cursor.execute(query4,values4)
          cnx.commit()

          for item in acf:
               query5="INSERT INTO autocorrelation(nome,partizione,value) VALUES (%s,%s,%s)"
               values5=(metric_name,disk,item)
               cursor.execute(query5, values5)
               cnx.commit()

          query6="INSERT INTO aggregates(nome,partizione,intervallo,tipologia,value) VALUES(%s,%s,%s,%s,%s)"
          tuples=[]
          tuples.append([metric_name,disk,'1h','max',hourly_max])
          tuples.append([metric_name,disk,'1h','min',hourly_min])
          tuples.append([metric_name,disk,'1h','mean',hourly_mean])
          tuples.append([metric_name,disk,'1h','std_dev',hourly_std])
          tuples.append([metric_name,disk,'3h','max', three_hourly_max])
          tuples.append([metric_name,disk,'3h','min',three_hourly_min])
          tuples.append([metric_name,disk,'3h','mean',three_hourly_mean])
          tuples.append([metric_name,disk,'3h','std_dev',three_hourly_std])
          tuples.append([metric_name,disk,'12h','max',twelve_hourly_max])
          tuples.append([metric_name,disk,'12h','min',twelve_hourly_min])
          tuples.append([metric_name,disk,'12h','mean',twelve_hourly_mean])
          tuples.append([metric_name,disk,'12h','std_dev',twelve_hourly_std])
          
          for tup in tuples:
               cursor.execute(query6, tup)
          
          query7="INSERT INTO aggregates(nome,partizione,intervallo,tipologia,valore_predetto) VALUES(%s,%s,%s,%s,%s)"
          value7=(metric_name,disk,'10m','max',prediction_max)
          cursor.execute(query7, value7)
          value8=(metric_name,disk,'10m','min',prediction_min)
          cursor.execute(query7, value8)
          value9=(metric_name,disk,'10m','mean',prediction_mean)
          cursor.execute(query7, value9)
          cnx.commit()

cnx.close()
consumer.close()