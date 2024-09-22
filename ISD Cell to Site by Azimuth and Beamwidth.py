#Set Time
import time
time_start_zero = time.time()

#Clear the layer
#QgsProject.instance().removeAllMapLayers()

#Variable Setting
filename_source = r"D:\Learning & Training\QGIS\@AL\ISD\RAW\Cell.csv"
filename_target = r"D:\Learning & Training\QGIS\@AL\ISD\RAW\Site.csv"
radiusx = 6
beamx = 90
result_path = r"D:\Learning & Training\QGIS\@AL\ISD\RAW\Result.csv"

#ploting_csv file as source
uri="file:///"+filename_source+'?delimiter=,&crs=epsg:4326&xField=Longitude&yField=Latitude'
print(uri)
lyr = QgsVectorLayer(uri, 'Souce_Cell','delimitedtext')
#QgsProject.instance().addMapLayer(lyr)

#ploting_csv file as target
uri2="file:///"+filename_target+'?delimiter=,&crs=epsg:4326&xField=Longitude&yField=Latitude'
print(uri2)
lyr2 = QgsVectorLayer(uri2, 'Site_Target','delimitedtext')
#QgsProject.instance().addMapLayer(lyr2)
#Time Elapsed
time_current = time.time()
duration_start_second = round(time_current-time_start_zero,2)
duration_start_minute = duration_start_second // 60
duration_start_second %= 60
duration_start = f"{int(duration_start_minute)}m{round(int(duration_start_second),2)}s"
print(duration_start,"Plotting Source and Target")

result = processing.run("shapetools:createpie", 
        {'INPUT':lyr,'ShapeType':0,
        'AzimuthMode':1,
        'Azimuth1':QgsProperty.fromExpression('"Azimuth"'),
        'Azimuth2':beamx,'Radius':radiusx,
        'UnitsOfMeasure':0,
        'DrawingSegments':36,'OUTPUT':'TEMPORARY_OUTPUT'})
        

lyr_beam = result['OUTPUT']

name = lyr_beam.name()
new_name = name.replace('Output layer','source_cell')
lyr_beam.setName(new_name)
#QgsProject.instance().addMapLayer(lyr_beam)
#Time Elapsed
time_current = time.time()
duration_start_second = round(time_current-time_start_zero,2)
duration_start_minute = duration_start_second // 60
duration_start_second %= 60
duration_start = f"{int(duration_start_minute)}m{round(int(duration_start_second),2)}s"
print(duration_start,"Coverage Beamwidth and Radius")

result = processing.run("native:joinattributesbylocation",
        {'INPUT':lyr_beam,'PREDICATE':[1],'JOIN':lyr2
        ,'JOIN_FIELDS':[],'METHOD':0,'DISCARD_NONMATCHING':True,'PREFIX':'',
        'OUTPUT':'TEMPORARY_OUTPUT'})
        

lyr_join = result['OUTPUT']
name = lyr_join.name()
new_name = name.replace('Joined layer','lyr_join')
lyr_join.setName(new_name)
#QgsProject.instance().addMapLayer(lyr_join)
#Time Elapsed
time_current = time.time()
duration_start_second = round(time_current-time_start_zero,2)
duration_start_minute = duration_start_second // 60
duration_start_second %= 60
duration_start = f"{int(duration_start_minute)}m{round(int(duration_start_second),2)}s"
print(duration_start,"Joining Source and Target")

result = processing.run(
"native:fieldcalculator", 
{'INPUT':lyr_join,
'FIELD_NAME':'distance',
'FIELD_TYPE':0,
'FIELD_LENGTH':0,
'FIELD_PRECISION':0,
'FORMULA':'6371 * 2 * asin(sqrt(sin(((radians("Latitude_2")) - (radians("Latitude")))/2)^2 + cos((radians("Latitude"))) * cos((radians("Latitude_2"))) * sin(((radians("Longitude_2")) - (radians("Longitude")))/2)^2))',
'OUTPUT':'TEMPORARY_OUTPUT'})

lyr_distance = result['OUTPUT']
name = lyr_distance.name()
new_name = name.replace('Calculated','lyr_distance')
lyr_distance.setName(new_name)
QgsProject.instance().addMapLayer(lyr_distance, addToLegend=False)
#Time Elapsed
time_current = time.time()
duration_start_second = round(time_current-time_start_zero,2)
duration_start_minute = duration_start_second // 60
duration_start_second %= 60
duration_start = f"{int(duration_start_minute)}m{round(int(duration_start_second),2)}s"
print(duration_start,"Distance Calculation")

import pandas as pd

layer = QgsProject.instance().mapLayersByName("lyr_distance")[0]
data = [feature.attributes() for feature in layer.getFeatures()]
field_names = [field.name() for field in layer.fields()]
df = pd.DataFrame(data, columns=field_names)

df['_rank']=df.groupby('Cellname')['distance'].rank(method="first", ascending=True)
df_test=df
df_test=df_test.loc[df_test['_rank']<4]

import pandas as pd

pivot_df = df_test.pivot(index=['Cellname', 'Longitude', 'Latitude', 'Azimuth'], 
                    columns='_rank', 
                    values=['Sitename', 'distance'])

pivot_df.columns = [f'{col[0]} {col[1]}' for col in pivot_df.columns]
pivot_df.reset_index(inplace=True)
pivot_df.columns = ['CellName','Longitude',	'Latitude',	'Azimuth', 'Neighbor1', 'Neighbor2', 'Neighbor3', 'Dist1', 'Dist2','Dist3']
pivot_df['Dist1'] = pd.to_numeric(pivot_df['Dist1'])
pivot_df['Dist2'] = pd.to_numeric(pivot_df['Dist2'])
pivot_df['Dist3'] = pd.to_numeric(pivot_df['Dist3'])
pivot_df['InterSite Distance'] = pivot_df[['Dist1','Dist2','Dist3']].mean(axis=1)
pivot_df.insert(5,'Dist1',pivot_df.pop('Dist1'))
pivot_df.insert(7,'Dist2',pivot_df.pop('Dist2'))
pivot_df.insert(9,'Dist3',pivot_df.pop('Dist3'))

pivot_df.to_csv(result_path, index=False)

#Time Elapsed
time_current = time.time()
duration_start_second = round(time_current-time_start_zero,2)
duration_start_minute = duration_start_second // 60
duration_start_second %= 60
duration_start = f"{int(duration_start_minute)}m{round(int(duration_start_second),2)}s"
print(duration_start,"Done")
print("\nPlease check the Result.CSV file")