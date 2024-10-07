# task-hooks

## Problem statement
I'm a sales engineer. Much of my workflow is in Salesforce, particularly where quote creation is concerned. I often need to context switch as higher priority tasks arise, and I want to avoid losing track of what I'm working on. 

## Solution
Salesforce has a notion of a Task object, which is quite general and can be used for many activities, but in my case is mostly used by my reps as a support ticket when they want me to do something. These tasks have a priority, due date, and a few other fields. It occurred to me that I can map Salesforce Tasks to Taskwarrior tasks, and vice versa, using hooks. This project is the implementation of that concept.

```task-hooks``` contains:
- An import script which pulls the user's tasks from Salesforce's API and maps them to Taskwarrior tasks. 
- A Taskwarrior hook which updates those tasks in Salesforce as you interact with them in Taskwarrior e.g. start, stop, complete, block.

You'll need to grab an access token from the Salesforce CLI (```sf```) before you can use any of these. Instructions below.

## Setup
1. Clone this repo.
2. Install ```task``` and ```sf``` using the package manager of your choice, and consider also installing ```tasksh``` for ease of use. 
    - On all platforms, ```npm``` is the recommended package manager for installing the Salesforce CLI. Run ```npm install -g @salesforce/cli```.
    - On MacOS, ```sf``` is also available through Homebrew. Run ```brew install sf```.
3. Authenticate to Salesforce.
```sh
sf org login web --alias <ORG_ALIAS> --instance-url <YOUR INSTANCE URL>
```
4. ```cd``` into the repo, if you haven't already, and initialize and activate a virtualenv.
```sh
python -m venv .
source bin/activate
```
5. Install python dependencies.
```sh
pip install -r requirements.txt
```
6. Initialize access tokens and $PYTHONPATH.
```sh
source scripts/init.sh <ORG_ALIAS>
```
7. Install the hook shims.
```sh
cd hooks
install-hook-shims -r *
```
8. Finally, make sure to import tasks from Salesforce:
```sh
./scripts/sf_read.py | import task
```

Now you're all set to run Taskwarrior through ```task``` or ```tasksh```. You'll notice your Salesforce tasks will be tagged with ```+salesforce``` by default, and any changes you make to their status in Taskwarrior within the virtualenv will be immediately synced to Salesforce.

When you want to start using the hooks again (e.g. after you've closed your terminal), you won't need to go through all that setup again. Here's all you'll need to do:
```sh
source bin/activate
source scripts/init.sh <ORG_ALIAS>
./scripts/sf_read.py | import task
```

## Uninstallation
1. Remove the installed shims from ```~/.task/hooks/```.
2. Delete this repo.
3. Uninstall ```sf``` and ```task```.

## Future plans
- ```task-hooks``` currently implements bidirectional sync with Salesforce only. Not everyone I work with has the ability or willingness to create Salesforce tasks and I get a lot of requests in Slack to do various things. I'd like Taskwarrior to continue to be my single source of task truth, so I'm looking into building a similar integration with Slack. Please let me know if you've ever done something similar to this with Slack's API.

## Why?
Salesforce doesn't make it easy to prioritize tasks, graph them into dependency chains, group them into projects, or any of the other great features I'm used to in Taskwarrior. I wanted the best of both worlds, so I built it. I get much more granular reporting w.r.t. time spent, burndown charts, etc., and my reps don't need to guess what I'm working on anymore, since Salesforce is now guaranteed to be accurate because it's automatically updated. Everyone wins.

## Limitations and known bugs
- Some Salesforce instances don't allow programmatic task completion. You may need to manually close out tasks after completing or deleting them in Taskwarrior. All the other TaskStatus states seem to be writeable through the API, but YMMV.
- In a prior version of the Salesforce hook, deleting or completing a task which is blocking a ```+salesforce``` task would continue to block that task in Salesforce (```{"Status": "In Progress"}```). This is by design: task dependency graphs persist in Taskwarrior even after blocking tasks are completed or deleted. Unfortunately, because it's not possible to explore the context of modified tasks in the OnModify hook, there's no way to know whether the OnModify task is blocked by a pending or by a completed task, so ```task-hooks``` doesn't use dependency chains to discover blocked tasks. You'll have to manually mark tasks as blocked using the ```+waitingfor``` tag, which corresponds to the "Waiting on someone else" status in Salesforce.

## Acknowledgements
This project uses [bergercookie](https://github.com/bergercookie)'s [tw-hooks](https://github.com/bergercookie/tw-hooks) framework. Thanks Nikos for your excellent work.
