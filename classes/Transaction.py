import sqlite3
import pandas as pd

class Transaction:
    
    def __init__(self):
        self.transaction_id = None
        self.price = None
        self.saledate = None
        self.postcode = None
        self.property = property #Every transaction has a property
        

    def transaction_rates(self):
        if self.transaction_id:
            
            with sqlite3.connect('tamarix.db') as conn:
                curs = conn.cursor()
                
                select_query = f"""
                                SELECT * FROM transactions WHERE id = '{self.transaction_id}'
                                """
                
                curs.execute(select_query)   
                rows = curs.fetchall()
                return rows
        else:
            return 'No transaction ID available'
        


    def transaction_amount_change():
        try:
            with sqlite3.connect('tamarix.db') as conn:
                
                select_query = f"""
                                SELECT * FROM transactions;
                                """

                df = pd.read_sql(select_query, conn)

                df['postcode_start'] = df['postcode'].apply(lambda x: x.split(' ')[0]) #Sets up column with just first part of postcode
                df['transaction_year'] = df['saledate'].apply(lambda x: x[0:4])

                df_2019 = df[df['transaction_year'] == "2019"]
                df_2020 = df[df['transaction_year'] == "2020"]

                df_2019 = df_2019['postcode_start'].value_counts(ascending=False).reset_index()
                df_2020 = df_2020['postcode_start'].value_counts(ascending=False).reset_index()
        

                merged_df = pd.merge(df_2019, df_2020, on='postcode_start', how='outer', suffixes=('_2019', '_2020'))

                merged_df['difference'] = merged_df['count_2020'] - merged_df['count_2019']

                sorted_df = merged_df.sort_values(by='difference', ascending=False)
                top_5 = sorted_df.head(5)

                result = {}

                for i in list(top_5['postcode_start'].keys()):
                    result[top_5['postcode_start'][i]] = top_5['difference'][i]

                return result
            
        except Exception as e:
            return e
        


    @classmethod
    def set_transaction_from_id(cls, transaction_id):
        
        # Returns a Transaction object with attributes populated

        if transaction_id:
            try:
                instance = cls()
                with sqlite3.connect('tamarix.db') as conn:
                    curs = conn.cursor()

                    select_query = f"""
                                SELECT * FROM transactions WHERE id="{transaction_id}";
                                    """
                
                                
                    curs.execute(select_query)   
                    rows = curs.fetchall()
                    
                    fields = rows[0]

                    instance.transaction_id = fields[0]
                    instance.price = fields[1]
                    instance.saledate = fields[2]
                    instance.postcode = fields[3]


                    return instance
                
            except Exception as e:
                return e
        else:
            return 'No transaction id'
        
    def vars(self):
        return {
            "id":self.transaction_id,
            "price":self.price,
            "saledate":self.saledate,
            "postcode":self.postcode,    
            }
