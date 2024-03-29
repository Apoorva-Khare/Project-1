#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from googleapiclient.discovery import build
import pymongo
import mysql.connector
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

from PIL import Image



#API Key connection

def Api_connect():
    
    api_service_name = "youtube"
    api_version = "v3"
    
    api_key = 'AIzaSyA89s1ztiZrHBihlyCcOQSyXM0UGRieEG4'
    
    youtube = build(api_service_name, api_version, developerKey=api_key)
    
    return youtube

youtube=Api_connect()


#get channel information
def get_channel_info(channel_id):
    
    request = youtube.channels().list(
                part = "snippet,contentDetails,Statistics",
                id = channel_id)
            
    response1=request.execute()

    for i in range(0,len(response1["items"])):
        data = dict(
                    Channel_Name = response1["items"][i]["snippet"]["title"],
                    Channel_Id = response1["items"][i]["id"],
                    Subscription_Count= response1["items"][i]["statistics"]["subscriberCount"],
                    Views = response1["items"][i]["statistics"]["viewCount"],
                    Total_Videos = response1["items"][i]["statistics"]["videoCount"],
                    Channel_Description = response1["items"][i]["snippet"]["description"],
                    Channel_pubAt =response1["items"][i]['snippet']['publishedAt'],
                    Playlist_Id = response1["items"][i]["contentDetails"]["relatedPlaylists"]["uploads"],
                    )
        return data

#to get videoids of a channel
def get_channel_videos(channel_id):
    video_ids = []
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id, 
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    
    while True:
        res = youtube.playlistItems().list( 
                                           part = 'snippet',
                                           playlistId = playlist_id, 
                                           maxResults = 50,
                                           pageToken = next_page_token).execute()
        
        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
    return video_ids



#get video details using video_ids
def get_video_info(video_ids):
    
    video_data = []
    def time_duration(t):
            a = pd.Timedelta(t)
            b = str(a).split()[-1]
            return b

    for video_id in video_ids:
        request = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id= video_id)
        response = request.execute()

        for item in response["items"]:
            data = dict(Channel_Name = item['snippet']['channelTitle'],
                        Channel_Id = item['snippet']['channelId'],
                        Video_Id = item['id'],
                        Title = item['snippet']['title'],
                        Tags = ",".join(item['snippet'].get('tags',["NA"])),
                        Thumbnail = item['snippet']['thumbnails']['default']['url'],
                        Description = item['snippet']['description'],
                        Published_Date = item['snippet']['publishedAt'],
                        Duration =time_duration(item['contentDetails']['duration']),
                        Views = item['statistics']['viewCount'],
                        Likes = item['statistics'].get('likeCount'),
                        Comments = item['statistics'].get('commentCount'),
                        Favorite_Count = item['statistics']['favoriteCount'],
                        )
            video_data.append(data)
    return video_data



#get comment information
def get_comment_info(video_ids):
        Comment_Information = []
        try:
                for video_id in video_ids:

                        request = youtube.commentThreads().list(
                                part = "snippet",
                                videoId = video_id,
                                maxResults = 50
                                )
                        response5 = request.execute()
                        
                        for item in response5["items"]:
                                comment_information = dict(
                                        Comment_Id = item["snippet"]["topLevelComment"]["id"],
                                        Video_Id = item["snippet"]["videoId"],
                                        Comment_Text = item["snippet"]["topLevelComment"]["snippet"]["textOriginal"],
                                        Comment_Author = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                                        Comment_Published = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"])

                                Comment_Information.append(comment_information)
        except:
                pass
                
        return Comment_Information


#MongoDB Connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Youtube_Data"]  



def channel_details(channel_id):
    ch_details = get_channel_info(channel_id)
    vi_ids = get_channel_videos(channel_id)
    vi_details = get_video_info(vi_ids)
    com_details = get_comment_info(vi_ids)

    coll1 = db["channel_details"]
    coll1.insert_one({"channel_information":ch_details,
                      "video_information":vi_details,
                     "comment_information":com_details})
    
    return "Upload to MongoDB successful"


#function to create and insert channels table in mysql
def channels_table():
    
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="1234",
      database="youtube_data_harvesting"
    )
    cursor=mydb.cursor()

    drop_query = "drop table if exists channels"
    cursor.execute(drop_query)
    mydb.commit()

    try:
        create_query = '''create table if not exists channels(Channel_Name varchar(100),
                        Channel_Id varchar(80) primary key, 
                        Subscription_Count bigint, 
                        Views bigint,
                        Total_Videos int,
                        Channel_Description text,
                        Channel_pubAt varchar(80),
                        Playlist_Id varchar(50))'''
        cursor.execute(create_query)
        mydb.commit()
     
    except:
        st.write("Channels Table alredy created")

    ch_list = []
    db = client["Youtube_Data"]
    coll1 = db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    df = pd.DataFrame(ch_list)
    
    for index,row in df.iterrows():
        insert_query = '''insert into channels(Channel_Name,
                                                Channel_Id,
                                                Subscription_Count,
                                                Views,
                                                Total_Videos,
                                                Channel_Description,
                                                Channel_pubAt,
                                                Playlist_Id)
                                                    
                                                values(%s,%s,%s,%s,%s,%s,%s,%s)'''
            

        values =(row['Channel_Name'],
                row['Channel_Id'],
                row['Subscription_Count'],
                row['Views'],
                row['Total_Videos'],
                row['Channel_Description'],
                row['Channel_pubAt'],
                row['Playlist_Id'])
        
      
        try:
            cursor.execute(insert_query,values)
            mydb.commit()
        
        except:
            st.write("Channels values are already inserted")
            
            
#function to create and insert videos table in mysql
def videos_table():
    

    mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          password="1234",
          database="youtube_data_harvesting"
    )
    cursor=mydb.cursor()

    drop_query = "drop table if exists videos"
    cursor.execute(drop_query)
    mydb.commit()

    try:
        create_query = '''create table if not exists videos(
                        Channel_Name varchar(150),
                        Channel_Id varchar(100),
                        Video_Id varchar(50) primary key, 
                        Title varchar(150), 
                        Tags text,
                        Thumbnail varchar(225),
                        Description text, 
                        Published_Date varchar(80),
                        Duration time, 
                        Views bigint, 
                        Likes bigint,
                        Comments bigint,
                        Favorite_Count int 
                        )''' 

        cursor.execute(create_query)             
        mydb.commit()
    
    except:
        st.write("Videos Table alrady created")

    vi_list = []
    db = client["Youtube_Data"]
    coll1 = db["channel_details"]
    for vi_data in coll1.find({},{"_id":0,"video_information":1}):
        for i in range(len(vi_data["video_information"])):
            vi_list.append(vi_data["video_information"][i])
    df2 = pd.DataFrame(vi_list)
        
    
    for index, row in df2.iterrows():
        insert_query = '''
                    insert into videos(Channel_Name,
                        Channel_Id,
                        Video_Id, 
                        Title, 
                        Tags,
                        Thumbnail,
                        Description, 
                        Published_Date,
                        Duration, 
                        Views, 
                        Likes,
                        Comments,
                        Favorite_Count 
                        )
                        values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

                '''
        values = (
                    row['Channel_Name'],
                    row['Channel_Id'],
                    row['Video_Id'],
                    row['Title'],
                    row['Tags'],
                    row['Thumbnail'],
                    row['Description'],
                    row['Published_Date'],
                    row['Duration'],
                    row['Views'],
                    row['Likes'],
                    row['Comments'],
                    row['Favorite_Count']
                    )
        try:
            cursor.execute(insert_query,values)
            mydb.commit()
        except:
            st.write("videos values already inserted in the table")
            

#function to create and insert comments table in mysql
def comments_table():
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="1234",
      database="youtube_data_harvesting"
    )
    cursor=mydb.cursor()


    drop_query = "drop table if exists comments"
    cursor.execute(drop_query)
    mydb.commit()
    
    try:
   
        create_query = '''CREATE TABLE if not exists comments(Comment_Id varchar(100) primary key,
                       Video_Id varchar(80),
                       Comment_Text text, 
                       Comment_Author varchar(150),
                       Comment_Published varchar(80))'''
        cursor.execute(create_query)
        mydb.commit()
     
    except:
        st.write("Comments Table already created")
        
    
    com_list = []
    db = client["Youtube_Data"]
    coll1 = db["channel_details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    df3 = pd.DataFrame(com_list)


    for index, row in df3.iterrows():
        
        insert_query = '''insert into comments(Comment_Id,
                                  Video_Id ,
                                  Comment_Text,
                                  Comment_Author,
                                  Comment_Published)
                                  
                                 values(%s, %s, %s, %s, %s)'''
        
        values = (
            row['Comment_Id'],
            row['Video_Id'],
            row['Comment_Text'],
            row['Comment_Author'],
            row['Comment_Published']
        )
        try:
            
            cursor.execute(insert_query,values)
            mydb.commit()
        
        except:
               st.write("This comments are already exist in comments table")
        

# defined tables function to call channel,videos and comments table
def tables():
    channels_table()
    videos_table()
    comments_table()
    return "Data Migrated to MYSQL successfully"


# # display of all channels related data in streamlit


def show_channels_table():
    ch_list = []
    db = client["Youtube_Data"]
    coll1 = db["channel_details"] 
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    channels_table = st.dataframe(ch_list)
    return channels_table


def show_videos_table():
    vi_list = []
    db = client["Youtube_Data"]
    coll2 = db["channel_details"]
    for vi_data in coll2.find({},{"_id":0,"video_information":1}):
        for i in range(len(vi_data["video_information"])):
            vi_list.append(vi_data["video_information"][i])
    videos_table = st.dataframe(vi_list)
    return videos_table



def show_comments_table():
    com_list = []
    db = client["Youtube_Data"]
    coll3 = db["channel_details"]
    for com_data in coll3.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    comments_table = st.dataframe(com_list)
    return comments_table


# SETTING PAGE CONFIGURATIONS
icon=Image.open(r"C:\Users\Dell\JupyterPythoncodes\Youtube_logo.png")
st.set_page_config(page_title= "Welcome To My Streamlit Page | Apoorva Khare",
                   page_icon=icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About': """# This app is created by *Apoorva Khare!*"""})



with st.sidebar:
    st.title(":green[YOUTUBE DATA HARVESTING AND WAREHOUSING]")
    st.header("SKILL TAKE AWAY")
    st.caption(":blue[Python scripting]")
    st.caption(":blue[Data Collection]")
    st.caption(":blue[MongoDB]")
    st.caption(":blue[API Integration]")
    st.caption(":blue[Data Managment using MongoDB and SQL]")

head=st.header("WELCOME TO STREAMLIT PAGE | by Apoorva Khare")


selected = option_menu(
    menu_title = "YOUTUBE DATA HARVESTING AND WAREHOUSING",
    options = ["SELECT AND STORE", "MIGRATION OF DATA","CHANNELS DATA","DATA ANALYSIS"],
    menu_icon = "youtube",
    orientation = "horizontal"
)

# Storing data to MongoDB

if selected == "SELECT AND STORE":

    channel_id = st.text_input("**Enter a channel ID**")
    channels = channel_id.split(',')
    channels = [ch.strip() for ch in channels if ch]
    store_data = st.button("STORE DATA IN MONGODB")
    
    if store_data:
        for channel in channels:
            ch_ids = []
            db = client["Youtube_Data"]
            coll1 = db["channel_details"]
            for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
                ch_ids.append(ch_data["channel_information"]["Channel_Id"])
            if channel in ch_ids:
                st.success("Channel details of the given channel id: " + channel + " already exists")
            else:
                output = channel_details(channel)
                st.success(output)

        
# Migration of Data to MySQL
if selected == "MIGRATION OF DATA":
    
     # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["Youtube_Data"]
    coll1 = db["channel_details"]
    migrate = st.button("MIGRATE DATA TO MYSQL")
    if migrate:
        display = tables()
        st.success(display)
        
                     

# Display of channels,videos and comments table
if selected == "CHANNELS DATA":
    show_table = st.selectbox("SELECT THE TABLE FOR VIEW",("Select","Channels","Videos","Comments"))

    if show_table == "Channels":
        show_channels_table()
    elif show_table =="Videos":
        show_videos_table()
    elif show_table == "Comments":
        show_comments_table()
    
    
# Query Part

if selected == "DATA ANALYSIS":
    
    #SQL connection
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="youtube_data_harvesting"
    )
    cursor=mydb.cursor()

    st.write("## :orange[Select any question to get Insights]")
    question = st.selectbox(
            'Please Choose Your Question',
            ('Select',
             '1. Name of all the videos and the Channel Name',
             '2. Channels with most number of videos',
             '3. Which are the 10 most viewed videos',
             '4. Comments in each video',
             '5. Show Videos with highest likes',
             '6. Likes of all videos',
             '7. Views of each channel',
             '8. Videos published in the year 2022',
             '9. Average duration of all videos in each channel',
             '10. Videos with highest number of comments'))


    if question == '1. Name of all the videos and the Channel Name':
        query1 = "select Title as videos, Channel_Name as ChannelName from videos;"
        cursor.execute(query1)
        t1=cursor.fetchall()
        st.write(pd.DataFrame(t1, columns=["Video Title","Channel Name"]))

    elif question == '2. Channels with most number of videos':
        query2 = "select Channel_Name as ChannelName,Total_Videos as NO_Videos from channels order by Total_Videos desc;"
        cursor.execute(query2)
        t2=cursor.fetchall()
        st.write(pd.DataFrame(t2, columns=["Channel Name","No Of Videos"]))

    elif question == '3. Which are the 10 most viewed videos':
        query3 = '''select Views as views , Channel_Name as ChannelName,Title as VideoTitle from videos 
                            where Views is not null order by Views desc limit 10;'''
        cursor.execute(query3)
        t3 = cursor.fetchall()
        st.write(pd.DataFrame(t3, columns = ["views","channel Name","video title"]))

    elif question == '4. Comments in each video':
        query4 = "select Comments as No_comments ,Title as VideoTitle from videos where Comments is not null;"
        cursor.execute(query4)
        t4=cursor.fetchall()
        st.write(pd.DataFrame(t4, columns=["No Of Comments", "Video Title"]))

    elif question == '5. Show Videos with highest likes':
        query5 = '''select Title as VideoTitle, Channel_Name as ChannelName, Likes as LikesCount from videos 
                           where Likes is not null order by Likes desc;'''
        cursor.execute(query5)
        t5 = cursor.fetchall()
        st.write(pd.DataFrame(t5, columns=["video Title","channel Name","like count"]))

    elif question == '6. Likes of all videos':
        query6 = '''select Likes as likeCount,Title as VideoTitle from videos;'''
        cursor.execute(query6)
        t6 = cursor.fetchall()
        st.write(pd.DataFrame(t6, columns=["like count","video title"]))

    elif question == '7. Views of each channel':
        query7 = "select Channel_Name as ChannelName, Views as Channelviews from channels;"
        cursor.execute(query7)
        t7=cursor.fetchall()
        st.write(pd.DataFrame(t7, columns=["channel name","total views"]))

    elif question == '8. Videos published in the year 2022':
        query8 = '''select Title as Video_Title, Published_Date as VideoRelease, Channel_Name as ChannelName from videos 
                    where extract(year from Published_Date) = 2022;'''
        cursor.execute(query8)
        t8=cursor.fetchall()
        st.write(pd.DataFrame(t8,columns=["Name", "Video Publised On", "ChannelName"]))

    elif question == '9. Average duration of all videos in each channel':
        query9 = "select Channel_Name as ChannelName, avg(Duration) as average_duration from videos group by Channel_Name order by avg(Duration) desc;"
        cursor.execute(query9)
        t9=cursor.fetchall()
        st.write(pd.DataFrame(t9, columns=['ChannelTitle', 'Average Duration(sec)']))

    elif question == '10. Videos with highest number of comments':
        query10 = '''select Title as VideoTitle, Channel_Name as ChannelName, Comments as Comments from videos 
                           where Comments is not null order by Comments desc;'''
        cursor.execute(query10)
        t10=cursor.fetchall()
        st.write(pd.DataFrame(t10, columns=['Video Title', 'Channel Name', 'NO Of Comments']))

