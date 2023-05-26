import os
import shutil
import zipfile
from base64 import b64decode

import requests

root_path = os.getcwd()
config_path = os.path.join(root_path, 'info.txt')
gat = "Z2l0aHViX3BhdF8xMUJBQkhHNkEwa1JRZEM1dFByczhVXzU0cERCS21URXRGYm" \
      "FYRElUWE5KVUk4VkUxVTdjb0dHbElMSWdhVnI2Qkc3QzVCN0lCWlhWdDJMOUo2"


def download_and_extract_zip(url, root_path):
    zip_file_path = os.path.join(root_path, 'repository.zip')
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('Content-Length', 0))
    block_size = 1024  # 每次下载的块大小
    progress = 0
    with open(zip_file_path, 'wb') as file:
        for data in response.iter_content(block_size):
            progress += len(data)
            file.write(data)

            # 计算下载进度并显示进度条
            percent = (progress / total_size) * 100
            progress_bar = '=' * int(percent // 5) + '>'
            print(f"下载进度: {percent:.2f}% [{progress_bar:<20}] ", end='\r')

    print("\n下载完成！")
    # 解压ZIP文件
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(root_path)

    os.remove(zip_file_path)  # 删除ZIP文件


def sync_github_repo(repo_url, root_path):
    # 构建API URL
    api_url = f"https://api.github.com/repos/{repo_url}/zipball/main"

    # 检查保存路径是否存在，如果不存在则创建
    os.makedirs(root_path, exist_ok=True)

    # 下载并解压ZIP文件
    download_and_extract_zip(api_url, root_path)


def get_latest_branch_sha(repo_url):
    url = f"https://api.github.com/repos/{repo_url}/branches"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": b64decode(gat).decode('utf-8')
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        branches = response.json()
        if branches:
            latest_branch = branches[0]
            return latest_branch['commit']['sha']
    else:
        return None


def get_local_sha():
    # 读取
    with open(config_path, 'r') as file:
        lines = file.readlines()
    # 判断是否有sha信息,没有则填补空行
    if len(lines) < 5:
        lines.extend(['\n'] * (5 - len(lines)))
        with open(config_path, 'w') as file:
            file.writelines(lines)
    return lines[4].strip()


def set_local_sha(sha):
    # 读取
    with open(config_path, 'r') as file:
        lines = file.readlines()
    # 判断是否有sha信息,没有则填补空行
    if len(lines) < 5:
        lines.extend(['\n'] * (5 - len(lines)))
    lines[4] = sha + '\n'
    with open(config_path, 'w') as file:
        file.writelines(lines)


def update_map():
    repo_url = 'CHNZYX/maps'
    # 获取远端sha
    remote_sha = get_latest_branch_sha(repo_url)
    if remote_sha is None:
        print("远端地图sha获取失败, 请检查网络连接")
        return
    print("远端地图sha: " + remote_sha)
    # 获取本地sha
    local_sha = get_local_sha()
    print("本地地图sha: " + local_sha)
    # 判断是否需要更新
    if remote_sha == local_sha:
        print("map无需更新")
        return
    map_path = os.path.join(root_path, 'imgs\\maps')
    print("Map path: " + map_path)
    # 下载map仓库并解压
    sync_github_repo(repo_url, root_path)
    print("下载完成")
    # 找出下载的map文件夹
    t = os.listdir(root_path)
    chn_folders = [item for item in t if item.startswith("CHNZYX")]
    downloaded_map_path = os.path.join(os.path.join(root_path, chn_folders[0]), "maps")
    print("download_map_path: " + downloaded_map_path)
    # 删除原有map文件夹，复制新的map文件夹
    shutil.rmtree(map_path)
    shutil.copytree(downloaded_map_path, map_path)
    shutil.rmtree(os.path.dirname(downloaded_map_path))
    print("更新完成")
    # 更新sha
    set_local_sha(remote_sha)


# 测试用
if __name__ == '__main__':
    root_path = os.path.dirname(os.getcwd())
    config_path = os.path.join(root_path, 'info.txt')
    update_map()