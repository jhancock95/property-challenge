import pandas as pd
import sqlite3


def transactions_setup():
    '''
    * Read data from speficied files
    * Merge into single dataframe and format
    * Create and upload into SQL table
    '''


    with sqlite3.connect('tamarix.db') as conn:

        try:
            curs = conn.cursor()

            curs.execute("""DROP TABLE IF EXISTS transactions;""")

            data_2019 = pd.read_csv('.\\data\\pp-2019.csv', header=None)
            data_2020 = pd.read_csv('.\\data\\pp-2020.csv', header=None)

            merged = pd.concat([data_2019, data_2020])

            merged = merged.fillna('None')

            merged[1] = merged[1].astype(int)
            merged[10] = merged[10].astype(str)

            transactions_values = list(merged.itertuples(index=False, name=None))
            
            curs.execute(""" CREATE TABLE transactions(
                id VARCHAR(50),
                price INT,
                saledate DATETIME,
                postcode VARCHAR(10),
                property_type VARCHAR(1),
                old_new VARCHAR(1),
                duration VARCHAR(1),
                paon VARCHAR(100),
                saon VARCHAR(100),
                street VARCHAR(100),
                locality VARCHAR(100),
                town VARCHAR(50),
                district VARCHAR(50),
                county VARCHAR(50),
                ppd VARCHAR(1),
                record_status VARCHAR(1),
                PRIMARY KEY (id)
                );
                """)

            
            insert_query = """
                            INSERT INTO transactions (id, price, saledate, postcode, property_type, old_new, duration, paon, saon, street, locality, town, district, county, ppd, record_status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """
            
            curs.executemany(insert_query, transactions_values)
            
            conn.commit()
        
        except Exception as e:
            return e



def properties_setup():
    '''
    * Take unique properties from transactions list (paon + saon + postcode will always be unique)
    * Add to distinct table with property-only (i.e. irrelevant to transaction) data
    * sqlite will automatically add a hidden "rowid" property serving as unique PK
    '''

    try:
        with sqlite3.connect('tamarix.db') as conn:
            curs = conn.cursor()

            curs.execute("""DROP TABLE IF EXISTS properties;""")

            select_query = f"""
                            SELECT count(*) FROM sqlite_master WHERE type='table' AND name='transactions';
                            """
            curs.execute(select_query)   
            
            curs.execute(""" 
            CREATE TABLE properties(
            paon VARCHAR(100),
            saon VARCHAR(100),
            postcode VARCHAR(10),
            street VARCHAR(100),
            locality VARCHAR(100),
            town VARCHAR(100),
            district VARCHAR(100),
            county VARCHAR(100));
            """)

            
            insert_query = """
                            INSERT INTO properties(paon, saon, postcode, street, locality, town, district, county) SELECT DISTINCT paon, saon, postcode, street, locality, town, district, county FROM transactions;
                            """
            
            curs.execute(insert_query)
            
            conn.commit()
    
    except Exception as e:
        return e



def postcodes_setup():

    try:
        with sqlite3.connect('tamarix.db') as conn:
            curs = conn.cursor()

            curs.execute("""DROP TABLE IF EXISTS postcodes;""")        

            data_postcode = pd.read_csv('.\\data\\postcode-data.csv')

            data_postcode['Postcode 2'] =  data_postcode['Postcode 2'].astype(str)
            data_postcode.drop(['Postcode 1', 'Postcode 3', 'Spatial Accuracy', 'Last Uploaded'], axis=1, inplace=True)

            postcode_values = list(data_postcode.itertuples(index=False, name=None))

            curs.execute(""" CREATE TABLE postcodes(
                    postcode VARCHAR(10),
                    easting INT,
                    northing INT,
                    postitional INT,
                    local_authority VARCHAR(100),
                    longitude REAL,
                    latitude REAL,
                    location VARCHAR(100),
                    socrata_id INT
                );
                """)

            
            insert_query = """
                            INSERT INTO postcodes (postcode, easting, northing, postitional, local_authority, longitude, latitude, location, socrata_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                            """
            
            curs.executemany(insert_query, postcode_values)
            
            conn.commit()

    except Exception as e:
        return e