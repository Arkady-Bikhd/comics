import requests
from dotenv import load_dotenv
from os import environ
from pathlib import Path
from random import randint
from sys import exit



def main():

    load_dotenv()
    vk_access_token = environ['VK_ACCESS_TOKEN']
    vk_group_id = environ['VK_GROUP_ID']
    actual_api_version = '5.131'
    file_name = 'image.png'
    try:
        comic_caption = download_random_comic()
        try:
            post_wall_photo(vk_access_token, vk_group_id, actual_api_version, file_name, comic_caption)
        except requests.exceptions.HTTPError:
            print('Ошибка опубликования комикса')
    except requests.exceptions.HTTPError:
        print('Ошибка загрузки комикса')


def download_random_comic():

    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    total_comic = response.json()['num']
    comic_number = randint(1, total_comic)
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()  
    comic_link = response.json()['img']
    comic_caption = response.json()['alt']
    response = requests.get(comic_link)
    response.raise_for_status()
    file_name = Path().cwd() / 'image.png'    
    with open(file_name, 'wb') as file:
        file.write(response.content)

    return comic_caption 


def delete_image_file(file_name):
    Path(file_name).unlink() 


def get_upload_vk_server_url(vk_access_token, vk_group_id, api_version, file_name):

    
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
        print_error_msg(upload_url_response, file_name)            
    else:
        return upload_url_response['response']['upload_url']
        

def print_error_msg(response, file_name):
    
    delete_image_file(file_name)
    print('Ошибка. Описание:')
    print(response['error']['error_msg'])
    exit() 


def upload_wall_photos(vk_access_token, vk_group_id, api_version, file_name):
    
    with open(file_name, 'rb') as file:
        url = get_upload_vk_server_url(vk_access_token, vk_group_id, api_version, file_name)
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
    response.raise_for_status()
    upload_wall_photo_response = response.json()
    if 'error' in upload_wall_photo_response:
        print_error_msg(upload_wall_photo_response, file_name)
    elif upload_wall_photo_response['photo'] == '[]':
        print('Комикс не загружен в группу')
        exit()
    else:
        return upload_wall_photo_response
                 

def save_wall_photo(vk_access_token, vk_group_id,  api_version, file_name):

    url = 'https://api.vk.com/method/photos.saveWallPhoto'  
    
    upload_photo_response = upload_wall_photos(vk_access_token, vk_group_id, api_version, file_name)    
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
        print_error_msg(save_wall_photo_response, file_name)
    else:
        return save_wall_photo_response['response']


def post_wall_photo(vk_access_token, vk_group_id, api_version, file_name, caption):

    url = 'https://api.vk.com/method/wall.post'  
    
    save_wall_photo_response = save_wall_photo(vk_access_token, vk_group_id, api_version, file_name)
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
        print_error_msg(post_wall_photo_response, file_name)
    delete_image_file(file_name)
       

if __name__ == "__main__":
    main()