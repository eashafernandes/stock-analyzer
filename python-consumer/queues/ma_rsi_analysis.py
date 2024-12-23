import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import os
from config import PY_DATE_FORMAT,DATE_FORMAT
from dbengine import saveToDB, connect
from applogger import logger
import json
import ta
import traceback

def process_message(ch, method, properties, body):
    try:
        print(f"Moving Average and Relative Strength Index- Received message: {body.decode('utf-8')}")
        data = json.loads(body.decode('utf-8'))
        ticker_name = data.get("ticker")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        ystart = datetime.datetime.strptime(start_date, PY_DATE_FORMAT).strftime('%Y-%m-%d')
        yend = datetime.datetime.strptime(end_date, PY_DATE_FORMAT).strftime('%Y-%m-%d')
        # Fetch historical data
        ticker_data = yf.download(ticker_name, start=ystart, end=yend)
        #Make proper case
        ticker_data.columns = ticker_data.columns.str.strip('"').str.replace(' ', '_').str.lower()
        # Convert index to datetime with proper format
        ticker_data.index = ticker_data.index.strftime(PY_DATE_FORMAT)
        ticker_data['ticker_date'] = ticker_data.index
        ticker_data['ticker_name'] = ticker_name
        ticker_data['startdate'] = start_date
        ticker_data['enddate'] = end_date
        # Save Dataframe to DB
        del_qry = f"delete from ticker_data where ticker_date between to_date('{start_date}', {DATE_FORMAT}) and to_date('{end_date}',{DATE_FORMAT}) and ticker_name = '{ticker_name}'"
        saveToDB(connect,del_qry,ticker_data,"ticker_data")
        #Start Moving Average
        sdate = datetime.datetime.strptime(start_date, PY_DATE_FORMAT).date()
        edate = datetime.datetime.strptime(end_date, PY_DATE_FORMAT).date()
        window = int((edate - sdate).days) - 1
        print(window)
        ticker_data['window'] = window
        ticker_data['moving_average'] = ticker_data['close'].rolling(window=window, min_periods=1).mean()
        #Start RSI
        ticker_data['rsi'] = ta.momentum.rsi(ticker_data['close'], window=14)
        ticker_data = ticker_data.fillna(value=0)
        plots = visualizer(ticker_data,window,ticker_name)
        if plots['status'] == 'unsuccess':
            return plots
        path = plots['path']
        ticker_data['path'] = path
        del_qry = f"delete from ticker_data_analysis_ma_rsi where ticker_date between to_date('{start_date}', {DATE_FORMAT}) and to_date('{end_date}',{DATE_FORMAT}) and ticker_name = '{ticker_name}'"
        saveToDB(connect,del_qry,ticker_data,"ticker_data_analysis_ma_rsi")
        return {"status":"success"}
    except Exception as e:
        logger.critical(traceback.format_exc())
        return {"status":"unsuccess"}

def visualizer(ticker_data,window,ticker_symbol):
    try:
        # Plotting
        plt.figure(figsize=(14, 7))

        # Plot Close price
        plt.subplot(2, 1, 1)  # Two rows, one column, first subplot
        plt.plot(ticker_data.index, ticker_data['close'], label='Close Price', color='blue')
        plt.plot(ticker_data.index, ticker_data['moving_average'], label=f"Moving Average - {window}", color='orange')
        plt.title(f'{ticker_symbol} Close Price and Moving Averages')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()

        # Plot RSI
        plt.subplot(2, 1, 2)  # Two rows, one column, second subplot
        plt.plot(ticker_data.index, ticker_data['rsi'], label='RSI', color='purple')
        plt.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
        plt.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
        plt.title(f'{ticker_symbol} Relative Strength Index (RSI)')
        plt.xlabel('Date')
        plt.ylabel('RSI')
        plt.legend()

        # Adjust layout
        plt.tight_layout()
        # Create a directory 'plots' in the current directory if it doesn't exist
        output_dir = os.path.abspath(os.path.join(os.getcwd(),'plots'))
        os.makedirs(output_dir, exist_ok=True)

        current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Save plot to a file in the 'plots' directory (e.g., PNG format)
        plot_filename = os.path.join(output_dir, f"ticker_analysis_{current_datetime}.png")
        plt.savefig(plot_filename)
        return {"status":"success", "path":plot_filename}
    except Exception as e:
        logger.critical(traceback.format_exc())
        err = str(e.args[0]).replace("'","`").replace('"',"`")
        return {"status":"unsuccess", "path":"", "error":err}

