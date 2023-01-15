import requests
from dotenv import load_dotenv
from os import environ
from pathlib import Path
from random import randint
from requests.exceptions import HTTPError


def main():

    load_dotenv()
    vk_access_token = environ['VK_ACCESS_TOKEN']
    vk_group_id = environ['VK_GROUP_ID']
    actual_api_version = '5.131'
    file_name = 'image.png'
    try:
        comic_caption = download_random_comic()
    except HTTPError:
        print('Ошибка загрузки комикса')
    try:
        post_comic_in_vk(vk_access_token, vk_group_id, actual_api_version, file_name, comic_caption)
    except HTTPError as err:
        print('Ошибка опубликования комикса')
        print(err.args[0])        
    finally:
        Path(file_name).unlink()
    

def download_random_comic():

    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    total_comic = response.json()['num']
    comic_number = randint(1, total_comic)
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()  
    comic_response = response.json()    
    response = requests.get(comic_response['img'])
    response.raise_for_status()
    file_name = Path().cwd() / 'image.png'    
    with open(file_name, 'wb') as file:
        file.write(response.content)

    return comic_response['alt'] 


def get_upload_vk_server_url(vk_access_token, vk_group_id, api_version):

    
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payloads = {
        'access_token': vk_access_token, 
        'v': api_version,
        'group_id': vk_group_id
    }
    response = requests.get(url, params=payloads)
    response.raise_for_status()    
    upload_url_response = response.json()    
    if 'error' in upload_url_response:
        raise HTTPError(upload_url_response['error']['error_msg'])          
    return upload_url_response['response']['upload_url']
        

def upload_comic_file(url, file_name):
    
    with open(file_name, 'rb') as file:
            files = {
                'photo': file
            }
            response = requests.post(url, files=files)
    response.raise_for_status()    
    return response


def upload_wall_photo(file_name, url):
    
    upload_file_response = upload_comic_file(url, file_name)
    upload_wall_photo_response = upload_file_response.json()
    if 'error' in upload_wall_photo_response:
        raise HTTPError(upload_wall_photo_response['error']['error_msg'])  
    elif upload_wall_photo_response['photo'] == '[]':
        raise HTTPError('Комикс не загружен в группу')                    
    return upload_wall_photo_response
                 

def save_wall_photo(vk_access_token, vk_group_id,  api_version, upload_photo_response):

    url = 'https://api.vk.com/method/photos.saveWallPhoto'  
    payloads = {
        'access_token': vk_access_token,         
        'group_id': vk_group_id,
        'photo': upload_photo_response['photo'],
        'server': upload_photo_response['server'],
        'v': api_version,
        'hash': upload_photo_response['hash']
        }
    response = requests.post(url, params=payloads)
    response.raise_for_status()
    save_wall_photo_response = response.json()    
    if 'error' in save_wall_photo_response:
        raise HTTPError(save_wall_photo_response['error']['error_msg']) 
    return save_wall_photo_response['response']


def post_wall_photo(vk_access_token, vk_group_id, api_version, file_name, caption, save_wall_photo_response):

    url = 'https://api.vk.com/method/wall.post'  
    owner_id = save_wall_photo_response[0]['owner_id']
    media_id = save_wall_photo_response[0]['id']
    payloads = {
        'access_token': vk_access_token,         
        'owner_id': -int(vk_group_id),
        'from_group': 1,
        'message': caption,
        'attachments': f'photo{owner_id}_{media_id}',        
        'v': api_version,        
    }
    response = requests.post(url, params=payloads)
    response.raise_for_status()
    post_wall_photo_response = response.json()
    if 'error' in post_wall_photo_response:
        raise HTTPError(post_wall_photo_response['error']['error_msg']) 
               

def post_comic_in_vk(vk_access_token, vk_group_id, api_version, file_name, caption):

    upload_vk_server_url = get_upload_vk_server_url(vk_access_token, vk_group_id, api_version)
    upload_wall_photo_response = upload_wall_photo(file_name, upload_vk_server_url)
    save_wall_photo_response = save_wall_photo(vk_access_token, vk_group_id,  api_version, upload_wall_photo_response)
    post_wall_photo(vk_access_token, vk_group_id, api_version, file_name, caption, save_wall_photo_response)
    

if __name__ == "__main__":
    main()