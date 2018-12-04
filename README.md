# TrendMapper
TrendMapper is a QGIS Python plugin to make it easier to batch analyze NOAA weather station data for time dependent linear 
trends. 

![Trendmapper Screenshot1](https://russloewe.github.io/TrendMapper/pics/trendmapper_whole.png)

With TrendMapper you can load a vector or CSV layer with data from multiple weather stations over multiple 
dates into QGIS and produce a vector layer that shows the linear regression for each station for a chosen data column. 


## Example using NOAA Global Summary of the Year data
For this example invistigate the DX90 weather stat. The DX90 weather stat is the number of days in a given year
that were over 90 degrees F. We will use TrendMapper to convert a data set from several weather stations over 
a range of years into a vector layer showing the rate of change of the DX90 stat per year.

First load /TrendMapper/test/test_noaa_yearly.sqlite into QGIS. This layer contains yearly weather station stats from 
a couple of NOAA ground based weather stations.

![NOAA YEARLY DATA](https://russloewe.github.io/TrendMapper/pics/example_data.png)

Next, open the TrendMapper plugin.

From the Input Layer drop down select the data layer. 

For the Category drop down select 'STATION'. This tells TrendMapper to break down the data set into subsets with matching STATION values. This is so that raw data will get grouped by the station identifier. In this example the 'NAME' column would also work.

For the X variable select 'DATE' and for the Y variable select 'DX90'. Check the 'Export Stats' checkbox. TrendMapper 
uses Numpy to perform the linear regression and the Export Stats will output some of the Numpy calculation, such as 
the sum of the risiduals, the number of data points used in the regression and the rank of the least squares matrix.

In the "Additional Attributes to Copy' box select 'NAME' and 'ELEVATION' so that results layer will include the 
name of the station and the elevation of the station for each station. 

![NOAA YEARLY OPTIONS](https://russloewe.github.io/TrendMapper/pics/example_options.png)

Select OK and TrendMapper will make a new vector layer.

![NOAA YEARLY OPTIONS](https://russloewe.github.io/TrendMapper/pics/example_output.png)

In the outputted layer, the slope and intercept columns correspond to the slope and y intercept of the linear
best fit line in slop intercep form. So the slope tells us the yearly rate of change of the DX90 stat for that
weather station. For example, North Pole Ridge Oregon weather station has 0.26 more days over 90 degrees in a 
year every year.

## Example using NOAA daily data
For this example we will use TrendMapper's date formatter option to perform regression on a data set that uses 
a sting instead of and number in the date column.

First, load the /TrendMapper/test/test_noaa_daily.sqlite into QGIS.


![NOAA DAILY DATA](https://russloewe.github.io/TrendMapper/pics/example_daily_data.png)

Open TrendMapper plugin, select the vector layer from the dropdown. Use the same options as the last example, but this 
time instead of DX90 select tmax (hottest temperature that day), and check the 'format data column' check box and select 
'date' from the drop down menu. 

In the text box immediatly right you can specify the format of the date. For example, if the
date is formatted like '2018-05-25' use the default format. If the date is '2018/25/05' use '%Y/%d/%m' in the format text 
box.


![NOAA DAILY OPTIONS](https://russloewe.github.io/TrendMapper/pics/example_daily_options.png)

Note, when using the date format option, the linear regression uses days instead of years as the time unit. This is because 
the date is converted using Python's built in to ordinal function that converts dates to days since January 1, year 1.


![NOAA DAILY OUTPUT](https://russloewe.github.io/TrendMapper/pics/example_daily_output.png)

In the output above, the first weather station has an increase of 0.011 degress per day over the set of 5 datapoints that 
were used in the calculation.


Source code documentation at https://russloewe.github.io/TrendMapper/docs/

### Install
Copy TrendMapper folder into your QGIS plugins directory and enable from inside QGIS's plugin manager tool.
