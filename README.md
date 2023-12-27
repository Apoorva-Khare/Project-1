# Project-1

# DS_YOUTUBE DATA HARVESTING AND WAREHOUSING 

# INTRODUCTION

YouTube Data Harvesting and Warehousing is a project aimed at developing a user-friendly Streamlit application that uses Google API to extract valuable information from YouTube channels. The extracted data is then stored in a MongoDB database, subsequently migrated to a SQL data warehouse, and made accessible for analysis and exploration within the Streamlit app.

# TABLE OF CONTENTS
1. Key Technologies and skills.
2. Installation.
3. Features.
4. Data Analysis.

# Key Technologies and skills
* Python Scripting
* Data Collection
* API Integration
* Data Management using MongoDB and MYSQL
* Streamlit

# Installation

To run this project, you need to install the following packages:

from googleapiclient.discovery import build
import pymongo
import mysql.connector
import pandas as pd
import streamlit as st
from PIL import Image

# Features

* Retrieve data from the YouTube API, including channel information, playlists, videos, and comments.
* Store the retrieved data in a MongoDB database.
* Migrate the data to a SQL data warehouse.
* Perform queries on the SQL data warehouse.
* Use of the Streamlit Application to display all information in proper format.

# Retrieve data from the YouTube API, including channel information, videos information, and comments information:

The project utilizes the Google API to retrieve required data from YouTube channels. The data includes information on channels, videos, and comments. By interacting with the Google API, we collect the data and merge it in Python file.

# Storing data in MongoDB

The retrieved data is stored in a MongoDB database based on user authorization. It display the channel information, video information and comments information of each channel and its videos.

# Migrating data to MYSQL

The application allows users to migrate data from MongoDB to a SQL data warehouse. Data is extracted from MongoDB and stored in the table format in MySQL and from MySQL data is extracted from table according to the requirement using MySQL query.

# Streamlit Application
Streamlit library was used to create a user-friendly UI that enables users to interact with the programme and carry out data retrieval and analysis operations.

# CONTACT

📧 Email: apkhare29@gmail.com

🌐 LinkedIn: https://www.linkedin.com/in/apoorva-khare-7548642a6/

