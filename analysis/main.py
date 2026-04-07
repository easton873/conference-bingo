from pathlib import Path

def clean_up(word):
    new_word = ""
    for letter in word:
        if letter.isalpha() and letter.isascii():
            new_word += letter.lower()
    return new_word

def to_percentage(thing, total):
    result = {}
    for word in thing:
        result[word] = str(round(thing[word] / total * 100, 2)) + '%'
    return result

def first(thing, num=25):
    result = {}
    for i, word in enumerate(thing):
        if i >= num:
            return result
        result[word] = thing[word]
    return result

# Specify the directory path
directory_path = Path('scrapper/sessions/April 2018')

words = {}
exclusions = [
    'the', 'and', 'of', 'to', 'in', 'a', 'that', 'we', 'i', 'is', 'his', 
    'our', 'he', 'with', 'for', 'you', 'as', 'be', 'it', 'us', 'was', 'are', 'my',
    'by', 'have', 'not', 'this', '', 'will', 'him', 'on', 'your', 'they', 'all', 'or', 'when',
    'from', 'but', 'can', 'one', 'who', 'their', 'do', 'me', 'what', 'at', 'had', 'if', 'has',
    'those', 'each', 'were', 'through', 'about', 'more', 'these', 'things', 'so', 'an',
    'said', 'would', 'may', 'know', 'unto', 'no', 'shall', 'come', 'how', 'there', 'amen',
    'name', 'been', 'like', 'day', 'only', 'which', 'many', 'then', 'm', 'after', 'see'
    'every', 'see', 'before', 'now', 'where', 'because', 'make', 'could', 'other', 'some',
    'even', 'them', 'also', 'out', 'just', 'into', 'words', 'up', 'than', 'being', 'way',
    'upon', 'keep', 'felt', 'another', 'years', 'made', 'feel', 'let', 'again', 'ye', 'over',
    'should', 'did', 'very', 'its', 'does', 'take'
]

total_talks = 0

# Iterate through all .txt files in the directory
for file_path in directory_path.glob('*.txt'):
    with open(file_path, 'r') as file:
        # content = file.read()
        # print(f"Processing: {file_path.name}")
        words_this_talk = []
        total_talks += 1
        for line in file:
            for word in line.split():
                word = clean_up(word)
                if word in exclusions:
                    continue
                if word not in words_this_talk:
                    words_this_talk.append(word)
        for word in words_this_talk:
            if word not in words:
                words[word] = 0
            words[word] += 1
        if 'jesus' not in words_this_talk:
            print(f"{file_path.name}")

print('total talks', total_talks)
words = dict(sorted(words.items(), key=lambda item: item[1], reverse=True))
results = to_percentage(words, total_talks)
print(first(results, 25).keys())
# print(results["music"])