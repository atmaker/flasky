#!/bin/bash

# Fetch the latest changes
git fetch origin

# Get list of all remote branches except master/main
branches=$(git branch -r | grep -v 'master\|main' | sed 's/origin\///')

for branch in $branches; do
    echo "Processing branch: $branch"
    git checkout $branch
    git merge origin/master -m "Merge origin/master into $branch"
    
    if [ $? -eq 0 ]; then
        git push origin $branch
        echo "Successfully merged master into $branch and pushed."
    else
        echo "Merge conflict in $branch. Please resolve manually."
    fi
done

# Checkout master/main at the end
git checkout master
