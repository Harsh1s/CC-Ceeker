# CC-Ceeker
Your Go-To Seeker in the Subtitle Safari – Navigate the Jungle of Videos with Ease using Subtitle Searches!

Link:
You can try the app at this link: http://ec2-35-154-71-104.ap-south-1.compute.amazonaws.com:8000/

## Overview
This project is aimed at creating a web application that allows users to upload videos, process them by extracting subtitles using the ccextractor binary, and then search for specific content within the videos using the extracted subtitles as keywords. All of the processing is done behind the scenes by an EC2 instance. Video files are processed and then stored in an S3 bucket and their subtitles are given a unique id and stored in a DynamoDb table. When the user searches for a specific keyword, the DynamoDB table for subtitles is looked into for the corresponding subtitle of the video file. Then this subtitle file is processed to search for the keywords. The search results are further stored in a separate table.

## Features
### Subtitle Extraction:
Subtitles will be extracted from uploaded videos using the ccextractor binary.
The extracted subtitles will be stored with a unique id in the database.

### Video Processing:
Uploaded videos will be processed in the background to ensure seamless user experience.
The processed videos will be stored in Amazon S3 and at the same time removed from the processing server to free space.

### Keyword-Based Search:
Users can search for specific words or phrases, and the application will return the time segment within which the video contains those phrases.
The search results themselves are stored in a DynamoDB table.

### Snappy:
The application is designed to be as fast as possible, reducing the search times to as short as possible.
The moment a video file is uploaded, it is processed and ready for a search.

### Miscellaneous:
File recognition is built in so that only valid files can be uploaded.
Everything is hosted and doesn't require any setup time by the user.

## Environment Setup:

### If you want to test the app locally, you can follow these steps:
Make sure you have Python installed on your system.
Install CCExtractor on your system, preferably version 0.88.

AWS Configuration:
Edit the .env file and add the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY after creating a user with correct permissions using IAM.

Installing Requirements:
```
pip install -r requirements.txt
```

Run the Application:

Start the Django development server:
```
python manage.py runserver
```
Access the application at http://localhost:8000.

## Video Demo
[Screen recording 2023-11-29 2.04.52 PM.webm](https://github.com/Harsh1s/CC-Ceeker/assets/53043454/5c600572-05c5-45fb-95af-00912226d035)
