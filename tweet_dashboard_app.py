import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# Application Titles and Description
st.title("Sentiment Analysis of Tweets about US Airlines")
st.sidebar.title("Sentiment Analysis of Tweets about US Airlines")

st.markdown("This application is a Streamlit dashboard to analyze the sentiment of Tweets")
st.sidebar.markdown("This application is a Streamlit dashboard to analyze the sentiment of Tweets")

# Loading Data
data_url = ("Tweets.csv") # Points the CSV file in the same directory as the script


# Caches the result using the new st.cache_data decorator
@st.cache_data(persist=True)

# load_data function
# Reads the CSV file
# Converts the tweet_created column to datetime
def load_data():
    data = pd.read_csv(data_url)
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data

# Holds the DataFrame loaded by the function
data = load_data()

# =================================
# Random Tweet Display
# =================================

# Displays a sidebar subheader
st.sidebar.subheader("Show random tweet")

# Provides a radio button for selecting a sentiment('positive', 'neutral', 'negative')
random_tweet = st.sidebar.radio('Sentiment', ('positive', 'neutral', 'negative'))

# Uses query and sample to pick a random tweet that matches the selected sentiment and displays its text
st.sidebar.markdown(data.query('airline_sentiment == @random_tweet')[['text']].sample(n=1).iat[0,0])

# =================================
# Tweets by Sentiment Visualization
# =================================

st.sidebar.markdown('### Number of tweets by sentiment')

# A select box allows the user to choose between a histogram or pie chart
select = st.sidebar.selectbox('Visualization type', ['Histogram', 'Pie chart'], key='1')

# Calculates tweet counts per sentiment
sentiment_count = data['airline_sentiment'].value_counts()
# The counts are converted into a DataFrame
sentiment_count = pd.DataFrame({'Sentiment': sentiment_count.index, 'Tweets': sentiment_count.values})

# If user unchecks the "Hide" checkbox, it displays the chosen chart (using Plotly Express) on the main page 
if not st.sidebar.checkbox("Hide", True):
    st.markdown("### Number of tweets by sentiment")
    if select == 'Histogram':
        fig = px.bar(sentiment_count, x='Sentiment', y='Tweets', color='Sentiment', height=500)
        st.plotly_chart(fig)
    else:
        fig = px.pie(sentiment_count, values='Tweets', names='Sentiment')
        st.plotly_chart(fig)

# =================================
# Tweet Location Mapping by Time
# =================================

st.sidebar.subheader("When and where are user tweeting from?")

# Time Filtering
# A slider lets the user pick an hour (0-23)
# The data is filtered to tweets created in that hour
hour = st.sidebar.slider("Hour of day", 0, 23)
modified_data = data[data['tweet_created'].dt.hour == hour]

# Display
# If not hidden, shows the count of tweets and displays their locations on a map
# Optionally, raw data can be shown
if not st.sidebar.checkbox("Hide", True, key='2'):
    st.markdown('### Tweets locations based on the time of day')
    st.markdown('%i tweets between %i:00 and %i:00' % (len(modified_data), hour, (hour+1)%24))
    st.map(modified_data)

    if st.sidebar.checkbox('Show raw data', False):
        st.write(modified_data)

# ========================================
# Breakdown of Airline Tweets by Sentiment
# ========================================

st.sidebar.subheader("Breakdown of Airline Tweets by Sentiment")

# Airline Selection
# A multiselect widget lets user choose one or more airlines
# Data is filtered to only include the selected airlines
# A histogram is created with facets based on sentiment, showing the breakdown for each airline
choice = st.sidebar.multiselect('Pick airlines', ('US Airways', 'United', 'American', 'Southwest', 'Delta', 'Virgin America'), key='0')

if len(choice) > 0:
    choice_data = data[data.airline.isin(choice)]
    fig_choice = px.histogram(choice_data, x='airline', y='airline_sentiment', histfunc='count', color='airline_sentiment',
    facet_col='airline_sentiment', labels={'airline_sentiment':'tweets'}, height=600, width=800)
    st.plotly_chart(fig_choice)

# =====================
# Word Cloud Generation
# =====================

st.sidebar.header("Word Cloud")

# A radio button selects which sentiment's tweets to display
# The data is filtered for the chosen sentiment
# All tweet texts are joined into a single string
# Unwanted tokens (URLs, mentions, retweet markers) are removed
# A WordCloud is generated from the processed text
word_sentiment = st.sidebar.radio('Display word cloud for what sentiment?', ('positive', 'neutral', 'negative'))

if not st.sidebar.checkbox('Hide', True, key='3'):
    st.header('word cloud for %s sentiment' % (word_sentiment))
    df = data[data['airline_sentiment']==word_sentiment]
    words = ' '.join(df['text'])
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', height=640, width=800).generate(processed_words)
    
    

    fig, ax = plt.subplots()
    ax.imshow(wordcloud)
    ax.set_xticks([])
    ax.set_yticks([])
    st.pyplot(fig)

#    plt.imshow(wordcloud)
#    plt.xticks([])
#    plt.yticks([])
#    st.pyplot()
