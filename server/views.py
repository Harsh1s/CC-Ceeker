from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from .settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import subprocess
import os
import re
import boto3
import uuid

def index(request):
    return render(request,"index.html")

def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        fileName = handle_uploaded_file(uploaded_file)

        extract_subtitles(fileName)
        save_to_s3(fileName)
        save_srt_content_to_dynamodb(
            fileName,
            os.path.join(f'media/output/{fileName}.srt')
        )

        delete_files_from_server(fileName)

        return redirect(f'/subtitle/{fileName}')
    
    return

def request_subtitle(request,fileid):
    if request.method == 'GET':
        return render(request, 'search.html', {'passed':True})

    elif request.method == 'POST':
        dynamodb = boto3.resource('dynamodb', 
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name='ap-south-1'
        )

        # Get the srt data from dynamodb of the fileid
        table_name = 'subtitles'
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={'video': fileid})
        subtitles = parse_srt_file(response['Item']['subtitles'])

        keyword = request.POST.get('keyword')
        if keyword==None or keyword=='':
            keyword='~!@@#$^%*'
        querysub = search_subtitles(keyword.strip(),subtitles)
        
        save_query_to_dynamo(fileid, querysub, keyword)
        
        return render(request, 'search.html', {'subtitles_data':querysub, 'passed':False}) 
    return

# Returns the file name for the uploaded file
def handle_uploaded_file(uploaded_file):
    newFileName = str(uuid.uuid4()) + uploaded_file.name
    default_storage.save(newFileName, uploaded_file)
    return newFileName

# Runs CCExtractor to extract the subtitles from the video file
# Saves the same to /media/output/<filename>.srt
def extract_subtitles(filename):
    video_file_location = os.path.join(f'media/{filename}')
    output_path = os.path.join(f'media/output/{filename}.srt')

    # Extract the file
    subprocess.run(['ccextractor', video_file_location, '-o', output_path])

    return output_path

def parse_srt_file(srt_response):
    subtitles = []

    subtitle_blocks = re.split(r'\n\s*\n', srt_response.strip())
        
    for block in subtitle_blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            index = int(lines[0].lstrip('\ufeff'))
            times = re.findall(r'(\d{2}:\d{2}:\d{2},\d{3})', lines[1])
            start_time, end_time = times[0], times[1]
            text = '\n'.join(lines[2:])
                
            subtitle = {
                'index': index,
                'start_time': start_time,
                'end_time': end_time,
                'text': text
            }
                
            subtitles.append(subtitle)
    
    return subtitles


def delete_files_from_server(file_name):
    os.remove(os.path.join(f'media/{file_name}'))
    os.remove(os.path.join(f'media/output/{file_name}.srt'))
    return        

def search_subtitles(keyword,subtitles):
    filtered_subs = []
    for i in subtitles:
        if keyword.lower() in i['text'].lower():
            filtered_subs.append(i)
    return filtered_subs

# Uploads the file to S3
def save_to_s3(file_name):
    video_file_location = os.path.join(f'media/{file_name}')
   
    # Specify the file path, S3 bucket name, key (path + filename) on S3, and the credentials
    bucket_name = 'cc-ceeker'
    s3_key = 'videos/' + file_name

    # Create an S3 client with specified credentials and region
    s3 = boto3.client('s3', 
        aws_access_key_id=AWS_ACCESS_KEY_ID, 
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), 
        region_name='ap-south-1'
    )

    # Upload the file
    s3.upload_file(video_file_location, bucket_name, s3_key)

    
def save_srt_content_to_dynamodb(file_name, subtitle_path):
    # Open and read the .srt file
    with open(subtitle_path, 'r') as file:
        subtitle = file.read()

    dynamodb = boto3.resource('dynamodb', 
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name='ap-south-1'
    )

    table_name = 'subtitles'
    table = dynamodb.Table(table_name)
    item = {
        'video': file_name,
        'subtitles': subtitle
    }
    table.put_item(Item=item)

def save_query_to_dynamo(file_name,subtitles,keyword):
    dynamodb = boto3.resource('dynamodb', 
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name='ap-south-1'
    )

    # Specify the table name
    table_name = 'cc-ceeker'
    table = dynamodb.Table(table_name)
    # Specify the item to be inserted
    item = {
        'video': file_name,
        'keyword': keyword,
        'result': subtitles
    }
    table.put_item(Item=item)

    print(f"Item inserted into DynamoDB table: {table_name}")
