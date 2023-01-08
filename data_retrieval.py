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
          adfuller = values['adfuller']
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

          query = "INSERT INTO metrics(nome,partizione,dickey_fuller,hourly_max,hourly_min,hourly_mean,hourly_std,three_hourly_max,three_hourly_min,three_hourly_mean,three_hourly_std,twelve_hourly_max,twelve_hourly_min,twelve_hourly_mean,twelve_hourly_std,prediction_max,prediction_min,prediction_mean) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
          values=(metric_name,disk,adfuller,hourly_max,hourly_min,hourly_mean,hourly_std,three_hourly_max,three_hourly_min,three_hourly_mean,three_hourly_std,
                   twelve_hourly_max,twelve_hourly_min,twelve_hourly_mean,twelve_hourly_std,prediction_max,prediction_min,prediction_mean)
          cursor.execute(query, values)
          cnx.commit()
     print(disk, adfuller, hourly_max, three_hourly_min, twelve_hourly_mean, prediction_max)

