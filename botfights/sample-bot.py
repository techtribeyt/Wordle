# sample-bot.py

# sample bot to play wordle. see wordle.py for how to play.
import random


g_wordlist = None
def get_wordlist():
    global g_wordlist
    if None == g_wordlist:
        g_wordlist = []
        for i in open('wordlist.txt').readlines():
            i = i[:-1]
            g_wordlist.append(i)
    return g_wordlist

def matches(target, guess, feedback):
    for i, ch in enumerate(feedback):
        if feedback[i] == '3':
            if target[i] != guess[i]:
                return False
            target = target[:i] + ' ' + target[i + 1:]
        if guess[i] == target[i] and feedback[i] != '3':
            return False
    for i, ch in enumerate(feedback):
        if feedback[i] == '2':
            if guess[i] not in target:
                return False
            find_index = target.find(guess[i])
            target = target[:find_index] + ' ' + target[find_index + 1:]
    for i, ch in enumerate(feedback): 
        if feedback[i] == '1' and guess[i] in target:
            return False
    return True


def play(state):
    # state looks like: "-----:00000,arose:31112,amend:31211"
    possible = get_wordlist()
    pairs = state.split(',')
    if len(pairs) == 1:
        return "arise"
    
    for pair in pairs:
        guess, feedback = pair.split(':')
        possible = list(filter(lambda x: matches(x, guess, feedback), possible))
        possible = list(set(possible) - {guess})
      
    if len(possible) == 1:
        return possible[0]
    min_wordcount = 1e10
    chosen_word = ""
    # check every word in words_to_consider to see which one gives us most information
    # (allows us to cancel out the most words)
    word_list = random.sample(get_wordlist(), 1000)
    for word_to_guess in word_list:
        temp_eval_to_words_map = {}
        
        # evaluate with every possible answer
        for possible_answer in possible:
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

    return chosen_word
            
    
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
