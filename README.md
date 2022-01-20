# Wordle
To better understand the code and this project, it might be helpful to watch the accompanying YouTube video: https://www.youtube.com/watch?v=R_9qLkVim4s&ab_channel=TechTribe. 

The goal was to make a bot that solves Wordle in under 6 attempts every time. Every wordle game has a valid guess list (larger list) and a valid answer list (smaller list of common words). The bot tries to find out as much information as possible about the anwer by narrowing down the possible answer list. This is accomplished by choosing guesses from the guess list.

`wordle_test.py` contains the algorithm, specifically a function that chooses a random word and the algorithm tries to guess it. It also includes functions that test the accuracy and speed of the algorithm. It has 100% accuracy (rate at which it guesses the secret word in 6 or fewer guesses) and takes about 2 seconds per puzzle on average (5.5 seconds in the worst case). 

`words.py` contains helper functions to load the list of guess and answer words from the `.txt` files. Wordmaster (https://octokatherine.github.io/word-master/) lets you play multiple times a day, but it has a different word and guess list, so this Python file contains helper functions to load those text files as well.

`play_wordle.py` uses Selenium to actually play Wordle without human input. There is a boolean that you can change called `classic_wordle.` If True, it will play the classic wordle - otherwise it plays Wordmaster. Then, you can call `run_program` and the program will start. Once the correct website loads, you can close any modals / popups and then press the Escape key. This will start the program. For classic wordle, it just solves one puzzle (because that's the daily limit). For Wordmaster, you can specify how many puzzles you want to watch it solve, and it will solve multiple.

In the botfights directory, you can see my submission to the Botfights (https://botfights.io/game/wordle) Wordle bot competitition. Specifically, it is in the `sample-bot.py` file. 

The algorithm I used in `play_wordle.py` for the websites tries to minimize the worst-case length of the narrowed down answer list after a certain guess. This has more consistent performance. For the botfights submission, I tried to minimize the average (expected) length of the narrowed down answer list after a certain guess. While there is more variance to this algorithm, it leads to the lowest number of average guesses per wordle puzzle, which is ultimately what the competition tests. This algorithm takes forever to run for botfights (2+ hours for 1000 words in the competition), but guesses the correct answer (from 13,000 possible words) in 4.1 tries on average. Pretty solid!
