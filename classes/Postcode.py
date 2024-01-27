import sqlite3
from .Transaction import Transaction

class Postcode:
    
    def __init__(self, postcode):
        self.postcode = postcode
        self.properties = [] #A postcode can have many properties
        self.transactions = []
    
    def add_property(self, property):
        self.properties.append(property)
        
    def get_all_properties(self):
        return self.properties
    
    def postcode_sales(postcode, start_date, end_date):

        if postcode:
            try:
            
                with sqlite3.connect('tamarix.db') as conn:
                    curs = conn.cursor()
                    
                    select_query = f"""
                                    SELECT id FROM transactions WHERE postcode LIKE '{postcode}%' 
                                    """
                    #LIKE and percentage% mean that a full postcode not required

                    if start_date:
                        select_query += f"AND saledate >= '{start_date}'"
                        
                    if end_date:
                        select_query += f"AND saledate <= '{end_date}'"
                        
                    curs.execute(select_query)   
                    rows = curs.fetchall()

                    result_list = []
                                    
                    for element in rows:
                        transaction_id = element[0]
                        #Creates transaction objects
                        transaction = Transaction.set_transaction_from_id(transaction_id=transaction_id)
                        result_list.append(transaction.vars())

                    return result_list
            
            except Exception as e:
                return e
        else:
            return 'No postcode available'
    