import requests
from sqlManager import SQLManager

################################################################
#################### USER VARIABLES  ###########################
################################################################
POOLID = "" #Bech32 format. Should start with "pool"....
EPOCH_MIN = -1 #The first epoch included in stake calculations
EPOCH_MAX = -1 #The last epoch included in stake calculations.
               #If epoch_max is 320, it will scan the delegations
               #of epoch 320, but not 321.
RATE = 0.2 #The rate that tokens will be allocated, per ADA.
           #For example, if a user choses a rate of 0.2, a delegate
           #will earn 0.2 of token "X" per ADA, per Epoch.
################################################################
################################################################
                             
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
    else:
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
    

sqlManager = SQLManager()
populateMessyDB(sqlManager)
populateCalculationDB(sqlManager)

sqlManager.endSQL()
del sqlManager
