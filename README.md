# John Pellman's Curated and Organized Github Stars

[2/11/24]: This repository has been essentially obsolete for quite a while now. GitHub now allows you to organize stars into lists (see [here](https://github.blog/changelog/2021-12-09-lists-are-now-available-as-a-public-beta/).  Although technically lists are still somehow beta (After nearly 2.5 years? Really?) I plan on using them to organize my starred repositories in the future.

This repo hosts a static site that displays exported data from the [Astral](https://github.com/astralapp/astral) app, which is used for the curation / tagging of Github stars.  I add raw data that has been exported from Astral manually (`jpellman_astral_data.json`), a build script processes this data and converts it into a set of Markdown documents, and then [MkDocs](https://www.mkdocs.org/) generates the static site.    

