import csv
from twitter_specials import *
from math import log

posScore_location = {}
class_location = {}
count_class = [0,0,0,0]
word_counts_in_class = [{},{},{},{}]

with open("labeled_corpus.tsv", encoding="utf-8") as csvfile:
    readCSV = csv.reader(csvfile, delimiter='\t')
    for row in readCSV:
        line_arr = list(row)
        
        positivity_class = line_arr[1]
        if positivity_class == 'positive':
            class_index = 0
        elif positivity_class == 'negative':
            class_index = 1
        elif positivity_class == 'neutral':
            class_index = 2
        elif positivity_class == 'irrelevant':
            class_index = 3

        count_class[class_index] += 1

        tweet = line_arr[0]
        
        tweet = clean_tweet(tweet, emo_repl_order, emo_repl, re_repl)
        
        words = tweet.split()
        word_set = set()
        for w in words:
            if '#' not in w and '@' not in w:
                word_set.add(w)
    
        for w in word_set:
            if w not in word_counts_in_class[class_index]:
                word_counts_in_class[class_index][w] = 0
            word_counts_in_class[class_index][w] += 1

csvfile.close()

word_counts_in_class_sorted = [{},{},{},{}]

for i in range(0,4):
    for w,count in (word_counts_in_class[i]).items():
        if count > 1:
            if w not in word_counts_in_class_sorted[i]:
                word_counts_in_class_sorted[i][w] = 0
            word_counts_in_class_sorted[i][w] += count

total_class = count_class[0]+count_class[1]+count_class[2]+count_class[3]
p_class = [log(count_class[0]/total_class),log(count_class[1]/total_class),log(count_class[2]/total_class),log(count_class[3]/total_class)]

with open("geo_twits_squares.tsv", encoding="utf-8") as tsvfile, open("locations_classified.tsv","w") as t:
    readTSV = csv.reader((x.replace('\0', '') for x in tsvfile), delimiter='\t')
    temp = csv.writer(t,delimiter='\t')

    for row in readTSV:
        line_arr = list(row)
        latitude = line_arr[0]
        longitude = line_arr[1]
        tweet = line_arr[2]
        
        words = tweet.split()

        p_class2 = [0,0,0,0] #reset p_class2
        for w in words:
            for i in range(0,4):
                try:
                    count = word_counts_in_class_sorted[i][w]
                except:
                    continue
                p_class2[i] += log(count/count_class[i])

        p_class2 = [x + y for x,y in zip(p_class, p_class2)]
        max_index = p_class2.index(max(p_class2))
        
        if max_index == 0:
            positivity_class2 = 'positive'
        if max_index == 1:
            positivity_class2 = 'negative'
        if max_index == 2:
            positivity_class2 = 'neutral'
        if max_index == 3:
            positivity_class2 = 'irrelevant'
        row[2] = positivity_class2
        temp.writerow(row)

        if (latitude, longitude) not in class_location:
            class_location[(latitude, longitude)] = [0, 0, 0, 0]
        class_location[(latitude, longitude)][max_index] += 1

tsvfile.close()
t.close()

for location, class_count in class_location.items():
    total = class_count[0] + class_count[1]+ class_count[2] +class_count[3]
    score = ((class_count[0] / total - class_count[1] / total) + 1) / 2
    posScore_location[location] = score


file_object = open('./public_html/data.js', 'w', newline='')
file_object.write("var data = [")
count = 0

for (location, score) in posScore_location.items():
    if count == 0:
        file_object.write('{"score": ' + str(score) + ', "g": ' + str(float(location[1])+0.05/2) + ', "t": ' + str(float(location[0])+0.05/2) + '}')
    else:
        file_object.write(', {"score": ' + str(score) + ', "g": ' + str(float(location[1]) + 0.05 / 2) + ', "t": ' + str(float(location[0]) + 0.05 / 2) + '}')
    count += 1

file_object.write('];')
file_object.close()
