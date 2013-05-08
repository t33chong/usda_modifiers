#!/usr/bin/env python2.7

# This script attempts to isolate the canonical form of each type of food in
# the USDA database, and provide a list of given modifiers for each food.
# The numword module is required for normalize()
# Written by Tristan Euan Chong on 3/18/2013

import os
import re
from numword import cardinal

def normalize(text):
    """Lowercase, strip parenthetical clauses and hyphens, convert numbers to
    words
    """
    text = re.sub('\(.*?\)', '', text.lower())
    text = re.sub('-', ' ', text)
    text = re.sub('([a-z]+)([0-9]+)', '\g<1> \g<2>', text)
    numbers = re.findall('[0-9]+', text)
    if numbers:
        for number in numbers:
            try:
                text = re.sub(number, cardinal(int(number)), text)
            except:
                text = text
    if '%' in text:
        text = re.sub('%', ' percent', text)
    return text

# Create dictionary; key: USDA category number, value: dict
d = {}

# Iterate through lines in USDA FOOD_DES source file
for line in open('FOOD_DES.txt', 'r').readlines():
    # Isolate useful strings
    text = re.match('~[0-9]+~\^~([0-9]+)~\^~([^~]+)~\^~([^~]+)', line)
    category = text.group(1)
    food_string = normalize(text.group(2))
    # Create dict as value of d; key: food canonical form, value: list
    if category not in d:
        d[category] = {}
    # Split string taken from USDA file into separate elements
    food_elements = [x.strip() for x in food_string.split(',')]
    # Create list as value of nested dict, to contain modifiers
    if food_elements[0] not in d[category]:
        d[category][food_elements[0]] = []
    # Populate list with modifiers, avoiding duplicates
    if len(food_elements) > 1:
        for food_element in food_elements[1:]:
            if str(food_element) not in d[category][food_elements[0]]:
                d[category][food_elements[0]].append(str(food_element))
    
# Create dictionary from FD_GROUP file; key: category number, value: category
cat = {}
for line in open('FD_GROUP.txt', 'r').readlines():
    text = re.match('~([0-9]+)~\^~([^~]+)~', line)
    cat_num = text.group(1)
    cat_txt = '_'.join(x for x in re.findall('[A-Z]+', text.group(2).upper()))
    cat[cat_num] = cat_txt

# Define output directory
output_dir = 'modifiers_by_food'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Write facet lists to the appropriate text files
for key in d:
    #output_file = open('%s/%s.txt' % (output_dir, cat[key]), 'w')
    output_file = open(os.path.join(output_dir, '%s.txt' % cat[key]), 'w')
    for entry in d[key]:
        output_file.write('%s\t%s\n' % (entry, ','.join(facet for facet in d[key][entry])))
    output_file.close()

