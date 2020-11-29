#!/usr/bin/env python
import os
import json
import requests

GITHUB_API_REPO_URL = "https://api.github.com/repositories"
ASTRAL_DATA_JSON = "jpellman_astral_data.json"
ASTRAL_REPO_JSON = "jpellman_astral_repos.json"
ASTRAL_TAGS_JSON = "jpellman_astral_tags.json"

with open(ASTRAL_DATA_JSON, 'r') as f:
    astralData = json.load(f)

# Use cached results from last run if available.
if not os.path.exists(ASTRAL_TAGS_JSON):
    tags = {}
else:
    try:
        with open(ASTRAL_TAGS_JSON, 'r') as f:
            tags = json.load(f)
    except:
        tags = {}

if not os.path.exists(ASTRAL_REPO_JSON):
    repoIds = {}
else:
    try:
        with open(ASTRAL_REPO_JSON, 'r') as f:
            repoIds = json.load(f)
    except:
        repoIds = {}

for repoKey in astralData.keys():
    if "OAUTH_TOKEN" not in os.environ:
        continue
    else:
        OAUTH_TOKEN = os.environ["OAUTH_TOKEN"]
    repoId = None
    if 'repo_id' not in astralData[repoKey].keys():
        continue
    else:
        repoId = astralData[repoKey]['repo_id']
        if repoId not in repoIds.keys():
            repoIds[repoId] = {}
            print("Doing reverse lookup for repo ID %d" % repoId)
            # Undocumented GitHub API call to get repo data from repo ID.
            # https://github.com/octokit/rest.js/issues/163
            print("%s/%d" % (GITHUB_API_REPO_URL, repoId))
            repoRequest = requests.get("%s/%d" % (GITHUB_API_REPO_URL, repoId), auth=("token",OAUTH_TOKEN))
            repoJSON = json.loads(repoRequest.text)
            if "name" not in repoJSON.keys():
                continue
            else:
                repoIds[repoId]["name"] = repoJSON["name"]
            if "html_url" in repoJSON.keys():
                repoIds[repoId]["url"] = repoJSON["html_url"]
            elif "homepage" in repoJSON.keys():
                repoIds[repoId]["url"] = repoJSON["homepage"]
            else:
                continue
    if 'tags' in astralData[repoKey].keys():
        for tag in astralData[repoKey]['tags']:
            if "name" not in tag.keys():
                continue
            if tag["name"] not in tags.keys():
                tags[tag["name"]] = []
            if repoId not in tags[tag["name"]]:
                tags[tag["name"]].append(repoId)

with open(ASTRAL_TAGS_JSON, 'w') as f:
    json.dump(tags, f)

with open(ASTRAL_REPO_JSON, 'w') as f:
    json.dump(repoIds, f)

