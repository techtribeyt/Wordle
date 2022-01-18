# wordle.py -- botfights harness for wordle


USAGE = '''\
This is a harness to write bots that play wordle.

See: https://www.powerlanguage.co.uk/wordle/

To play against the computer:

   $ python wordle.py human

To test a bot named "play" in "sample-bot.py" against the word "apple":

   $ python wordle.py word wordlist.txt sample-bot.play apple

To test against 1000 random words in wordlist "wordlist.txt":

   $ python wordle.py bot wordlist.txt sample-bot.play 1000

To play your bot on botfights.io in the "test" event, where XXXX and YYYYYYYYY
are your credentials:

   $ python wordle.py botfights sample-bot.play XXXXX YYYYYYYYYY test

To enter your bot in the "botfights_i" event:

   $ python wordle.py botfights sample-bot.play XXXXX YYYYYYYYYY botfights_i

'''


import sys, importlib, random, time

import requests


MAGIC = 'WORDLE'


g_random = None
def get_random():
    global g_random
    if None == g_random:
        g_random = random.Random(MAGIC)
    return g_random


def load_wordlist(fn):
    a = set()
    for i in open(fn).readlines():
        a.add(i[:-1])
    return a


def load_bot(s):
    fn, func = s.split('.')
    module = importlib.import_module(fn)
    bot = getattr(module, func)
    return bot


def get_play(bot, history):
    state = ','.join(map(lambda x: '%s:%s' % (x[0], x[1]), history))
    response = bot(state)
    return response


def calc_score(secret, guess, wordlist):
    if not guess in wordlist:
        return '0' * len(secret)

    a = ['0'] * len(secret)
    secret_arr = [char for char in secret]

    # First pass of the guess, to find any that match exactly
    for i, ch in enumerate(secret_arr):
        g = '-'
        if i < len(guess):
            g = guess[i]
        if ch == g:
            a[i] = '3'
            secret_arr[i] = ' '

    # Second pass to score the rest, without re-using the secret letters more than once
    for i, ch in enumerate(secret_arr):
        if a[i] == '3':
            continue
        g = '-'
        if i < len(guess):
            g = guess[i]

        if g in secret_arr:
            idx = secret_arr.index(g)
            secret_arr[idx] = ' '
            a[i] = '2'
        else:
            a[i] = '1'

    return ''.join(a)


def play_word(bot, secret, wordlist):
    guess = '-' * len(secret)
    score = calc_score(secret, guess, wordlist)
    history = [(guess, score), ]
    guess_num = 1
    while 1:
        guess = get_play(bot, history)
        score = calc_score(secret, guess, wordlist)
        history.append((guess, score))
        sys.stdout.write('PLAY\t%d\t%s\t%s\t%s\n' % (guess_num, secret, guess, score))
        if guess == secret:
            return guess_num
        if guess_num == len(wordlist):
            return guess_num
        guess_num += 1


def play_bots(bots, wordlist, n):
    total_guesses = {}
    total_time = {}
    last_guesses = {}
    bot_keys = sorted(list(bots.keys()))
    for i in bot_keys:
        total_guesses[i] = 0
        total_time[i] = 0.0
    if 0 == n:
        count = len(wordlist)
    else:
        count = n
    wordlist_as_list = sorted(list(wordlist))
    for i in range(count):
        if 0 == n:
            word = wordlist_as_list[i]
        else:
            word = get_random().choice(wordlist_as_list)
        for bot in bot_keys:
            t0 = time.time()
            guesses = play_word(bots[bot], word, wordlist)
            last_guesses[bot] = guesses
            t = time.time() - t0
            total_guesses[bot] += guesses
            total_time[bot] += t
            i += 1
            sys.stdout.write('WORD\t%d\t%s\t%s\t%d\t%.3f\t%.3f\t%.3f\n' % (i, word, bot, guesses, total_guesses[bot] / float(i), t, total_time[bot] / float(i)))
        if 1 != len(bots):
            bots_sorted = sorted(bot_keys, key = lambda x: total_guesses[x])
            sys.stdout.write('BOTS\t%d\t%s\t%s\n' % (i, word, '\t'.join(map(lambda x: '%s:%d,%.3f' % (x, last_guesses[x], total_guesses[x] / float(i)), bots_sorted))))
    return n


def play_human(secret, wordlist):
    guess_num = 0
    guess = '-' * len(secret)
    while 1:
        score = calc_score(secret, guess, wordlist)
        sys.stdout.write('guess_num: %d, last_guess: %s, last_score: %s\n' % (guess_num, guess, score))
        sys.stdout.write('Your guess?\n')
        guess = sys.stdin.readline().strip()
        guess_num += 1
        if guess == secret:
            break
    sys.stdout.write('Congratulations! You solved it in %d guesses.\n' % guess_num)
    return guess_num


def play_botfights(bot, username, password, event):
    print('Creating fight on botfights.io ...')
    payload = {'event': event}
    r = requests.put('https://api.botfights.io/api/v1/game/wordle/', auth=(username, password), json=payload)
    fight = r.json()
    fight_id = fight['fight_id']
    feedback = fight['feedback']
    print('Fight created: https://botfights.io/fight/%s' % fight_id)
    history = {}
    for i, f in feedback.items():
        history[i] = [['-' * len(f), f], ]
    round_num = 0
    while 1:
        guesses = {}
        for i, f in feedback.items():
            if '33333' == f:
                continue
            history[i][-1][1] = f
            guess = get_play(bot, history[i])
            guesses[i] = guess
            history[i].append([guess, None])
        payload = {'guesses': guesses}
        round_num += 1
        print('Round %d, %d words to go ...' % (round_num, len(guesses)))
        time.sleep(1.0)
        r = requests.patch('https://api.botfights.io/api/v1/game/wordle/%s' % fight_id, auth=(username, password), json=payload)
        response = r.json()
        feedback = response['feedback']
        if 'score' in response:
            score = int(response['score'])
            print('Fight complete. Final score: %d' % score)
            break


def main(argv):
    if 0 == len(argv):
        print(USAGE)
        sys.exit()
    c = argv[0]
    if 0:
        pass
    elif 'human' == c:
        if 1 < len(argv):
            wordlist = load_wordlist(argv[1])
        else:
            wordlist = load_wordlist('wordlist.txt')
        secret = get_random().choice(list(wordlist))
        if 2 == len(argv):
            secret = argv[2]
        x = play_human(secret, wordlist)
        return x
    elif 'help' == c:
        print(USAGE)
        sys.exit()
    elif 'score' == c:
        wordlist = load_wordlist(argv[1])
        secret = argv[2]
        guess = argv[3]
        x = calc_score(secret, guess, wordlist)
        print(x)
    elif 'bot' == c:
        fn_wordlist = argv[1]
        bot = load_bot(argv[2])
        n = 0
        if 4 <= len(argv):
            n = int(argv[3])
        if 5 <= len(argv):
            get_random().seed(argv[4])
        wordlist = load_wordlist(fn_wordlist)
        x = play_bots({argv[2]: bot}, wordlist, n)
        return x
    elif 'bots' == c:
        fn_wordlist = argv[1]
        n = int(argv[2])
        get_random().seed(argv[3])
        bots = {}
        for i in argv[4:]:
            bots[i] = load_bot(i)
        wordlist = load_wordlist(fn_wordlist)
        x = play_bots(bots, wordlist, n)
        return x
    elif 'word' == c:
        fn_wordlist = argv[1]
        bot = load_bot(argv[2])
        secret = argv[3]
        wordlist = load_wordlist(fn_wordlist)
        x = play_word(bot, secret, wordlist)
        return x
    elif 'botfights' == c:
        bot = load_bot(argv[1])
        username, password, event = argv[2:5]
        play_botfights(bot, username, password, event)
    else:
        print(USAGE)
        sys.exit()


if __name__ == '__main__':
    x = main(sys.argv[1:])
    sys.exit(x)

