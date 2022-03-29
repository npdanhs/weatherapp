import os.path
import enum
import json
import datetime
import copy

class User:
    def __init__(self, u, p):
        self.username = u
        self.password = p

class AdminUser(User):
    def __init__(self, u ,p):
        super().__init__(u, p)

class UserDataHandler:
    class LoginState(enum.Enum):
        NO_USERNAME = 0,
        WRONG_PASSWORD = 1,
        VALID = 2

    class RegisterState(enum.Enum):
        DUPLICATE = 0,
        VALID = 1,
        #WEAK_PASSWORD = 2

    class JSONEncoder(json.JSONEncoder):
        def default(self, o):
            if type(o) == AdminUser:
                return {"admin_username": o.username, "admin_password": o.password}
            elif type(o) == User:
                return {'username': o.username, 'password': o.password }
            else:
                return super().default(o)
    
    def __init__(self, jsonPath):
        self.dataFilePath = jsonPath
        self.users = None
        self.backup = None
        self.adminUser = None

    def Verify(self, username, password):
        assert self.users is not None, "Database is not loaded"

        print(username, password)
        print(self.users)
        if username in self.users:
            if self.users[username] == password:
                return UserDataHandler.LoginState.VALID
            else:
                return UserDataHandler.LoginState.WRONG_PASSWORD
        else:
            return UserDataHandler.LoginState.NO_USERNAME

    def VerifyAdmin(self, username, password):
        assert self.users is not None, "Database is not loaded"

        if username == self.adminUser.username and password == self.adminUser.password:
            return True
        
        return False

    def Register(self, username, password):
        assert self.users is not None, "Database is not loaded"

        if username not in self.users:
            self.users[username] = password
            return UserDataHandler.RegisterState.VALID
        else:
            return UserDataHandler.RegisterState.DUPLICATE

    def Delete(self, username):
        assert self.users is not None, "Database is not loaded"
        
        if username in self.users:
            self.users.pop(username)

    def RequestPassword(self, username):
        assert self.users is not None, "Database is not loaded"

        if username in self.users:
            return self.users[username]

        return None

    def LoadDatabase(self):
        try:
            self.backup = None
            self.users = dict()
            if os.path.isfile(self.dataFilePath):
                with open(self.dataFilePath, 'r') as fp:
                    self.backup = fp.read()
                    items = json.loads(self.backup)
                for item in items:
                    if "admin_username" in item:
                        if not self.adminUser:
                            self.adminUser = AdminUser(item['admin_username'], item['admin_password'])
                        else:
                            raise Exception('More than one admin account exists')
                    else:
                        username = item['username']                
                        password = item['password']
                        assert username not in self.users            
                        self.users[username] = password
            
            if not self.adminUser:
                self.adminUser = AdminUser('admin', 'admin')

            print(self.users)
            return True
        except Exception as e:
            return False

    def SaveDatabase(self):
        try:
            #backupPah = self.datafilepath + datetime.datetime.today().strftime('%Y%m%d_%H%M%S') + '.BAK'
            backupPath = self.dataFilePath + '.BAK'
            if self.backup:
                with open(backupPath, 'w') as bfp:
                    bfp.write(self.backup)
            with open(self.dataFilePath, "w") as fp:
                saveThis = [self.adminUser] + [User(key, value) for key, value in self.users.items()]
                json.dump(saveThis, fp, indent='\t', cls=UserDataHandler.JSONEncoder)
            return True
        except Exception as e:
            print(e)
            return False

if __name__ == '__main__':
    from pathlib import Path
    
    JSON_PATH = os.path.join(Path(__file__).parent.absolute(),"data\\user_data.json")
    a = UserDataHandler(JSON_PATH)
    a.LoadDatabase()
    a.Register('aaaa', '111')
    a.Register('bbbb', '222')
    a.Register('cccd', '333')
    print(a.adminUser.username)
    a.SaveDatabase()