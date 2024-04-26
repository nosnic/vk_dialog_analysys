from datetime import datetime, timedelta

import vk_api
import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objs as go
from nltk.corpus import stopwords
from statsmodels.tsa.seasonal import seasonal_decompose

from collections import Counter
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image  # Load images from files
import numpy as np


class VkDialogAnalyzer:
    def __init__(self, token):
        self.messages_amount_df = None
        self.your_name = 'Kent_You'
        self.companion_name = 'Kent_NOT_You'
        self.dialog = None
        self.token = token
        self.vk_session = vk_api.VkApi(token=self.token).get_api()
        self.messages = None
        self.friend_list = self.vk_session.friends.get(order='hints')['items']
        self.test = 0
        self.dataframe = None

    def download_vk_dialog(self, friend_id):
        try:
            messages = self.vk_session.messages.getHistory(user_id=friend_id, count=200)
            all_messages = messages['items']
            while messages['count'] > len(all_messages):
                messages = (self.vk_session.
                            messages.getHistory(user_id=friend_id, count=200, offset=len(all_messages)))
                all_messages.extend(messages['items'])
                self.test = round(len(all_messages) / messages['count'], 2)
                print(round(len(all_messages) / messages['count'], 2))
                self.dialog = all_messages
        except vk_api.VkApiError as error_msg:
            print(error_msg)

    def create_dataframe(self):
        data = pd.DataFrame(self.dialog)
        data['date'] = (data['date']
                        .apply(lambda x: datetime.fromtimestamp(x).strftime('%d.%m.%Y %H:%M:%S')))
        data['date'] = pd.to_datetime(data['date'], format='%d.%m.%Y %H:%M:%S')
        data = data.set_index('date')
        data = data.sort_index(ascending=False)
        data['out'] = data['out'].replace({1: self.your_name, 0: self.companion_name})
        self.dataframe = data
        self.messages = data[['out', 'text']]
        self.messages_amount_df = self.messages.drop(['text', 'out'], axis=1)
        self.messages_amount_df['count'] = 1
        self.messages.loc[:, 'word_count'] = self.messages['text'].apply(lambda x: len(x.split()))
        self.messages.loc[:, 'time_diff'] = ((self.messages.index.to_series().shift(1) - self.messages.index)
                                             .fillna(pd.Timedelta(seconds=0)))

    def get_messages_amount(self):
        return self.messages.shape[0]

    def get_messages_amount_split(self):
        return self.messages['out'].value_counts()

    def get_date_of_first_message(self):
        return self.messages.index[-1]

    def get_amount_of_talking_days_yearly(self):
        messages_amount_df = self.messages_amount_df.resample('D').sum()
        messages_amount_df['year'] = messages_amount_df.index.year
        messages_amount_year_df = (
            messages_amount_df[messages_amount_df['count'] > 0].groupby('year')['count'].count().reset_index())
        return messages_amount_year_df

    def get_word_count_mean(self):
        return round(self.messages['word_count'].mean(), 2)

    def get_word_count_mean_by_person(self):
        return self.messages.groupby('out')['word_count'].mean()

    def get_amount_of_started_conversations(self, offset):
        self.messages.loc[:, 'start_conversation'] = (self.messages['time_diff'] > pd.Timedelta(hours=offset))
        conversation_starts = self.messages.groupby('out')['start_conversation'].sum()
        return conversation_starts

    def create_seasoning_with_tolling_mean(self, window_size=7):
        messages_amount_df = self.messages_amount_df.resample('D').sum()

        trace1 = go.Scatter(x=messages_amount_df.index, y=messages_amount_df['count'], mode='lines', name='Значения')
        rolling_mean = messages_amount_df['count'].rolling(window=window_size).mean()
        trace2 = go.Scatter(x=messages_amount_df.index, y=rolling_mean, mode='lines',
                            name=f'{window_size}-дневное скользящее среднее', line=dict(color='red'))
        data = [trace1, trace2]

        layout = go.Layout(title='Количество сообщений по дням',
                           xaxis=dict(title='Дата'),
                           yaxis=dict(title='Количество сообщений'),
                           hovermode='closest',
                           height=700,
                           width=1100)
        fig = go.Figure(data=data, layout=layout)
        return fig

    def create_seasoning_hour(self):
        decomposed = seasonal_decompose(self.messages_amount_df.resample('h').sum())
        trace_seasonal = go.Scatter(x=decomposed.seasonal.index[:70], y=decomposed.seasonal.iloc[:70], mode='lines',
                                    name='Сезонность по часам')

        layout = go.Layout(title='Сезонность по часам',
                           xaxis=dict(title='Дата'),
                           height=700,
                           width=1000)
        layout['xaxis']['tickformat'] = '%H:%M'
        fig = go.Figure(data=[trace_seasonal], layout=layout)
        return fig

    def create_seasoning_day(self):
        decomposed = seasonal_decompose(self.messages_amount_df.resample('D').sum())
        trace_seasonal = go.Scatter(x=decomposed.seasonal.index[:21], y=decomposed.seasonal.iloc[:21], mode='lines',
                                    name='Сезонность по дням недели')

        layout = go.Layout(title='Сезонность по дням недели',
                           xaxis=dict(title='Дата'),
                           height=700,
                           width=1000)
        layout['xaxis']['tickformat'] = '%A'
        fig = go.Figure(data=[trace_seasonal], layout=layout)
        return fig

    def create_seasoning_month(self):
        decomposed = seasonal_decompose(self.messages_amount_df.resample('ME').sum())
        x_values = [date + timedelta(days=1) for date in decomposed.seasonal.index[-12:]]

        trace_seasonal = go.Scatter(x=x_values, y=decomposed.seasonal.iloc[-12:], mode='lines',
                                    name='Сезонность по месяцам')

        layout = go.Layout(title='Сезонность по месяцам',
                           xaxis=dict(title='Дата'),
                           height=700,
                           width=1000)
        layout['xaxis']['tickformat'] = '%B'
        fig = go.Figure(data=[trace_seasonal], layout=layout)
        return fig

    @staticmethod
    def str_corpus(corpus):
        str_corpus = ''
        for i in corpus:
            str_corpus += ' ' + i
        str_corpus = str_corpus.strip()
        return str_corpus

    def create_wordcloud(self, mode='general'):
        if mode == 'general':
            text = self.str_corpus(self.messages['text'])
        elif mode == 'only_you':
            text = self.str_corpus(self.messages['text'][self.messages['out'] == self.your_name])
        elif mode == 'only_kent':
            text = self.str_corpus(self.messages['text'][self.messages['out'] == self.companion_name])
        else:
            text = 'Гойда'
        stop_words_set = set(stopwords.words('russian'))
        fog_machine = WordCloud(stopwords=stop_words_set,
                                width=800,
                                height=600,
                                min_font_size=14,
                                background_color="#333333",
                                colormap="spring")
        fog_machine.generate(text)
        return fog_machine.to_image()

