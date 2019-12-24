#!/bin/bash
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

tagname="2.9.1"
git tag -d "$tagname"
git push --delete origin "$tagname"
git tag -a "$tagname"
git push --tags
