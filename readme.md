# Instruction
## Adding a repository address to a project
    git remote add <name_remote> <address_repository>
## Creating a new branch without history
    git checkout --orphan <name_branch>
## Clearing a created branch
    git reset
    git clean -df
## Download all tags from a remote repository
    git fetch <name_remote> --tags
## Allows you to merge the stories of two projects that started their lives independently
    git merge --allow-unrelated-histories <name_remote>/<name_branch_remote_repository>
## Upload data to a new repository and create a new branch in it
    git push origin <name_new_branch>
# Useful link
## https://github.com/cyberspacedk/Git-commands.git