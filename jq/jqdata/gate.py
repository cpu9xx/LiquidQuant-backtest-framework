import pandas as pd
import os
from sqlalchemy import create_engine, text, types
from sqlalchemy.orm import sessionmaker
import multiprocessing


class MySQL_gate():
    def __init__(self, start_date=None, end_date=None, **kwargs):
        self.start_date = start_date
        self.end_date = end_date
        self.db_config = kwargs
        self.StockSession = None
        self.IndexSession = None

    def init_session(self, db):
        stock_engine = create_engine(f"mysql+mysqldb://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}/stock", pool_size=5)
        index_engine = create_engine(f"mysql+mysqldb://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}/index", pool_size=5)
        self.StockSession = sessionmaker(bind=stock_engine)
        self.IndexSession = sessionmaker(bind=index_engine)
        current_process = multiprocessing.current_process()
        print(f"{current_process.name} init_session db: {db}")
        return self.get_session(db)
        
    def get_session(self, db):
        try:
            if db == 'stock':
                if self.StockSession is not None:
                    return self.StockSession()
                else:
                    return self.init_session(db)
            elif db == 'index':
                if self.IndexSession is not None:
                    return self.IndexSession()
                else:
                    return self.init_session(db)
            else:
                print(f"Error get_session with (db: {db})")
                return None
        except Exception as e:
            print(f"Error get_session ('{db}'): {e}")
            return self.init_session(db)

    def get_tables(self, db='stock'):
        query = f"SHOW TABLES;"
        df = self.execute_query(query, db, commit=False)
        return df

    def read_data_date(self, tablename, db='stock', days=1):
        query = f"SELECT * FROM `{tablename}` ORDER BY trade_date DESC LIMIT {days}"
        df = self.execute_query(query, db, commit=False)
        return df
    
    def read_df(self, tablename, db='stock'):
        query = f"SELECT * FROM `{tablename}` WHERE trade_date >= '{self.start_date}' AND trade_date <= '{self.end_date}';"
        df = self.execute_query(query, db, commit=False)
        return df

    def execute_query(self, query, db, commit=False):
        session = self.get_session(db)

        try:
            result = session.execute(text(query))
            if commit:
                session.commit()
            if result.returns_rows:
                df = pd.DataFrame(result.fetchall())
                return df
            else:
                return result.rowcount
        except Exception as e:
            session.rollback()
            print(f"Error executing query('{query}'): {e}")
            return None
        finally:
            session.close()
        