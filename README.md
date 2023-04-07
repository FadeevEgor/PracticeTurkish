# PracticeTurkish

A set of command line tools to practice your Turkish vocabulary. 

Create a dictionary file and practice translation from one language to another. You can find files used by the author of the package at [PracticeTurkishDictionaries](https://github.com/FadeevEgor/PracticeTurkishDictionaries) repository.

Supported languages:
- Turkish;
- Russian;
- English.

Although the main goal was to add support for Turkish language, it's possible to practice translation from and to any of the languages listed above, including Russian ⇨ English and vice versa.   

## Installation

In order to install application all you need is working **Python3.10+**.

Prior to installation, I recommend you to create a directory on your machine: it'll be much more convenient to store all your dictionaries, your configuration file and virtual environment at one place. Preferably, you will always lunch the application from the same directory with the following structure.
```
folder/
├── venv/    
├── turkrut/    
├── CSV/
├── config.ini
```
You can create a folder with the exact structure, by cloning the repository [PracticeTurkishDictionaries](https://github.com/FadeevEgor/PracticeTurkishDictionaries). As a bonus you will get a few ready to use dictionaries used by author of the package.  

Then, I recommend you to setup a new virtual environment in the folder, but if you're not familiar with python virtual environments, you can install the package globally with little to no effort.

To install the application, run the following command.  
```
python -m pip install practice-turkish
```
That is, you are ready to start practicing. However, you can improve your experience by configuring telegram bot! See **"Telegram bot configuration"** section bellow.


## Usage

The main feature of the application — practice translation of words from Turkish to Russian and vice versa, although the special mode for numbers is implemented. 

### Translation with dictionary

The list of words to practice (a dictionary) is provided by a user in one of two formats:
- **turkrut** — the format inspired by lessons from [turkrut.ru](turkrut.ru). Supports only turkish and russian languages. In most cases, a straight forward copy form a [turkrut.ru](turkrut.ru) into a text file is enough to work. 
- **CSV** — a more general and convenient format. Supports all languages and phrases.  The command `new_dictionary` helps you to generate such files.

You can find examples of dictionaries of both formats in another [repository](https://github.com/FadeevEgor/PracticeTurkishDictionaries).


You can start practicing translation with a dictionary by running the command in your command line:
```
translate
```
**If you used virtual environment, the command `translate` will be available only inside the environment.**

You will be prompted to specify all available options and path to the dictionary, after which the translation session will start.


### Numbers spelling

To practice spelling of numbers in turkish, type in the following command.
```
numbers
```

**If you used virtual environment, the command `numbers` will be available only inside the environment.**

## Telegram bot configuration

Telegram bot **[@PracticeTurkishBot](https://t.me/PracticeTurkishBot)** is able to send you a message with all mistakes you made during a session. It helps to learn words you're struggling with, since you can see them all in one place and practice them any time. 

In order for the bot to be able to send messages directly to you, it's necessary to configure the bot by creating a file **config.ini** with correct content, ideally in the folder with your dictionaries.

First, start a private chat with the bot. You can find him either by following the link [t.me/PracticeTurkishBot](https://t.me/PracticeTurkishBot) or by typing **PracticeTurkishBot** in the search bar.

In response to command `/config`, it'll send you a message with the content of your configuration file. Here's how it'll look like.
```
[BOT API]
USER ID = YOURID
TOKEN = YOURTOKEN
```
Copy that information by the bot and paste it in the file **config.ini**. That's all, as long as you running `translate` command from the same folder, the file **config.ini**, the bot will send all your mistakes to you via telegram!

**Your token is used to ensure that only you'll be able to send messages to you via the bot. Please, don't share it with people you don't trust.**
