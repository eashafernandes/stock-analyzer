import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import os
from config import PY_DATE_FORMAT,DATE_FORMAT
from dbengine import saveToDB, connect
from applogger import logger
import json
import traceback
import pandas as pd
import seaborn as sns

def process_message(ch, method, properties, body):
    try:
        print(f"Correlation Analysis - Received message: {body.decode('utf-8')}")
        data = json.loads(body.decode('utf-8'))
        ticker_symbols = data.get("ticker")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        ystart = datetime.datetime.strptime(start_date, PY_DATE_FORMAT).strftime('%Y-%m-%d')
        yend = datetime.datetime.strptime(end_date, PY_DATE_FORMAT).strftime('%Y-%m-%d')
        # Fetch historical data
        ticker_data_obj = {ticker: yf.download(ticker, start='2023-01-01', end='2023-12-31')['Adj Close'] for ticker in ticker_symbols}

        # Create DataFrame from ticker_data
        ticker_data = pd.DataFrame(ticker_data_obj)
        #Make proper case
        ticker_data.columns = ticker_data.columns.str.strip('"').str.replace(' ', '_').str.lower()
        # Save Dataframe to DB
        ticker_list = "','".join(ticker_symbols)
        del_qry = ""
        #del_qry = f"delete from ticker_data where many_ticker_data between to_date('{start_date}', '{DATE_FORMAT}') and to_date('{end_date}','{DATE_FORMAT}') and ticker_name in ('{ticker_list}')"
        saveToDB(connect,del_qry,ticker_data,"many_ticker_data")
        #Correlation
        correlation_matrix = ticker_data.corr()
        # Stack the correlation matrix to get pairs of symbols and their correlations
        stacked_corr = correlation_matrix.stack().reset_index()

        # Rename columns for clarity
        stacked_corr.columns = ['ticker_1', 'ticker_2', 'correlation']

        # Create a mask to exclude self-correlations (diagonal) and duplicates
        mask = stacked_corr['ticker_1'] < stacked_corr['ticker_2']

        # Apply the mask to get the final DataFrame of symbol pairs and correlations
        correlation_df = stacked_corr[mask]

        # Reset index for a clean DataFrame if needed
        correlation_df = correlation_df.reset_index(drop=True, inplace=True)
        ###
        plots = visualizer(ticker_data)
        if plots['status'] == 'unsuccess':
            return plots
        path = plots['path']
        ticker_data['path'] = path
        del_qry = f"delete from ticker_data_correlation where ticker_date between to_date('{start_date}', '{DATE_FORMAT}') and to_date('{end_date}','{DATE_FORMAT}') and ticker_name in ('{ticker_list}')"
        saveToDB(connect,del_qry,ticker_data,"ticker_data_correlation")
        return {"status":"success"}
    except Exception as e:
        logger.critical(traceback.format_exc())
        return {"status":"unsuccess"}

def visualizer(correlation_matrix):
    try:
        # Plot correlation matrix as heatmap
        plt.figure(figsize=(10, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title('Correlation Matrix of Ticker Data')
        # Create a directory 'plots' in the current directory if it doesn't exist
        output_dir = os.path.abspath(os.path.join(os.getcwd(),'plots'))
        os.makedirs(output_dir, exist_ok=True)

        current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Save plot to a file in the 'plots' directory (e.g., PNG format)
        plot_filename = os.path.join(output_dir, f"correlation_analysis_{current_datetime}.png")
        plt.savefig(plot_filename)
        return {"status":"success", "path":plot_filename}
    except Exception as e:
        logger.critical(traceback.format_exc())
        err = str(e.args[0]).replace("'","`").replace('"',"`")
        return {"status":"unsuccess", "path":"", "error":err}



