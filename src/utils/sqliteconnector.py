import os, json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
BASEFOLDER = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class SqliteConnector:
    engine = {}
    session = {}
    config_path = os.path.join(BASEFOLDER, "src", "config", "db_list.json")
    def __init__(self, service:str):
        if service not in SqliteConnector.engine:
            with open(self.config_path) as default_config_file:
                config = json.load(default_config_file)
            sqlite_uri = self.__compose_uri(config['sqlite3'][service])
            engine = create_engine(sqlite_uri)
            SqliteConnector.engine[service] = engine
            SqliteConnector.session[service] = sessionmaker(bind=engine)
        connection = SqliteConnector.engine[service].connect()
        self.session = SqliteConnector.session[service](bind=connection)
    
    def get_session(self):
        return self.session
    
    def session_close(self):
        self.session.get_bind().close()
        self.session.close()

    def query(self, *entities, **kwargs):
        return self.session.query(*entities, **kwargs)
    
    def insert(self, *entities, **kwargs):
        return self.session.insert(*entities, **kwargs)
    
    def execute_raw_sql(self, *entites, **kwargs):
        return self.session.execute(*entites, **kwargs)
    
    def __compose_uri(self, config):
        path = config["path"]
        return f"sqlite:///{path}"
    
class SqliteHelper:
    def __init__(self, CONN_INFO):
        self.sql_connector = SqliteConnector(CONN_INFO)

    def ExecuteUpdate(self, *entities, **kwargs):
            count = 0
            try:   
                result = self.sql_connector.execute_raw_sql(*entities, **kwargs)
                count = result.rowcount
            except Exception as e:
                print(e)
                self.sql_connector.get_session().rollback()
            else:    
                self.sql_connector.get_session().commit()
            finally:         
                self.sql_connector.session_close()
            return count
            
    def ExecuteDictSelect(self, *entities, **kwargs):
            results = self.sql_connector.execute_raw_sql(*entities, **kwargs)
            data = [dict(result) for result in results] 
            self.sql_connector.session_close()
            return data     
    def ExecuteSelect(self, *entities, **kwargs):
        result = self.sql_connector.execute_raw_sql(*entities, **kwargs)
        data = result.fetchall()       
        self.sql_connector.session_close()
        return data     
