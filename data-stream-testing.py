import numpy as np
import pandas as pd
from datetime import datetime
import random
import matplotlib.pyplot as plt


def data_stream_generator():
    while True:
        data = {
            'timestamp': datetime.now(),
            'value': random.random()
        }
        yield data


def process_data_stream(stream, max_data_points=1000):
    df = pd.DataFrame(columns=['timestamp', 'value'])
    print(df)
    for i, data in enumerate(stream):
        print(data)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        if i >= max_data_points - 1:
            break

    return df

def analyze_data(df):
    df['rolling_avg'] = df['value'].rolling(window=50).mean()
    return df


if __name__ == '__main__':
    stream = data_stream_generator()
    df_res = process_data_stream(stream)
    result_df = analyze_data(df_res)
    print(result_df)
    plt.plot(result_df['timestamp'], result_df['rolling_avg'])
    plt.xlabel('Timestamp')
    plt.ylabel('Rolling Average')
    plt.title('Data Stream Analysis')
    plt.show()