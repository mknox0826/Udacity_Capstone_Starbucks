import pandas as pd
import numpy as np
import math
import json
import matplotlib.pyplot as plt


from sklearn.preprocessing import MultiLabelBinarizer
import seaborn as sns
import matplotlib.pyplot as plt
import datetime



def clean_portfolio(portfolio):
    '''
    cleaning the portfolio dataframe 

    INPUT:
    portfolio - the original dataframe to be cleaned

    OUTPUT:
    cleaned_portfolio - the cleaned dataframe
    '''
    cleaned_portfolio = portfolio.copy()
    
    # create binary channels
    # https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html#sklearn.preprocessing.OneHotEncoder
    # https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MultiLabelBinarizer.html
    mlb = MultiLabelBinarizer()
    binary_channels = pd.DataFrame(mlb.fit_transform(portfolio['channels']), columns=mlb.classes_, index=portfolio.index)
   
    # create binary offer types
    binary_offer_types = portfolio['offer_type'].str.get_dummies()

    # concat
    cleaned_portfolio = pd.concat([cleaned_portfolio, binary_channels], axis=1)
    cleaned_portfolio = pd.concat([cleaned_portfolio, binary_offer_types], axis=1)
    
    # drop
    cleaned_portfolio.drop(['channels'], axis=1, inplace=True)

    # change duration to hours to match transactions df
    cleaned_portfolio['duration'] = cleaned_portfolio['duration'] * 24
    
    # rename id column
    cleaned_portfolio.rename(columns={"id": "offer_id"}, inplace=True)

    # rename offer_ids for easier visualiztion, reflecting offer type
    cleaned_portfolio.replace({'offer_id' : {'^a.+0ddfd$' : 'B1', '^4.+e8da0$' : 'B2', '^3.+a8bed$' : 'I1', '^9.+9e6d9$' : 'B3',
                                             '^0.+2e1d7$' : 'D1', '^2.+fb8c2$' : 'D2','^f.+fc2a4$' : 'D3', '^5.+b9837$' : 'I2', 
                                             '^f.+0e20d$' : 'B4', '^2.+daaa5$' : 'D4'}}, regex=True, inplace=True)

    return cleaned_portfolio




def clean_profile(profile):
    '''
    cleaning the profile dataframe

    INPUT:
    profile - the original dataframe to be cleaned

    OUTPUT:
    cleaned_profile - the cleaned dataframe
    '''
    cleaned_profile = profile.copy()

    # drop null (null age is encoded as 118)
    cleaned_profile.drop(cleaned_profile[cleaned_profile.age > 100].index, inplace = True)

    # create binary columns for each gender
    binary_genders = cleaned_profile['gender'].str.get_dummies()
    cleaned_profile = pd.concat([cleaned_profile, binary_genders], axis=1)
    
    # standardize date variable and convert to the number of days a customer has been a member, "member_days"
    cleaned_profile['became_member_on'] = pd.to_datetime(cleaned_profile['became_member_on'], format='%Y%m%d')
    cleaned_profile['member_days'] = datetime.datetime.today().date() - pd.to_datetime(cleaned_profile['became_member_on']).dt.date
    cleaned_profile['member_days'] = cleaned_profile['member_days'].dt.days

    # rename the id column
    cleaned_profile.rename(columns={"id": "customer_id"}, inplace=True)

    return cleaned_profile





def clean_transcript(transcript):
    '''
    cleaning the transcript dataframe

    INPUT:
    transcript - the original dataframe to be cleaned

    OUTPUT:
    offers - the cleaned dataframe when 'event' is offer_received, _viewed, _completed
    transactions - the cleaned dataframe when 'event' is a transaction
    '''
    cleaned_transcript = transcript.copy()

    # rename columns 
    cleaned_transcript.rename(columns={"person": "customer_id","time": "hours"}, inplace=True)

    # dummy the offer events
    binary_events = cleaned_transcript['event'].str.get_dummies()
    cleaned_transcript = pd.concat([cleaned_transcript, binary_events], axis=1)
    cleaned_transcript.rename(columns={"offer received": "offer_received", "offer viewed": "offer_viewed","offer completed": "offer_completed"}, inplace=True)

    # separate transactions: https://sparkbyexamples.com/pandas/pandas-drop-rows-with-condition/
    transactions = cleaned_transcript.query("event == 'transaction'").copy()
    transactions.drop(['offer_completed','offer_received','offer_viewed'], axis=1, inplace=True)

    # extract the transaction amount from the value column
    # The value column is a dictionary of strings, so that means I need to access the value of a key:value pair of the dictionary, 
    # which is within a list for each row in the column. 
    # I can achieve this using a lambda function (https://stackoverflow.com/questions/37500623/accessing-values-of-a-dictionary-in-a-list-using-lambda)
    #(https://www.programiz.com/python-programming/methods/dictionary/values) 
    #(https://www.geeksforgeeks.org/applying-lambda-functions-to-pandas-dataframe/)
    transactions['amount'] = transactions['value'].apply(lambda x: list(x.values())[0])
    transactions.drop(['value','event','transaction'], axis=1, inplace=True)

    # separate the offer events
    offers = cleaned_transcript.query("event != 'transaction'").copy()

    # extract the offer_id from the value column 
    offers['offer_id'] = offers['value'].apply(lambda x: list(x.values())[0])
    offers.drop(['value'], axis=1, inplace=True)

     # reorder the columns of the offer df
    offers = offers[['customer_id', 'offer_id', 'event', 'hours', 'offer_received', 'offer_viewed', 'offer_completed']]

    # change offer_ids for easier visualization, reflecting offer type
    offers.replace({'offer_id' : {'^a.+0ddfd$' : 'B1', '^4.+e8da0$' : 'B2', '^3.+a8bed$' : 'I1', '^9.+9e6d9$' : 'B3',
                                             '^0.+2e1d7$' : 'D1', '^2.+fb8c2$' : 'D2','^f.+fc2a4$' : 'D3', '^5.+b9837$' : 'I2', 
                                             '^f.+0e20d$' : 'B4', '^2.+daaa5$' : 'D4'}}, regex=True, inplace=True)
    
    return offers, transactions



