from flask import Flask, request
import sqlite3
import pandas as pd
import data_load_functions
from classes.Property import Property
from classes.Postcode import Postcode
from classes.Transaction import Transaction
import math
import numpy as np
import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt



app = Flask(__name__)

@app.route('/database_setup', methods=["GET"])
def database_setup():
    '''
    It shouldn't be necessary to run this route as the sqlite db file is included 
    '''
    try:
        data_load_functions.transactions_setup()
        data_load_functions.properties_setup()
        data_load_functions.postcodes_setup()

        return '<h1>Database setup underway</h1>'
    except:
        return '<h1>Error in database setup</h1>'



@app.route('/property_from_transaction_id', methods=["GET"])
def property_from_transaction_id():
    '''
    @input: transaction_id - relevant transaction ID

    @return: json containing data relevant to ID

    '''

    transaction_id = request.args.get('transaction_id')

    property = Property.set_property_from_transaction(transaction_id=transaction_id)

    return property.vars()


@app.route('/postcode_sales', methods=["GET"])
def postcode_sales():

    '''
    @input: postcode
    @input: start_date - start of date range
    @input: end_date - end of date range (now, if not specified)
    @input: id_only - determine whether full json is necessary or just list of IDs

    @return: list of transaction jsons for the postcode and dates given
    '''

    
    postcode = request.args.get('postcode')

    if not postcode:
        return 'No postcode'
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    id_only = request.args.get('id_only')


    result = Postcode.postcode_sales(postcode=postcode, start_date=start_date, end_date=end_date)

    if id_only == 'yes':
        result = [item['id'] for item in result]

    return {'transactions':result}


@app.route('/transaction_amount_change', methods=["GET"])
def transaction_amount_change():
    '''
    @return: json containing the postcodes with the highest increase in transactions between 2019-2020
    '''

    result = Transaction.transaction_amount_change()
    return result


@app.route('/migration', methods=["GET"])
def migration():
    '''
    @input: year - year user wishes to access migration data for (default 2020)

    @return: latitude and longitude for migration 'centre of gravity'
    '''
    if request.args.get('year'):
        year = request.args.get('year')

        if year not in ['2019', '2020']:
            return 'Invalid year'
    else:
        year = '2020'
    
    try:
        with sqlite3.connect('tamarix.db') as conn:    
            
            latitude_select_query = f"""
                            SELECT 
                            t1.latitude,
                            t2.count,
                            (t1.latitude*t2.count) as weighted
                            FROM
                            (SELECT postcode, latitude FROM postcodes) t1
                            JOIN
                            (SELECT postcode, COUNT(id) as count FROM transactions WHERE saledate >= "{year}-01-01" AND saledate <= "{year}-12-31" 
                            GROUP BY postcode) t2                    
                            ON
                            t1.postcode = t2.postcode
                            ORDER BY t2.count
                            ;
                            """
            
            longitude_select_query = f"""
                            SELECT 
                            t1.longitude,
                            t2.count,
                            (t1.longitude*t2.count) as weighted
                            FROM
                            (SELECT postcode, longitude FROM postcodes) t1
                            JOIN
                            (SELECT postcode, COUNT(id) as count FROM transactions WHERE saledate >= "{year}-01-01" AND saledate <= "{year}-12-31" 
                            GROUP BY postcode) t2
                            ON
                            t1.postcode = t2.postcode
                            ORDER BY t2.count
                            ;
                            """
            
            # `(t1.longitude*t2.count) as weighted` determines the weighting
            # measure of how MANY people moved to a place - not value
            
            latitude_df = pd.read_sql(latitude_select_query, conn)
            longitude_df = pd.read_sql(longitude_select_query, conn)

            # Weighted totals / overall total = weighted average
            weighted_lat = latitude_df['weighted'].sum()/latitude_df['count'].sum()
            weighted_long = longitude_df['weighted'].sum()/longitude_df['count'].sum()

            return {'latitude':weighted_lat, 'longitude':weighted_long}
    
    except Exception as e:
        return e


@app.route('/distance_from_london', methods=["GET"])
def distance_from_london():
    '''
    @return: json containing deciles of distance from london and average price for each decile
    '''
    try:
        with sqlite3.connect('tamarix.db') as conn:

            select_query = f"""
                            SELECT postcode, latitude, longitude FROM postcodes WHERE postcode LIKE 'EC1A%';
                            """
            
            ec1a_df = pd.read_sql(select_query, conn)

            #Getting the geographic centre of EC1A
            mean_lat = ec1a_df['latitude'].mean()
            mean_long = ec1a_df['longitude'].mean()

            select_query = """
                        SELECT
                        t1.postcode,
                        t1.price,
                        t2.latitude,
                        t2.longitude

                        FROM
                        
                        (
                            SELECT 
                            postcode, 
                            AVG(price) as price
                            FROM 
                            transactions
                            GROUP BY postcode
                        ) t1
                        
                        JOIN
                        
                        (
                            SELECT 
                            postcode, 
                            latitude,
                            longitude
                            FROM 
                            postcodes              
                        ) t2
                        
                        ON t1.postcode = t2.postcode

                        """
        
        df = pd.read_sql(select_query, conn)


        #Calculates a column containing the distance between the postcode and EC1A
        df['distance'] = np.sqrt((df['latitude'] - mean_lat)**2 + (df['longitude'] - mean_long)**2)

        min_distance = df['distance'].min()
        max_distance = df['distance'].max()

        #Breaks the whole distance into deciles
        decile = (max_distance - min_distance)/9

        #Assigns a decile to each postcode
        df['decile'] = df['distance'].apply(lambda x: math.ceil(x/decile))

        #Gets the average price of a property in each decile
        #Distance could also be added if necessary
        return df.groupby(['decile']).mean()['price'].to_dict()
    
    except Exception as e:
        return e


@app.route('/inflation_measure', methods=["GET"])
def inflation_measure():

    '''
    @input: measure - a column from the cpi-inflation-index file

    @return: png plot of relationship between that measure and house prices
    '''

    #Allows user to specify specific measure in URL
    if request.args.get('measure'):
        measure = request.args.get('measure')
    else:
        measure = 'CPI wts: Food, alcoholic beverages & tobacco GOODS'
    

    inflation = pd.read_csv('.\\data\\cpi-inflation-index.csv')
    
    #Leaving behind the years and the chosen measure
    inflation['Title'] = pd.to_numeric(inflation['Title'], errors="coerce")
    inflation = inflation[['Title', measure]]

    #Only fields with data
    inflation = inflation.dropna()

    inflation['Title'] = inflation['Title'].map(lambda x: str(x)[:4])
    inflation = inflation.rename(columns={"Title":"year"})



    prices = pd.read_csv('.\\data\\Average-prices-2021-03.csv')
    prices = prices[prices['Region_Name'] == 'United Kingdom']
    prices['year'] = prices['Date'].apply(lambda x: x[:4])

    #Getting the mean price for each year
    prices = prices.groupby('year',as_index=False).mean(numeric_only=True)

    #As data is only available on the inflation index after 1995, this is what we want to keep
    prices_after_95 = prices[prices['year'].astype(int) > 1995]

    price_list = prices_after_95[['Average_Price', 'year']]

    
    merged = price_list.merge(inflation)
    plot_dataframe = merged[['Average_Price', measure]]


    fig, ax = plt.subplots(figsize=(9, 9))

    scatter = ax.scatter(
        x=plot_dataframe[::-1][measure],
        y=plot_dataframe[::-1]['Average_Price'],
        c='DarkBlue'
    )

    # Save the plot to a BytesIO object
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    # Return the plot as a response
    return Response(output.getvalue(), mimetype='image/png')



if __name__ == '__main__':
   app.run(host='0.0.0.0',port=5000, debug=True)

