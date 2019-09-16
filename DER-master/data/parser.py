# In[1]:


import json
import csv
import pickle
import re
import numpy as np
from collections import defaultdict
filename_input = 'reviews_Automotive_5.json'
# Load the raw data
raw_data = [json.loads(line) for line in open(filename_input, 'r')]


# In[2]:


# Generate id_user_dict/id_item_dict/id_word_dict
users = set()
items = set()
vocab = set()
max_interaction_length = 0
for line in raw_data:
    UserID = line['reviewerID']
    ItemID = line['asin']
    sentence = re.sub(r'[^\w\s]|\d','',line['reviewText'].lower())
    words = [word for word in  sentence.split()]
    if len(words) > max_interaction_length:
        max_interaction_length = len(words)
    users.add(UserID)
    items.add(ItemID)
    for word in words:
        vocab.add(word)
id_user_dict = dict(zip(range(len(users)), users))
id_item_dict = dict(zip(range(len(items)), items))
id_word_dict = dict(zip(range(len(vocab)), vocab))
word_id_dict = dict(zip(vocab,range(len(vocab))))
with open('id_user_dict', 'wb') as f:
    pickle.dump(id_user_dict, f)
with open('id_item_dict', 'wb') as f:
    pickle.dump(id_item_dict, f)
with open('id_word_dict', 'wb') as f:
    pickle.dump(id_word_dict, f)


# In[3]:


print('length of id_user_dict:',len(id_user_dict))
print('length of id_item_dict:',len(id_item_dict))
print('length of id_word_dict:',len(id_word_dict))


# In[4]:


def get_key_by_value(value,D):
    id = list(D.values()).index(value)
    return list(D.keys())[id]


# In[5]:


"""
item_reviews
    Key: ItemID 
    Value: All the user reviews received by the Item
user_item_review
    Key: UserID@ItemID 
    Value: review from the user to the item
user_purchased_items
    Key: UserID
    Value: list of purchasedID
"""
item_real_reviews = defaultdict(list)
user_item_review = defaultdict(list)
user_purchased_items = defaultdict(list)
for line in raw_data:
    # Turn the original ID into the index in the dictionary
    UserID = get_key_by_value(line['reviewerID'], id_user_dict)
    ItemID = get_key_by_value(line['asin'], id_item_dict)
    item_real_reviews[ItemID].append(line)
    UserItem = '{}@{}'.format(UserID,ItemID)
    user_item_review[UserItem].append(line)
    user_purchased_items[UserID].append(ItemID)
with open('item_real_reviews', 'wb') as f:
    pickle.dump(item_real_reviews, f)
with open('item_reviews', 'wb') as f:
    pickle.dump(item_real_reviews, f)
with open('user_item_review', 'wb') as f:
    pickle.dump(user_item_review, f)
with open('train_user_purchased_items', 'wb') as f:
    pickle.dump(user_purchased_items, f)    
with open('validation_user_purchased_items', 'wb') as f:
    pickle.dump(user_purchased_items, f)        
with open('test_user_purchased_items', 'wb') as f:
    pickle.dump(user_purchased_items, f)        


# In[6]:


def parseStr(review):
    ItemID = get_key_by_value(review['asin'], id_item_dict)
    rating = review['overall']
    time = review['unixReviewTime']
    word_ids = []
    review_text = re.sub(r'[^\w\s]|\d','',review['reviewText'].lower())
    for word in review_text.split():
        word_id = word_id_dict[word]
        word_ids.append(str(word_id)) 
    return '{}||{:1}||'.format(ItemID,rating)+'::'.join(word_ids)+"||{}".format(time)

train = []
validation = []
test = []
for UserID in range(len(id_user_dict)):
    items = user_purchased_items[UserID]
    if UserID % 100 == 0:
        print('Processing {}/{}'.format(UserID,len(id_user_dict)))
    reviews = []
    for ItemID in items:
        UserItem = '{}@{}'.format(UserID,ItemID)
        reviews.append(user_item_review[UserItem][0])
    reviews_sorted = sorted(reviews, key=lambda k: k['unixReviewTime']) 
    for i in range(2,len(reviews_sorted)):
        target_review = reviews_sorted[i]
        pre_review = reviews_sorted[i-1]
        pre_pre_review = reviews_sorted[i-2]
        row = '{}&&'.format(UserID)+parseStr(pre_review)+'()'+parseStr(pre_pre_review)+'&&'+parseStr(target_review)
        if i < len(reviews_sorted) - 2:
            train.append(row)
        elif i == len(reviews_sorted) - 2:
            test.append(row)
        elif i == len(reviews_sorted) - 1:
            validation.append(row)
print('Done!')


# In[7]:


# Save output
with open('train_ided_whole_data', 'w') as out_file:
    out_file.write('\n'.join(train))
with open('validation_ided_whole_data', 'w') as out_file:
    out_file.write('\n'.join(validation))    
with open('test_ided_whole_data', 'w') as out_file:
    out_file.write('\n'.join(test))
with open('train_validation_ided_whole_data', 'w') as out_file:
    out_file.write('\n'.join(train+validation)) 


# In[9]:


data_statistics = {
    'max_interaction_length': max_interaction_length,
    'interaction_num': len(raw_data),
    'max_sentence_length': 1,
    'max_sentence_word_length': max_interaction_length,
    'time_bin_number': 1,
    'user_num': len(id_user_dict),
    'item_num': len(id_item_dict),
    'word_num': len(id_word_dict)
}
with open('data_statistics', 'wb') as f:
    pickle.dump(data_statistics, f)


# In[ ]:




