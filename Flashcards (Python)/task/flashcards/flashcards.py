import json
import random
import sys
import getopt
import itertools


class Tee:
    def write(self, *args, **kwargs):
        self.out1.append(*args, **kwargs)
        self.out2.write(*args, **kwargs)

    def __init__(self, out1, out2):
        self.out1 = out1
        self.out2 = out2

    def flush(self):
        pass


cards = {}
log_ = []
sys.stdout = Tee(log_, sys.stdout)


def flashcards():
    import_, export_ = '', ''
    opts, args = getopt.getopt(sys.argv[1:], "i:e:", ["import_from=", "export_to="])
    for opt, arg in opts:
        if opt in ("-i", "--import_from"):
            import_ = arg
        elif opt in ("-e", "--export_to"):
            export_ = arg
    if import_:
        try:
            with open(import_, 'r', encoding='utf-8') as f:
                cards_ = json.load(f)
                cards.update(cards_)
                print(f'{len(cards_)} cards have been loaded.')
        except FileNotFoundError:
            print('File not found.')
    while True:
        action = input('Input the action (add, remove, import, export, ask, exit, log, '
                       'hardest card, reset stats):\n').lower()
        log_.append(action)
        match action:
            case 'exit':
                if export_:
                    with open(export_, 'w', encoding='utf-8') as f:
                        json.dump(cards, f, ensure_ascii=False, indent=4)
                        print(f'{len(cards)} cards have been saved.')
                else:
                    print('Bye bye!')
                return None
            case 'add':
                term = input('The card:\n')
                log_.append(term)
                while term in cards:
                    term = input(f'The term "{term}" already exists. Try again:\n')
                    log_.append(term)
                definition = input('The definition for card:\n')
                log_.append(definition)
                while definition in list(itertools.chain.from_iterable(cards.values())):
                    definition = input(f'The definition "{definition}" already exists. Try again:\n')
                    log_.append(definition)
                cards[term] = [definition, 0]
                print(f'The pair ("{term}":"{definition}") has been added.')
            case 'remove':
                term = input('Which card?\n')
                log_.append(term)
                if term in cards:
                    cards.pop(term)
                    print('The card has been removed.')
                else:
                    print(f'Can\'t remove "{term}": there is no such card.')
            case 'import':
                file_name = input('File name:\n')
                log_.append(file_name)
                try:
                    with open(file_name, 'r', encoding='utf-8') as f:
                        cards_ = json.load(f)
                        cards.update(cards_)
                        print(f'{len(cards_)} cards have been loaded.')
                except FileNotFoundError:
                    print('File not found.')
            case 'export':
                file_name = input('File name:\n')
                log_.append(file_name)
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(cards, f, ensure_ascii=False, indent=4)
                    print(f'{len(cards)} cards have been saved.')
            case 'ask':
                num_cards = int(input('How many times to ask?\n'))
                log_.append(str(num_cards))
                for num in range(num_cards):
                    key = random.choice(list(cards))
                    answer = input(f'Print the definition of "{key}":\n')
                    log_.append(answer)
                    if answer == cards[key][0]:
                        print('Correct!')
                    elif answer in list(itertools.chain.from_iterable(cards.values())):
                        right_key = ''
                        for k, v in cards.items():
                            if answer in v:
                                right_key = k
                        print(f'Wrong. The right answer is "{cards[key][0]}", but your definition is correct '
                              f'for "{right_key}"')
                        cards[key][1] += 1
                    else:
                        print(f'Wrong. The right answer is "{cards[key][0]}".')
                        cards[key][1] += 1
            case 'log':
                file_name = input('File name:\n')
                log_.append(file_name)
                with open(file_name, 'w') as f:
                    for lines in log_:
                        if lines:
                            f.write(lines + '\n')
                    print('The log has been saved.')
            case 'hardest card':
                hardest_card = []
                mistakes = 0
                for term in cards:
                    if cards[term][1] > mistakes:
                        mistakes = cards[term][1]
                        hardest_card = [term]
                    elif cards[term][1] == mistakes:
                        hardest_card.append(term)
                if mistakes == 0:
                    print('There are no cards with errors.')
                elif len(hardest_card) == 1:
                    print(f'The hardest card is "{hardest_card[0]}". You have {mistakes} errors answering it.')
                else:
                    hardest_card = '", "'.join(hardest_card)
                    print(f'The hardest cards are "{hardest_card}". You have {mistakes} errors answering it.')
            case 'reset stats':
                for term in cards:
                    cards[term][1] = 0
                print(f'Card statistics have been reset.')
            case _:
                print('Invalid input.')


flashcards()
