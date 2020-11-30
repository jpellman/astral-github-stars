#!/usr/bin/env python
import sys
import os
import json
import requests

# Used to map GitHub repo IDs to human-readable names.
GITHUB_API_REPO_URL = "https://api.github.com/repositories"
# Raw data from Astral.
ASTRAL_DATA_JSON = "jpellman_astral_data.json"
# Cached processed data.
ASTRAL_REPO_JSON = "jpellman_astral_repos.json"
ASTRAL_TAGS_JSON = "jpellman_astral_tags.json"

# Load raw data from Astral.
if os.path.exists(ASTRAL_DATA_JSON):
    with open(ASTRAL_DATA_JSON, 'r') as f:
        astralData = json.load(f)
else:
    sys.exit(1)

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

# Convert raw Astral data into a set of tag lists with GitHub repo IDs
# and a dict that maps GitHub repo IDs to human-readable names.
for repoKey in astralData.keys():
    # We don't do unauthenticated API queries due to rate-limiting.
    # If using a personal OAUTH token, then there is a limit of 5000 queries per hour.
    if "OAUTH_TOKEN" not in os.environ:
        print("No OAUTH token.  Will not perform any further processing.")
        break
    else:
        OAUTH_TOKEN = os.environ["OAUTH_TOKEN"]
    repoId = None
    if 'repo_id' not in astralData[repoKey].keys():
        continue
    else:
        repoId = str(astralData[repoKey]['repo_id'])
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
                tags[tag["name"]].append(str(repoId))

# Ensure that all entries in the tag lists are unique.
for tag in tags.keys():
    tags[tag] = set(tags[tag])
    # JSON doesn't seem to support sets, though I could have sworn YAML allows this.
    tags[tag] = list(tags[tag])

# Cache results for the future so we don't send a barrage of API requests to GitHub
# every time the Astral data is updated.
with open(ASTRAL_TAGS_JSON, 'w') as f:
    json.dump(tags, f)

with open(ASTRAL_REPO_JSON, 'w') as f:
    json.dump(repoIds, f)

# Make directory for MkDocs raw markdown.
# Assumes that the script is run from the repo directory.
# This assumption shouldn't be violated for GitHub actions.
DOCDIR = "docs"
if not os.path.exists(DOCDIR):
    os.mkdir(DOCDIR)

TAGDIR = os.path.join(DOCDIR,"tags")
if not os.path.exists(TAGDIR):
    os.mkdir(TAGDIR)

# Make a Markdown page for each set of tags.
for tag in tags.keys():
    TAGFILE = os.path.join(TAGDIR,"%s.md" % str(tag))
    with open(TAGFILE,'w') as f:
        f.write("# %s\n\n" % str(tag))
        for repoId in tags[tag]:
            if "name" not in repoIds[str(repoId)].keys() or "url" not in repoIds[str(repoId)].keys():
                continue
            else:
                f.write("* [%s](%s)\n" % (repoIds[str(repoId)]["name"], repoIds[str(repoId)]["url"]))

# Copy over index and CNAME.
if os.path.exists("README.md"):
    with open("README.md", "r") as f:
        with open(os.path.join(DOCDIR,"index.md"), "w") as idx:
            for line in f:
                idx.write(line)

if os.path.exists("CNAME"):
    with open("CNAME", "r") as f:
        with open(os.path.join(DOCDIR,"CNAME"), "w") as CNAME:
            for line in f:
                CNAME.write(line)
