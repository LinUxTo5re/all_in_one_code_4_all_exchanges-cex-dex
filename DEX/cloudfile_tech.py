import subprocess  # subprocess used as all in one/ execute command and done work
import requests
from credentials import cloudfile_api_key
headers = {
        "ApiKey": cloudfile_api_key
    }

def upload_file_by_command(file_path, fileName):
    global cloudfile_api_key
    file_path = file_path + '/' + fileName
    command = [
        'curl',
        '-H', f'ApiKey:{cloudfile_api_key}',
        '-F', f'file=@{file_path}',
        "https://api.cloudfile.tech/upload"
    ]

    try:
        subprocess.run(command, check=True)
        print("\nFile uploaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"\nFile upload failed. Error: {e}")
    except Exception as e:
        print("error: " + str(e))


def upload_file(file_path, fileName):
    global cloudfile_api_key
    file_path = file_path + '/' + fileName
    url = "https://api.cloudfile.tech/upload"
    files = {
        "file": open(file_path, 'rb')
    }
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        print('\nFile uploaded successfully')
    else:
        print('\nFailed to upload file')


def get_files_list():
    url = "https://api.cloudfile.tech/list"
    response = requests.get(url, headers=headers)
    files_list = dict()
    if response.status_code == 200:
        data = response.json()
        for file in data['files']['results']:
            print(file['id'] + ': ' + file['name'])
            files_list[file['id']] = file['name']
        return files_list
    else:
        print("\nFile listing failed, try again")


def delete_existing_files():
    files_list = get_files_list()
    for file_id in files_list.keys():
        url = f'https://api.cloudfile.tech/remove/{file_id}'
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print(f"\nFile: {files_list.get('file_id')} has been deleted")
        else:
            print("error: Failed to delete file, try again")
def delete_existing_files(fileName):
    files_list = get_files_list()
    for key, file_name in files_list.items():
        if fileName is not None:
            if file_name == fileName:
                url = f'https://api.cloudfile.tech/remove/{key}'
                response = requests.delete(url, headers=headers)
                if response.status_code == 200:
                    print(f"\nFile: {files_list.get('file_id')} has been deleted")
                else:
                    print("error: Failed to delete file, try again")
                break
        else:
            print(f"File: {fileName} not available.")
def download_file(fileName):
    files_list = get_files_list()
    for key, file_name in files_list.items():
        if file_name == fileName:
            file_id = key
            break

    url = f"https://api.cloudfile.tech/download/{file_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_data = response.content
        with open(fileName, 'wb') as file:
            file.write(file_data)
        print(f"\n{fileName} downloaded successfully")
    else:
        print(f"\nFailed to download the {fileName}.")
