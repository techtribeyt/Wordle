from words import get_wordle_guesses, get_wordle_answers, get_wordmaster_guesses, get_wordmaster_answers
import time 
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import keyboard
import numpy as np

def play(game_rows, browser, possible_guesses, possible_answers, classic_wordle=True):
    # get the word list
    words = possible_guesses
    narrowed_down_list = possible_answers

    for guess_number in range(5):
        # goal is to minimize the longest possible word list after guess & evaluation
        # start this metric at a million (we have under 100k words)
        min_wordcount = 1e6
        chosen_word = ""
        evaluation_to_wordlist_map = {}
        
        
        if guess_number != 0:
            words_to_consider = words
        else:
            # first guess doesn't change
            # there are many "good" first guesses
            # best words: https://www.polygon.com/gaming/22884031/wordle-game-tips-best-first-guess-5-letter-words
            words_to_consider = ["arise"]
    
        # check every word in words_to_consider to see which one gives us most information
        # (allows us to cancel out the most words)
        for word_to_guess in words_to_consider:
            temp_eval_to_words_map = {}
            
            # evaluate with every possible answer
            for possible_answer in narrowed_down_list:
                evaluation = get_evaluation(possible_answer, word_to_guess)
                        
                # store word by evaluation tuple in a list
                if tuple(evaluation) not in temp_eval_to_words_map:
                    temp_eval_to_words_map[tuple(evaluation)] = [possible_answer]
                else:
                    temp_eval_to_words_map[tuple(evaluation)].append(possible_answer)
    
    
            # metric we are trying to minimize
            biggest_possible_remaining_wordcount = max([len(val) for val in temp_eval_to_words_map.values()])
            
            # if we found a new minimum
            if biggest_possible_remaining_wordcount < min_wordcount:
                min_wordcount = biggest_possible_remaining_wordcount
                chosen_word = word_to_guess
                
                # save current best wordlist map
                evaluation_to_wordlist_map = temp_eval_to_words_map

        # evaluate chosen word with answer
        enter_guess(chosen_word)
        time.sleep(1)
        if classic_wordle:
            answer_evaluation = get_wordle_evaluation(chosen_word, game_rows[guess_number], browser)
        else:
            answer_evaluation = get_wordmaster_evaluation(chosen_word, game_rows[guess_number], browser)
        if answer_evaluation in evaluation_to_wordlist_map:
            narrowed_down_list = evaluation_to_wordlist_map[answer_evaluation]
            
        if answer_evaluation == [2, 2, 2, 2, 2]:
            return [chosen_word]
        time.sleep(1)
        
        # once narrowed down to 1, we are done
        if len(narrowed_down_list) == 1:
            enter_guess(narrowed_down_list[0])
            return [chosen_word]
    return narrowed_down_list
            

def get_wordle_evaluation(chosen_word, game_row, browser):
    row = browser.execute_script('return arguments[0].shadowRoot', game_row)
    tiles = row.find_elements(By.CSS_SELECTOR, "game-tile")
    evaluation = []
    eval_to_int = {
        "correct": 2,
        "present": 1,
        "absent": 0
    }
    for tile in tiles:
        evaluation.append(eval_to_int[tile.get_attribute("evaluation")])
    return tuple(evaluation)

def get_wordmaster_evaluation(chosen_word, game_row, browser):
    evaluation = []
    for tile in game_row:
        if 'nm-inset-n-green' in tile.get_attribute("class"):
            evaluation.append(2)
        elif 'nm-inset-yellow-500' in tile.get_attribute("class"):
            evaluation.append(1)
        elif 'nm-inset-n-gray' in tile.get_attribute("class"):
            evaluation.append(0)
    return tuple(evaluation)
    
    
def enter_guess(word):
    keyboard.write(word, delay=0.05)
    keyboard.press_and_release('enter')

def get_evaluation(answer, word):
    # 0 = nothing, 1 = yellow, 2 = green
    output = [0, 0, 0, 0, 0]
    
    # check for correct letter and placement
    for i in range(5):
        if word[i] == answer[i]:
            output[i] = 2
            answer = answer[:i] + ' ' + answer[i + 1:]
           
    # check for correct letter
    for i in range(5):
        char = word[i]
        if char in answer and output[i] == 0:
            output[i] = 1
            first_occurence = answer.find(char)
            answer = answer[:first_occurence] + ' ' + answer[first_occurence + 1:]
    return tuple(output)

def run_program():
    start_button = 'esc'
    classic_wordle = False

    # set up Selenium browser
    browser = webdriver.Chrome(ChromeDriverManager().install())
    if classic_wordle:
        browser.get("https://www.powerlanguage.co.uk/wordle/")
    
        # wait to start the program
        keyboard.wait(start_button)
           
        # get game rows
        game_app = browser.find_element(By.TAG_NAME, 'game-app')
        board = browser.execute_script("return arguments[0].shadowRoot.getElementById('board')", game_app)
        game_rows = board.find_elements(By.TAG_NAME, 'game-row')
        
        play(game_rows, browser, get_wordle_guesses(), get_wordle_answers(), classic_wordle)
    else:
        # how many rounds to play
        num_games = 100
        
        browser.get("https://octokatherine.github.io/word-master/")

        # wait to start the program
        keyboard.wait(start_button)
        
        for _ in range(num_games):
            # get game rows
            game_rows = np.array(browser.find_elements(By.TAG_NAME, 'span')).reshape(6, 5)
            
            # guess list and answer list is the same
            play(game_rows, browser, get_wordmaster_guesses(), get_wordmaster_answers(), classic_wordle)
            
            # play again
            time.sleep(2)
            keyboard.press('esc')
            time.sleep(2)
            keyboard.release('esc')
            time.sleep(1)
            browser.find_element(By.XPATH, '//button[text()="Play Again"]').click()
            time.sleep(1)
    keyboard.wait(start_button)

    

