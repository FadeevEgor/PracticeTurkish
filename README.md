# PracticeTurkish
A set of tools to practice your Turkish.

## Usage

The main feature of the application --- practice translation of words from Turkish to Russian and vice versa, although the special mode for numbers is implemented. 

### Translation with dictionary

The list of words to practice (a dictionary) is provided by a user in one of two formats:
- **turkrut** --- the format inspired by lessons from [turkrut.ru](turkrut.ru) (see turkrut folder for a few ready to use examples). In most cases, a straight forward copy form a [turkrut.ru](turkrut.ru) into a text file is enough to work.
- **CSV** --- a more general and convenient format (see CSV folder for a few ready to use examples). [https://github.com/FadeevEgor/PracticeTurkish/blob/main/make_csv.py](make_csv.py) script produces such files.


You can start practicing translation with a dictionary by running the command:
```
python practice.py translation 
```
You will be prompted to specify all available options and path to the dictionary. Alternatively, you can specify some options via CLI, see help:
```
python practice.py translation --help
```

### Numbers spelling

To practice spelling of numbers in turkish, type in the following command.
```
python practice.py numbers
```

## Setup 

### Installation

In order to use the application, you'll need **git** and **Python3.10+**.

Firstly, clone the repository and go the directory with source code by executing following commands.
```
git clone https://github.com/FadeevEgor/PracticeTurkish.git
cd PracticeTurkish
```

Then, I recommend you to setup a new virtual environment and install dependencies there, but if you're not familiar with them you can install them globally by executing following commands.
```
python -m pip install -U pip
python -m pip install -r requirements.txt
```

That is, you are ready to start practicing. However, you can improve your experience by configuring telegram bot!

### Telegram bot configuration

Telegram bot **[@PracticeTurkishBot](t.me/PracticeTurkishBot)** is able to send you a message with all mistakes you made during a session. It helps to learn words you're struggling with, since you can see them all in one place and practice them any time. 

In order for the bot to be able to send messages directly to you, it's necessary to configure the bot by completing the file **config.ini**. Gladly, the process is straight forward.

First, start a private chat with the bot. You can find him either by following the link [t.me/PracticeTurkishBot](t.me/PracticeTurkishBot) or by typing **PracticeTurkishBot** in the search bar.

In response to command "**/start**", he'll send you several messages containing all the information necessary for configuration. The last message should contain correct content for your **config.ini** file. Bellow is how this message could look like.
```
[BOT API]
URL = https://http-d2ooxt72na-lm.a.run.app/external
USER ID = YOURID
TOKEN = YOURTOKEN
```
Copy the last information by the bot and paste it in the file **config.ini**. That's all, your bot is configured!

**Your token is used to ensure that only you'll be able to send messages to you via the bot. Please, don't share it with people you don't trust.**
