import sqlite3

class Property:
    
    def __init__(self, id=None, Postcode=None):
        self.id = id
        self.postocde = Postcode, #Every property has a postcode
        self.transactions = [] #A property can be in many transactions

        self.id = None
        self.paon = None
        self.saon = None
        self.postcode = None
        self.street = None
        self.locality = None
        self.county = None 
    
    @classmethod
    def set_property_from_transaction(cls, transaction_id):
        instance = cls()
        if transaction_id:
            try:
                with sqlite3.connect('tamarix.db') as conn:
                    curs = conn.cursor()

                    select_query = f"""
                                SELECT p.rowid, p.paon, p.saon, p.postcode, p.street, p.locality, p.town, p.district, p.county
                                FROM properties p
                                JOIN transactions t ON p.paon = t.paon AND p.saon = t.saon AND p.postcode = t.postcode
                                WHERE t.id = "{transaction_id}";
                                    """
                
                    
                    #rowid used due to sqllite usage. Can be subbed for other id field. 
                    
                    curs.execute(select_query)   
                    rows = curs.fetchall()
                    
                    fields = rows[0]

                    instance.id = fields[0]
                    instance.paon = fields[1]
                    instance.saon = fields[2]
                    instance.postcode = fields[3]
                    instance.street = fields[4]
                    instance.locality = fields[5]
                    instance.county = fields[6] 

                    return instance
                
            except Exception as e:
                return e
            
        else:
            return 'No transaction id'
        
    def vars(self):
        return {
            "id":self.id,
            "paon":self.paon,
            "saon":self.saon,
            "postcode":self.postcode,
            "street":self.street,
            "locality":self.locality,
            "county":self.county        
            }
