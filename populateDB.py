import os
import requests
from sqlManager import SQLManager
from dotenv import load_dotenv

load_dotenv()

POOLID = os.getenv('POOLID')
EPOCH_MIN = int(os.getenv('EPOCH_MIN'))
EPOCH_MAX = int(os.getenv('EPOCH_MAX')) 
RATE = float(os.getenv('RATE')) 

                             
def populateMessyDB(sqlManager):
    # Error checking
    if EPOCH_MIN == -1 or EPOCH_MAX == -1:
        print("ERROR: ADD VALUE TO EPOCH_MIN/EPOCH_MAX VARIABLE IN populateDB.py")
        return 1
    elif EPOCH_MIN > EPOCH_MAX:
        print("ERROR: EPOCH MIN IS GREATER THAN EPOCH_MAX IN populateDB.py")
        return 1
    else:
        #Populating messy with API queries
        if EPOCH_MIN == EPOCH_MAX: #If user only wants one epoch
            print("INFO: EPOCH_MIN and EPOCH_MAX are equal. Guessing you only want to do one epoch then.")
            
            response = requests.get(f"https://api.koios.rest/api/v0/pool_delegators?_pool_bech32={POOLID}&_epoch_no={EPOCH_MIN}").json()
            
            if len(response) == 0:
                    print("ERROR: POOLID INCORRECT OR NO DELEGATES FOUND FOR EPOCH BETWEEN MAX AND MIN")
                    return 1
            
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
                
                if len(response) == 0:
                    print(f"WARNING: POOLID INCORRECT OR NO DELEGATES FOUND FOR EPOCH {epoch_count}")
                
                else:
                    for delegation in response:
                        query = f'''INSERT INTO messy(stakeID, epoch, amount) VALUES('{delegation['stake_address']}', 
                                    {delegation['epoch_no']},
                                    {delegation['amount']});'''
                        sqlManager.executeQuery(query)
                    print(f"INFO: Epoch {epoch_count} delegates populated")
                epoch_count+=1
            print("INFO: Messy table fully populated")
            
        return 0
            
def populateCalculationDB(sqlManager):
    query = '''SELECT stakeID, sum(amount) as TotalAmount from messy GROUP BY stakeID;'''
    
    unique_stake_IDs = sqlManager.executeQuery(query, returnType="fetchall")
    
    for unique_id in unique_stake_IDs:
        query = f'''INSERT INTO calculation(stakeID, total_delegated, owed_amount)
                    VALUES('{unique_id[0]}', 
                    {unique_id[1]},
                    ({unique_id[1]}/1000000)*{RATE});'''
        sqlManager.executeQuery(query)
    print("INFO: Calculation table populated")
    
    return 0
    

sqlManager = SQLManager()

if populateMessyDB(sqlManager) == 0 and populateCalculationDB(sqlManager) == 0:
    print("INFO: ISPO data collected!")
    sqlManager.endSQL()
else:
    print("ERROR OCCURED")
    sqlManager.noSave()

del sqlManager

