import sqlite3

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
            
            # Check if calculation table has been created
            exists_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='calculation'";
            self.cursor.execute(exists_query)
            result = self.cursor.fetchone()
            
            if result == None: # Create messy table
                create_messy_query = '''CREATE TABLE calculation(
                    stakeID text UNIQUE NOT NULL,
                    total_delegated integer NOT NULL,
                    owed_amount integer NOT NULL);'''
                self.cursor.execute(create_messy_query)
                print("INFO: Calculation table created")
                
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
        try:
            self.connection.commit()
            self.cursor.close()
            self.connection.close()
        except:
            print("ERROR: Could not write to database. Likely being used by another process")
    
    def noSave(self):
        try:
            self.cursor.close()
            self.connection.close()
        except:
            print("ERROR: Could not disconnect to database")
