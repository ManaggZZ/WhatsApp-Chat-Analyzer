from collections import Counter
import pandas as pd
import emoji
from wordcloud import WordCloud
from urlextract import URLExtract
exctract = URLExtract()



def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # 1- fetch number of messages
    num_messages = df.shape[0]

    # 2- fetch number of words
    words = []
    for message in df['message']:
        words.extend(message.split(' ')) 
    
    # 3- fetch number of media files
    # num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    num_media_messages = df['message'].str.contains('media omitted', case=False, na=False).sum()    

    # 4- fetch number of links shared
    links = []
    for message in df['message']:
        found_links = exctract.find_urls(message)
        # Exclude links containing 'B.Tech' or 'M.Tech'
        filtered_links = [link for link in found_links if 'B.Tech' not in link and 'M.Tech' not in link]
        links.extend(filtered_links)

    return num_messages, len(words), num_media_messages, len(links)
    
    
def most_busy_users(df):
    # This is the top 5 users with the most messages
    df = df[df['user'] != 'Group Notification']
    x = df['user'].value_counts().head()

    # This gives the percentage of messages sent by each user
    new_df = round((df['user'].value_counts()/df.shape[0]) * 100, 2).reset_index().rename(columns={'index': 'Name', 'user': 'Percentage'})
    new_df['Percentage'] = [str(x) for x in new_df['Percentage']]
    # CHANGED HERE

    return x, new_df

def create_wordcloud(selected_user, df):

    # Remove rows where 'message' contains 'media omitted' (case-insensitive)
    df = df[~df['message'].str.contains('media omitted', case=False, na=False)]
    # df = df[~df['message'].str.contains('message deleted', case=False, na=False)]
    # df = df[~df['message'].str.contains('message edited', case=False, na=False)]

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # remove group notification in word cloud
    temp = df[df['user'] != 'Group Notification']

    # remove media omitted messages
    # temp = temp[temp['message'] != '<Media omitted>']

    f = open(r'stop_words.txt', 'r', encoding='utf-8')
    stopwords = f.read()

    def remove_stopwords(message):
        y = []
        for word in message.lower().split():
            if word not in stopwords:
                y.append(word)
        return " ".join(y)
    
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['message'] = temp['message'].apply(remove_stopwords)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # remove group notification in top 10 msg
    temp = df[df['user'] != 'Group Notification']

    # remove media omitted messages
    temp = temp[temp['message'] != '<Media omitted>']

    # remove stop words
    # from nltk.corpus import stopwords (we can also use this)
    f = open(r'stop_words.txt', 'r', encoding='utf-8')
    stopwords = f.read()

    words = []
    for message in temp['message']:
        for word in message.lower().split():  # split the message into words
            if word not in stopwords and word != '<media' and word != 'omitted>revised' and word != 'omitted>':
                words.append(word)  # add list into words list
    
    counter = Counter(words)
    df_counter = pd.DataFrame(counter.most_common(20))
    df_counter.index = df_counter.index + 1  # Start index from 1
    return df_counter.rename(columns={0: 'Word', 1: 'Count'})

def emoji_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emoji_list = []
    for message in df['message']:
        for char in message:
            if char in emoji.EMOJI_DATA:
                emoji_list.append(char)
    
    emoji_df = pd.DataFrame(Counter(emoji_list).most_common(len(Counter(emoji_list))))
    emoji_df[1] = [str(x) for x in emoji_df[1]]
    return emoji_df.rename(columns={0: 'Emoji', 1: 'Count'})

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    timeline = df.groupby(['Year', 'Month_num', 'Month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['Month'][i] + "-" + str(timeline['Year'][i]))

    timeline['time'] = time
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    daily_timeline = df.groupby('Only_date').count()['message'].reset_index()
    
    return daily_timeline

def weekly_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    return df['Day_name'].value_counts()

def monthly_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    return df['Month'].value_counts()

# Heatmap

def get_period(hour):
    if hour == 23:
        return f"{hour}-00"
    elif hour == 0:
        return "00-1"
    else:
        return f"{hour}-{hour+1}"


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    df['period'] = df['Hour'].apply(get_period)
    period_order = [f"{i}-{(i+1)%24}" for i in range(24)]
    activity_table = df.pivot_table(
            index='Day_name',
            columns='period',
            values='message',
            aggfunc='count'
        ).reindex(columns=period_order).fillna(0)
    
    return activity_table