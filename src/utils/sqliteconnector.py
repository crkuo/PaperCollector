import os, json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import traceback
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
    
    def execute_raw_sql(self, statement, params=None, **kwargs):
        """
        :param statement: SQL 指令 (字串或 SQLAlchemy text() 物件)
        :param params: 可選，字典形式的參數
        :param **kwargs: 其餘要傳給 session.execute() 的參數，如 execution_options
        """
        # 如果進來的 statement 還是純字串，可自行用 text() 包裹
        if isinstance(statement, str):
            statement = text(statement)
        return self.session.execute(statement, params, **kwargs)
    
    def __compose_uri(self, config):
        path = config["path"]
        return f"sqlite:///{path}"
    
class SqliteHelper:
    def __init__(self, CONN_INFO):
        self.sql_connector = SqliteConnector(CONN_INFO)

    def ExecuteUpdate(self, statement, params=None, **kwargs):
        count = 0
        try:
            result = self.sql_connector.execute_raw_sql(statement, params, **kwargs)
            count = result.rowcount
        except Exception as e:
            print(traceback.format_exc())
            self.sql_connector.get_session().rollback()
        else:
            self.sql_connector.get_session().commit()
        finally:
            self.sql_connector.session_close()
        return count
            
    def ExecuteDictSelect(self, statement, params=None, **kwargs):
        data = []
        try:
            results = self.sql_connector.execute_raw_sql(statement, params, **kwargs)
            data = [dict(row._mapping) for row in results]
        except Exception as e:
            print(traceback.format_exc())
        finally:
            self.sql_connector.session_close()
        return data
    

    def ExecuteSelect(self, statement, params=None, **kwargs):
        data = []
        try:
            result = self.sql_connector.execute_raw_sql(statement, params, **kwargs)
            data = result.fetchall()
        except Exception as e:
            print(traceback.format_exc())
        finally:
            self.sql_connector.session_close()
        return data
