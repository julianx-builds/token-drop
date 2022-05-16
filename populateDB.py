import sqlite3
import requests

################################################################
#################### USER VARIABLES  ###########################
################################################################
POOLID = "" #Bech32 format. Should start with "pool"....
EPOCH_MIN = -1 #The first epoch included in stake calculations
EPOCH_MAX = -1 #The last epoch included in stake calculations.
               #If epoch_max is 320, it will scan the delegations
               #of epoch 320, but not 321.
################################################################
################################################################
                 
class SQLManager:
    def __init__(self):
        try:
            self.connection = sqlite3.connect('tokendrop.db')
            self.cursor = self.connection.cursor()
            print("INFO: Database created/connected")
            
            # Check if messy table has been created
            exists_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='messy'";
            self.cursor.execute(exists_query)
            result = self.cursor.fetchone()
            
            if result == None: # Create messy table
                create_messy_query = '''CREATE TABLE messy(
                    stakeID text NOT NULL,
                    epoch integer NOT NULL,
                    amount integer NOT NULL);'''
                self.cursor.execute(create_messy_query)
                print("INFO: Messy table created")
                
        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
    
    def executeQuery(self, query, returnType="no"):
        self.cursor.execute(query)
        
        if returnType == "no":
            return 0
        
        elif returnType == "fetchone":
            return self.cursor.fetchone()
        
        elif returnType == "fetchall":
            return self.cursor.fetchall()
    
    def endSQL(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        

    

def populateMessyDB(sqlManager):
    # Error checking
    if EPOCH_MIN == -1 or EPOCH_MAX == -1:
        print("ERROR: ADD VALUE TO EPOCH_MIN/EPOCH_MAX VARIABLE IN populateDB.py")
        sqlManager.endSQL()
        quit()
    elif EPOCH_MIN > EPOCH_MAX:
        print("ERROR: EPOCH MIN IS GREATER THAN EPOCH_MAX IN populateDB.py")
        sqlManager.endSQL()
        quit()


    #Populating messy with API queries
    if EPOCH_MIN == EPOCH_MAX: #If user only wants one epoch
        print("INFO: EPOCH_MIN and EPOCH_MAX are equal. Guessing you only want to do one epoch then.")
        
        response = requests.get(f"https://api.koios.rest/api/v0/pool_delegators?_pool_bech32={POOLID}&_epoch_no={EPOCH_MIN}").json()
        
        for delegation in response:
            query = f'''INSERT INTO messy(stakeID, epoch, amount) VALUES('{delegation['stake_address']}', 
                        {delegation['epoch_no']},
                        {delegation['amount']});'''
            sqlManager.executeQuery(query)
        print("INFO: Messy table populated")
    
    else:# If user wants more than one epoch    
        epoch_count = EPOCH_MIN
        
        while epoch_count <= EPOCH_MAX:
            response = requests.get(f"https://api.koios.rest/api/v0/pool_delegators?_pool_bech32={POOLID}&_epoch_no={epoch_count}").json()
        
            for delegation in response:
                query = f'''INSERT INTO messy(stakeID, epoch, amount) VALUES('{delegation['stake_address']}', 
                            {delegation['epoch_no']},
                            {delegation['amount']});'''
                sqlManager.executeQuery(query)
            print(f"INFO: Epoch {epoch_count} delegates populated")
            epoch_count+=1
        print("INFO: Messy table fully populated")
    

sqlManager = SQLManager()
populateMessyDB(sqlManager)

sqlManager.endSQL()