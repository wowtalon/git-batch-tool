#!/usr/bin/env python

import os
from re import findall, DOTALL, IGNORECASE
from requests import get
from termcolor import cprint
from time import sleep


base_dir = os.getcwd()
base_url = "https://github.com"


def git_explore(keyword, page_count):
    cprint('[*] Exploring git, base url:{}'.format(base_url), 'yellow')
    os.chdir(base_dir)

    repos = []
    url = '{}/explore/repos?page={}&q={}'.format(base_url, keyword)

    for page in range(1, page_count + 1):
        res = get(url.format(page))
        repo = findall(r'<a class="name" href=".*?">(.+?)<\/a>', res.text, DOTALL | IGNORECASE)
        repos.extend(repo)
        sleep(0.05)

    cprint('[*] Explore done.', 'yellow')

    with open('./repos.txt', 'w') as repo_file:
        repo_file.write('\n'.join(repos))


def git_clone_batch(repo_list):
    cprint('[*] Git batch clone start.', 'green')
    if not os.path.isdir('./repos'):
        os.mkdir('./repos')
    os.chdir(os.path.join(base_dir, 'repos'))
    with open(repo_list) as ff:
        for line in ff:
            line = line.replace(' ', '')
            cprint('[*] Cloning {}'.format(line), 'green')
            os.system('git clone {}/{}'.format(base_url, line))


def count_by_path(repos_dir):
    repo_count = {}

    for repo in os.listdir(repos_dir):
        cprint('[*] Counting {}...'.format(repo), 'yellow')
        if not os.path.isdir(os.path.join(repos_dir, repo, '.git')):
            print('Empty Folder.')
            continue
        os.chdir(os.path.join(repos_dir, repo))
        res_count = []
        res = os.popen('git log --pretty="%ad"| awk \'NR==1{print}\'')
        res_count.append(res.read().replace('\n', ''))
        res.close()
        res = os.popen('git log --pretty="%ad"| tail -n 1')
        res_count.append(res.read().replace('\n', ''))
        res.close()
        res = os.popen('git log --pretty="%aN" | sort -u')
        res_count.append(res.read().replace('\n', ''))
        res.close()
        repo_count[repo] = res_count
    os.chdir(base_dir)
    return repo_count


def count():
    cprint('[*] Git count start.', 'green')
    repos_dirs = [
        os.path.join(base_dir, 'repos')
    ]

    repo_count = {}
    for repos_dir in repos_dirs:
        _repo_count = count_by_path(repos_dir)
        for repo in _repo_count:
            repo_count[repo] = _repo_count[repo]
    cprint('[*] Git count done.', 'green')
    return repo_count


if __name__ == '__main__':
    repo_count = count()

    os.chdir(base_dir)
    with open('repo_count.csv', 'w') as rc:
        for repo in repo_count:
            rc.write('{},{}\n'.format(repo, ','.join(repo_count[repo])))

