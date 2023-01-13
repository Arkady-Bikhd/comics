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
    actual_version_API = '5.131'
    file_name = 'image.png'
    try:
        caption = get_comics()
        try:
            post_wall_photo(vk_access_token, vk_group_id, actual_version_API, file_name, caption)
        except requests.exceptions.HTTPError:
            print('Ошибка опубликования комикса')
    except requests.exceptions.HTTPError:
        print('Ошибка загрузки комикса')


def get_num_comics():

    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['num']


def get_comics():

    comics_number = randint(1, get_num_comics())
    url = f'https://xkcd.com/{comics_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()  
    get_image(response.json()['img'])

    return response.json()['alt'] 


def get_image(url):

    response = requests.get(url)
    response.raise_for_status()
    file_name = Path().cwd() / 'image.png'    
    with open(file_name, 'wb') as file:
        file.write(response.content)


def get_url_vk_group(vk_access_token, vk_group_id, version_API, file_name):

    
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payloads = {
        'access_token': vk_access_token, 
        'v': version_API,
        'group_id': vk_group_id
    }
    response = requests.get(url, params=payloads)
    response.raise_for_status()    
    response = response.json()    
    if 'error' in response:
        print_error_msg(response, file_name)            
    else:
        return response['response']['upload_url']
        

def print_error_msg(response, file_name):

    Path(file_name).unlink() 
    print('Ошибка. Описание:')
    print(response['error']['error_msg'])
    exit() 



def upload_comics_file(vk_access_token, vk_group_id, version_API, file_name):
    with open(file_name, 'rb') as file:
        url = get_url_vk_group(vk_access_token, vk_group_id, version_API, file_name)
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
    return response


def upload_wall_photos(vk_access_token, vk_group_id, version_API, file_name):
    
    with open(file_name, 'rb') as file:
        url = get_url_vk_group(vk_access_token, vk_group_id, version_API, file_name)
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
    response.raise_for_status()
    response = response.json()
    if 'error' in response:
        print_error_msg(response, file_name)
    elif response['photo'] == '[]':
        print('Комикс не загружен в группу')
        exit()
    else:
        return response
                 

def save_wall_photo(vk_access_token, vk_group_id,  version_API, file_name):

    url = 'https://api.vk.com/method/photos.saveWallPhoto'  
    
    response_upload_photo = upload_wall_photos(vk_access_token, vk_group_id, version_API, file_name)    
    payloads = {
        'access_token': vk_access_token,         
        'group_id': vk_group_id,
        'photo': response_upload_photo['photo'],
        'server': response_upload_photo['server'],
        'v': version_API,
        'hash': response_upload_photo['hash']
    }
    response = requests.post(url, params=payloads)
    response.raise_for_status()
    response = response.json()    
    if 'error' in response:
        print_error_msg(response, file_name)
    else:
        return response['response']


def post_wall_photo(vk_access_token, vk_group_id, version_API, file_name, caption):

    url = 'https://api.vk.com/method/wall.post'  
    
    response_save_wall_photo = save_wall_photo(vk_access_token, vk_group_id, version_API, file_name)
    owner_id = response_save_wall_photo[0]['owner_id']
    media_id = response_save_wall_photo[0]['id']
    payloads = {
        'access_token': vk_access_token,         
        'owner_id': -int(vk_group_id),
        'from_group': 1,
        'message': caption,
        'attachments': f'photo{owner_id}_{media_id}',        
        'v': version_API,        
    }
    response = requests.post(url, params=payloads)
    response.raise_for_status()
    response = response.json()
    if 'error' in response:
        print_error_msg(response, file_name)
    Path(file_name).unlink()
         


if __name__ == "__main__":
    main()