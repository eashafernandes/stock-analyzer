from sqlalchemy import create_engine, types, FLOAT
from applogger import logger
import traceback
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import sessionmaker



def initDB(data, date_format):
    try:
        global connect 
        engine_str = getDBDetails(data)
        if engine_str == None:
            raise Exception('Something went wrong, Please Check DB Details.')
        connect = create_engine(engine_str)
        with connect.connect() as con:
            con.execute(text(f"Alter session set nls_date_format='{date_format}'"))
            con.close()
        print("Database Initialized")
        return True
    except Exception as e:
        logger.critical(traceback.format_exc())
        return False


def getDBDetails(data):
    try:
        # Only string or None will be returned. String: Success || None: Db Details wrong.
        username = data.get('username')
        password = data.get('password')
        host = data.get('host')
        port = data.get('port')
        sid = data.get('sid')
        if username is None or username is None or username is None or username is None or username is None:
            return None
        engine_str = 'oracle+oracledb://{}:{}@{}:{}/?service_name={}'.format(username, password, host, port, sid,fast_executemany=True)
        return engine_str
    except Exception:
        logger.critical(traceback.format_exc())
        return None
    
def saveToDB(connect, stmt, pd_df, tablename):
    try:
        print(stmt)
        if stmt != "":
            print(stmt)
            with connect.connect() as con:
                con.execute(text(stmt))
                con.execute(text("commit"))
                con.close()
        dtyp = {}
        logger.info(pd_df.columns)
        for column in pd_df.columns:
            if pd_df[column].dtype == 'object':
                dtyp[column] = types.VARCHAR(pd_df[column].astype(str).str.len().max())
            elif pd_df[column].dtype in ['float', 'float64']:
                dtyp[column] = FLOAT
        pd_df.to_sql(tablename, con=connect, if_exists='append', index=False, dtype=dtyp)
        return {'status':'success', 'message':'Data Inserted Successfully.'}
    except Exception as e:
        logger.critical(traceback.format_exc())
        return {'status':'unsuccess', 'error':str(e.args[0])}
    

def runQuery(connect, qry):
    try:
        with connect.connect() as con:
            con.execute(text(qry))
            con.execute(text("commit"))
            con.close()
        return {'status':'success', 'message':'Query run successful.'}
    except Exception as e:
        logger.critical(traceback.format_exc())
        return {'status':'unsuccess', 'error':str(e.args[0])}
