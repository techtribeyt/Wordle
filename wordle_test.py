import random
from words import get_wordle_guesses, get_wordle_answers
import time 

def run():
    # get the word list
    words = get_wordle_guesses()
    narrowed_down_list = get_wordle_answers()
    
    # real answer - randomly chosen
    answer = random.choice(narrowed_down_list)

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
        narrowed_down_list = evaluation_to_wordlist_map[get_evaluation(answer, chosen_word)]
        
        # once narrowed down to 1, we are done
        if len(narrowed_down_list) == 1:
            return True
    return False
            
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

# returns success probability given n trials
def get_stats(n):
    successes = 0
    for i in range(n):
        print(i)
        successes += run()
    return successes / n

# returns worst case time elapsed
def get_time(n):
    t = 0
    for _ in range(n):
        start_time = time.time()
        run()
        t = max(t, time.time() - start_time)
    return t