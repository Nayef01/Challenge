from flask import Flask, request, jsonify
from flask_cors import CORS
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import Credentials
import re
import ast
from collections import defaultdict

# Create a Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

#==================================
# Credentials and connecting to Allam
#==================================

credentials = {
    "url": "https://eu-de.ml.cloud.ibm.com",
    "apikey": "fZbYWl96jE3SPfQ_els_H6wo1gN0QDDhyFXvtBWtdcbM"
}

project_id = "25b35d48-be1f-4dec-8c2f-239f963c272a"

parameters = {
    "DECODING_METHOD" : "greedy",
    "MIN_NEW_TOKENS" : 1,
    "MAX_NEW_TOKENS" : 100,
    "repetition_penalty": 1
}

model = Model(
    model_id="sdaia/allam-1-13b-instruct",
    params=parameters,
    credentials=credentials,
    project_id="25b35d48-be1f-4dec-8c2f-239f963c272a"
)

#==================================
# Defining Varaibles
#==================================


replace_specific_words_Array = []
check_al_type_shams_Array = []
check_al_type_qamar_Array = []
check_and_remove_alif_Array = []
modify_words_with_haa_Array = []
modify_words_with_meem_Array = []
replace_tanween_Array = []
replace_shaddah_Array = []
remove_vowel_with_sukun_Array = []
replace_alif_madda_Array = []
modify_endings_Array = []
remove_alif_if_ends_with_wa_Array = []

exceptions_list =  [
    "هذا",
    "هذه",
    "هذان",
    "هؤلاء",
    "أولئك",
    "ذلك",
    "ذلكم",
    "الله",
    "الرحمن",
    "لكن",
    "لكن",
    "طه",
    "يس",
    "داود",
    "أولو",
    "أولات",
    "أولئك",
    "عمرو"
]

separated_words = ""


#==================================
# Defining pipeline and functions
#==================================

def strip_harakat(word):

    harakat_pattern = r'[\u064B-\u0652]'
    return re.sub(harakat_pattern, '', word)

def reapply_harakat(original, modified):

    result = []
    j = 0  # Pointer for the modified word

    # Iterate over each character in the original word
    for i, char in enumerate(original):
        # If the character is a harakat, add it to the result directly
        if re.match(r'[\u064B-\u0652]', char):
            # Add the harakat only if the last letter in the result matches the current letter in the original word
            if result and result[-1] == original[i - 1]:
                result.append(char)
        else:
            # Check if the letter is still present in the modified word
            if j < len(modified) and char == modified[j]:
                result.append(char)  # Add the letter
                j += 1  # Move to the next letter in the modified word
            # If the letter is not present in the modified word, it is skipped

    return ''.join(result)


def extract_first_char_and_harakat(text):
    if text:
        # Get the first character
        first_char = text[0]

        # Check if there's a harakat immediately following the first character
        harakat_pattern = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
        if len(text) > 1 and harakat_pattern.match(text[1]):
            first_char += text[1]  # Append the harakat to the first character

        return first_char

def extract_array(response_text):
    # Try to extract the array part directly from the response text
    try:
        # Look for any valid Python list inside the response text
        start_index = response_text.find("[")
        end_index = response_text.find("]", start_index) + 1
        if start_index != -1 and end_index != -1:
            array_str = response_text[start_index:end_index]
            # Safely evaluate the array string into a Python list
            array = ast.literal_eval(array_str)
            if isinstance(array, list):
                return array
    except (ValueError, SyntaxError):
        pass
    # Return an empty list if parsing fails
    return []

def check_and_remove_all_qamr(word):
    """
    Checks if the word has the "ال" prefix (definite article) with Tashkeel.
    If the conditions are met, removes the "ا" and its Tashkeel (if present) and returns the modified word.
    If conditions aren't met, returns the original word.
    """
    # Check if the word starts with "ال" (including possible Tashkeel on "ا")
    if word.startswith("اْلْ") or re.match(r'^[\u0617-\u061A\u064B-\u0652]?ال', word):
        # print("yes")
        # Generate the prompt using the full word
        prompt_one = f"""
        [INST]
        هل ال التعريف في الكلمة التالية قمرية؟ اجب فقط بكلمة واحدة
        {word}
        [/INST]"""

        # Simulate the model response (replace this with your model's generate_text call)
        generated_response_one = model.generate_text(prompt=prompt_one, guardrails=False)
        print(generated_response_one)

        # If the response is affirmative, remove only the "ا" and its Tashkeel
        if "نعم" in generated_response_one:
            # Remove the "ا" and its Tashkeel (if present)
            modified_word = re.sub(r'^[\u0627\u0671][\u0617-\u061A\u064B-\u0652]?', '', word, count=1)
            return modified_word

    # Return the original word if conditions aren't met
    return word

def check_and_remove_all_shms(word):
    """
    Checks if the word has the "ال" prefix (definite article) for solar letters.
    If the conditions are met, removes the "ال" and returns the rest of the word with its Tashkeel.
    """
    # Check if the word starts with "ال" (including potential Tashkeel)
    if word.startswith("ال") or re.match(r'^[\u0617-\u061A\u064B-\u0652]?ال', word):
        # Generate the prompt using the full word
        prompt_one = f"""
        [INST]
        هل ال التعريف في الكلمة التالية شمسية؟ اجب فقط بكلمة واحدة
        {word}
        [/INST]"""

        # Simulate the model response (replace this with your model's generate_text call)
        generated_response_one = model.generate_text(prompt=prompt_one, guardrails=False)
        print(generated_response_one)

        # If the response is affirmative, remove "ال" and any Tashkeel attached to it
        if "نعم" in generated_response_one:
            # Remove "ال" and any Tashkeel following "ل"
            modified_word = re.sub(r'^ال[\u0617-\u061A\u064B-\u0652]?', '', word, count=1)
            return modified_word

    # Return the original word if conditions aren't met
    return word

def extract_first_harakah(word):
    # Regular expression to find the first harakah after the first letter
    match = re.search(r'^[^\u064B-\u0652]*([\u064B-\u0652])', word)
    return match.group(1) if match else None

def remove_last_two_chars(word):
    # Return the word excluding the last two characters
    return word[:-2] if len(word) >= 2 else ''

def remove_vowel_with_sukun(text,fulltext):
    """
    Detects 'و', 'ا', or 'ي' with Sukun and removes it if the next non-space letter also has Sukun.

    Args:
    text (str): The input Arabic text.

    Returns:
    str: The modified text with specific vowels with Sukun removed.
    """
    # print("Nein")
    # print(fulltext)
    modified_text = ""
    i = 0
    while i < len(text):
        # Check if the current character is 'و', 'ا', or 'ي' with Sukun
        if i + 1 < len(text) and text[i] in "ىواي" and text[i + 1] == 'ْ':
            # Look ahead to find the next non-diacritic character
            j = i + 2
            while j < len(text) and text[j] in "ًٌٍَُِ ":
                j += 1

            # Check if the next significant character has Sukun
            if j < len(text) - 1 and text[j + 1] == 'ْ':
                # Skip 'و', 'ا', or 'ي' with Sukun
                i += 2  # Skip the letter and its Sukun
                continue

        # If not removed, add the current character to the modified text
        modified_text += text[i]
        i += 1

    if extract_first_harakah(fulltext) == "ْ":
        #print("allam")
        return remove_last_two_chars(text)

    return modified_text

def check_and_remove_alif(word):
    """
    Checks if the word contains 'ا' or 'اْ' as the first or second letter only and applies a condition.

    If the condition is met, 'ا' is removed; otherwise, the word remains unchanged.

    Args:
    word (str): The input Arabic word.

    Returns:
    str: The modified word with 'ا' or 'اْ' removed if the condition is met, or the original word.
    """
    # Check if "ا" or "اْ" is the first or second letter only
    # print("check_and_remove_alif input ->", word)
    # print("word[0] ->", word[0])
    # print("word[1] ->", word[1])

    if len(word) > 1 and (word[0] == "ا" or (len(word) > 2 and word[1] == "ا")):
        # Generate the prompt using the word
        # prompt_one = f"[INST] هل الالف في كلمة '{word}' تربطها بالكلمة التي قبلها؟ جاوب حصرا بكلمة واحدة [/INST]"
        prompt_one = f"[INST] هل 'اْ' في كلمة '{word}' تربطها بالكلمة التي قبلها؟ جاوب حصرا بكلمة واحدة [/INST]"

        # prompt_one = f"[INST] هل الالف في كلمة '{word}' تصلها بالكلمة التي قبلها؟ جاوب حصرا بكلمة واحدة [/INST]"
        # print("prompt_one: ", prompt_one)
        # Simulate the model response (replace this with your model's generate_text call)
        generated_response_one = model.generate_text(prompt=prompt_one, guardrails=True)
        # print(generated_response_one)

        if "نعم" in generated_response_one:
            print("im in")
            # Check and remove "ا" only if it's the first or second letter
            if len(word) > 0 and word[0] == "ا":
                word = word[1:]  # Remove "ا" if it's the first character
            elif len(word) > 1 and word[1] == "ا":
                word = word[0] + word[2:]  # Remove "ا" if it's the second character

    return word

def replace_tanween(text):
    """
    Replaces Arabic Tanween diacritics with corresponding transformations.
    """
    text = text.replace("ًا", "نَ")
    text = text.replace("اً", "َنْ")  # Replace Alif with Fatha Tanween
    text = text.replace("ً", "َنْ")   # Replace Fatha Tanween
    text = text.replace("ٌ", "ُنْ")   # Replace Damma Tanween
    text = text.replace("ٍ", "ِنْ")   # Replace Kasra Tanween

    if "ة" in strip_harakat(text):
        text = re.sub(r"(ة)([\u064B-\u0652]*)", r"ت\2", text)

    return text

def process_text_bhoor(text):
    # Define the Unicode range for Arabic diacritics
    harakah_pattern = r'[\u064B-\u0652]'
    sukoon = "ْ"

    # Result string to build the output
    result = ""

    # Iterate through each character in the text
    i = 0
    while i < len(text):
        char = text[i]

        if char == "/":
            result += " / "
        elif char == " ":
            # Skip spaces
            i += 1
            continue
        else:
            # Check if the next character is a harakah
            if i + 1 < len(text) and re.match(harakah_pattern, text[i + 1]):
                harakah = text[i + 1]
                if harakah == sukoon:
                    result += "○"
                else:
                    result += "│"
                # Move past the harakah character
                i += 1
            else:
                # No harakah, so we add "○"
                result += "○"

        i += 1

    # Reverse the result to match right-to-left reading order
    return result[::-1]

def replace_shaddah(text):
    """
    Replaces Arabic Shaddah with the letter it is on, duplicated with Sukun and the original Harakah.

    Args:
    text (str): The input Arabic text.

    Returns:
    str: The modified text with Shaddah replaced.
    """
    result = []
    i = 0
    while i < len(text):
        if text[i] == 'ّ':  # Check for Shaddah
            # Find the character and the Harakah before Shaddah
            char_index = i - 1
            if char_index >= 0 and text[char_index] not in "ًٌٍَُِْ":  # Ensure char_index points to a letter
                char = text[char_index]
                harakah = text[char_index + 1] if (char_index + 1 < i and text[char_index + 1] in "ًٌٍَُِ") else ''

                # Construct replacement: original char with Sukun, then char with original Harakah
                replacement = f"{char}ْ{char}{harakah}"

                # Remove the last character from result (the original char with shaddah)
                result.pop()
                result.append(replacement)
            i += 1  # Move past the Shaddah
        else:
            result.append(text[i])
            i += 1
    if "ة" in text:
        text = re.sub(r"(ة)([\u064B-\u0652]*)$", r"ت\2", text)
    return ''.join(result)

def replace_alif_madda(text):# مَآذِنُ
    """
    Replaces the Arabic Alif Madda (آ) with Alif Hamza (أ) followed by Alif with Sukun (اْ).

    Args:
    text (str): The input Arabic text.

    Returns:
    str: The modified text with آ replaced by أاْ.
    """
    return text.replace("آ", "أاْ")

def strip_harakat(word):
    # Define a regular expression pattern to match all Arabic harakat
    harakat_pattern = r'[\u064B-\u0652]'
    # Remove all harakat from the word
    return re.sub(harakat_pattern, '', word)

def replace_specific_words(text): #لكن و لكن
    """
    Replaces specific Arabic words with their transformed forms.

    Args:
    text (str): The input Arabic text.

    Returns:
    str: The modified text with specific words replaced.
    """

    replacements = {
        "هذا": "هَاْذَاْ",
        "هذه": "هَاْذِهِ",
        "هذان": "هَاْذَاْنْ",
        "هؤلاء": "هَاْؤُلَاْءْ",
        "أولئك": "أُلَاْئِكْ",
        "ذلك": "ذَاْلِكْ",
        "ذلكم": "ذَالِكُمْ",
        "الله": "اْلْلَاْهْ",
        "الرحمن": "ارْرَحْمَاْنْ",
        "لَكِنْ": "لَاْكِنْ",
        "لَكِنَّ": "لَاْكِنْنَ",
        "طه": "طَاْهَاْ",
        "داود": "دَاْوُوْدْ",
         "أولو": "أُلُو" ,
        "أولات":" أُلَاتُ" ,
        "أولئك": "أُلَائِكَ" ,
        "عمرو":"عَمَرُن"
    }
    var1 = "يس"
    var2 = "يَاْسِيْنُ"
    if text == var1:
        print("hi")
        text = text.replace(var1,var2)
        return text
    # Replace each word in the text based on the replacements dictionary
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)

    return text

def check_al_type(word):
    solar_letters = "تثدذرزسشصضطظلن"
    lunar_letters = "ابجحخعغفقكمهوي"

    if word.startswith("ال"):
        # Get the first letter after "ال"
        first_letter = word[2]

        if first_letter in solar_letters:
            # Remove the initial "ال" for "شمسية"
            return word[2:], "شمسية"
        elif first_letter in lunar_letters:
            # Remove only the initial "ا" for "قمرية"
            return word[1:], "قمرية"
        else:
            return word, "غير محدد"  # Return as-is if it's neither "شمسية" nor "قمرية"
    else:
        return word, "غير محدد"   # Return as-is if it doesn't start with "ال"


def modify_words_with_haa(text,full_text): #do not check the last word of the poem
    prompt_one = f"""[INST]اجب حصرا بنعم او لا بدون اي كلمة اخرى: هل الهاء في الجملة التالية هي هاء الغائب؟
    {full_text}[/INST]"""
    prompt_two = f"""[INST]اجب حصرا بنعم او لا بدون اي كلمة اخرى: هل هاء الغائب في الكلمة التالية مشبعة؟
    {full_text}[/INST]"""
    generated_response_one = model.generate_text(prompt=prompt_one, guardrails=False)
    generated_response_two = model.generate_text(prompt=prompt_two, guardrails=False)
    # print(generated_response_one)
    # print(generated_response_two)
    if ("نعم" in generated_response_one and "نعم" in generated_response_two):
        """
        Modifies words containing 'ه' based on the presence of Dammah or Kasra:

        - Adds "و" after "ه" if it has a Dammah.
        - Adds "ي" after "ه" if it has a Kasra.

        Args:
        text (str): The input Arabic text.

        Returns:
        str: The modified text with changes applied to words containing 'ه' with Dammah or Kasra.
        """
        # Replace 'هُ' with 'هُو' and 'هِ' with 'هِي'
        text = re.sub(r'(هُ)(?!و)', r'\1و', text)
        text = re.sub(r'(هِ)(?!ي)', r'\1ي', text)

        return text
    else:
        return text

def modify_endings(text):
    """
    Modifies the ending of each word in the text:

    - Adds "ي" after a word ending with Kasra ( ِ ).
    - Adds "و" after a word ending with Dammah ( ُ ).

    Args:
    text (str): The input Arabic text.

    Returns:
    str: The modified text with changes applied to words ending in Kasra or Dammah.
    """
    if "ة" in strip_harakat(text):
        text = re.sub(r"(ة)([\u064B-\u0652]*)", r"ت\2", text)

    if text.endswith("ِ"):
        # print("ja1")
        text = text + "ي"
    elif text.endswith("ُ"):
        # print("ja2")
        text = text + "و"
    else:
        # print("ja3")
        text = text
    return text

def remove_alif_if_ends_with_wa(text):
    prompt_one = f"""[INST]اجب حصرا بنعم او لا بدون اي كلمة اخرى: هل الواو التالية هي واو الجماعة؟
    {text}[/INST]"""
    prompt_two = f"""[INST]اجب حصرا بنعم او لا بدون اي كلمة اخرى: هل الالف في الكلمة التالية هي الالف الفارقة بعد واو الجماعة؟
    {text}[/INST]"""
    generated_response_one = model.generate_text(prompt=prompt_one, guardrails=False)
    generated_response_two = model.generate_text(prompt=prompt_two, guardrails=False)

    if ("نعم" in generated_response_one and "نعم" in generated_response_two):
        modified_words = []

            # Check if the word ends with the exact sequence "وا"
        if text.endswith("وا"):
            modified_word = text[:-1]  # Remove the last character "ا"
        else:
            modified_word = text

        modified_words.append(modified_word)

        # Join the modified words back into a single string
    return ' '.join(modified_words)

def modify_words_with_meem(text,full_text): #do not check the last word of the poem
    prompt_one = f"""[INST]اجب حصرا بنعم او لا بدون اي كلمة اخرى: هل الميم في الجملة التالية هي ميم الجماعة؟
    {full_text}[/INST]"""
    prompt_two = f"""[INST]اجب حصرا بنعم او لا بدون اي كلمة اخرى: هل حركة ميم الجماعة في الجملة التالية مشبعة؟
    {full_text}[/INST]"""
    generated_response_one = model.generate_text(prompt=prompt_one, guardrails=False)
    generated_response_two = model.generate_text(prompt=prompt_two, guardrails=False)

    if ("نعم" in generated_response_one and "نعم" in generated_response_two):
        """
        Modifies words containing 'م' based on the presence of Dammah or Kasra:

        - Adds "و" after "ه" if it has a Dammah.
        - Adds "ي" after "ه" if it has a Kasra.

        Args:
        text (str): The input Arabic text.

        Returns:
        str: The modified text with changes applied to words containing 'م' with Dammah or Kasra.
        """
        # Replace 'هُ' with 'هُو' and 'هِ' with 'هِي'
        text = re.sub(r'(مُ)(?!و)', r'\1و', text)
        text = re.sub(r'(مِ)(?!ي)', r'\1ي', text)

        return text
    else:
        return text

def split_sentence(sentence):
    # Split the sentence by spaces and return the result as a list of words
    return sentence.split()

def extract_and_index_poem(text):
    """
    Extracts the two halves of a poem line from a given text and assigns specific indexes to each half and each word.
    Handles various separators including single or multiple forward slashes.
    """
    # Remove any introductory text to isolate the poem text only
    # Make the introductory phrase optional in the regex
    poem = re.sub(r'^(?:.*كتابة عروضية[:،\s]*)?', '', text)

    # Define potential separators between the two halves
    separators = [
        ' … ', '\.{2,}',  # Handle dots
        '/+',  # Handle one or more slashes
        '\n+',  # Handle one or more newlines
        'الشطر الاول:', 'الشطر الثاني:',
        ' {2,}',
        '\t+',               # One or more tabs
        '(\.\s)+'            # Dot followed by a space, repeated
    ]

    # Create a regex pattern that matches any of the separators
    separator_pattern = '|'.join(separators)

    # Replace all potential separators with a single separator
    poem = re.sub(f'({separator_pattern})', '/', poem.strip())

    # Remove any extra slashes that might have been created
    poem = re.sub(r'/+', '/', poem)

    # Split the text into two halves based on the separator
    halves = poem.split('/', 1)

    if len(halves) < 2:
        return "The input does not contain two halves of a poem."

    # Process each half to give it a specific index
    indexed_parts = {}
    for i, half in enumerate(halves, start=1):
        # Remove any additional labels and clean the text
        half = re.sub(r'^(الشطر الأول|الشطر الثاني)[:\s]*', '', half)
        half = half.strip()  # Remove leading/trailing whitespace
        words = half.split()

        # Create indexes for words within each half
        indexed_words = {f'word_{i}{j+1}': word for j, word in enumerate(words[:-1])}
        indexed_words[f'end_{i}'] = words[-1] if words else ''
        indexed_parts[f'part_{i}'] = indexed_words

    # Initialize an empty 2D array
    output = []

    # Loop through each part and create a sublist for each
    for part in ['part_1', 'part_2']:
        words = list(indexed_parts[part].values())
        output.append(words)  # Append each part's words as a sublist

    return output

def parse_arabic_sentence(sentence):
    # Step 1: Get the part after '&&'
    if ":" in sentence:
        sentence = sentence.split(":")[1].strip()

    # Step 2: Split the sentence by '/' to form the first dimension
    parts = sentence.split(" / ")

    # Step 3: Split each part by spaces to form the second dimension
    multi_dim_array = [part.split() for part in parts]

    return multi_dim_array

#==================================
# Defining Actions and Process
#==================================


def process_words(texts,size):
    final_output = []

    for i in range(len(texts)):
        text = texts[i]
        before = text
        print("word: ",text)
        #print("text[0] -> ", text[0])
        #print("text[1] -> ", text[1])

        # Main logic to strip harakat, process the word, and reapply harakat
        original_text = text  # Example input with harakat
        stripped_text = strip_harakat(original_text)  # Strip harakat

        if any(substring in stripped_text for substring in exceptions_list) and (not "يس" in stripped_text or strip_harakat(before) == "يس"):  #
            print("replace_specific_words")
            processed_text = replace_specific_words(stripped_text) #strip_harakat(text)
            text = processed_text
            replace_specific_words_Array.append([before, processed_text])

        # Main logic to strip harakat, process the word, and reapply harakat
        original_text = text  # Example input with harakat
        stripped_text = strip_harakat(original_text)  # Strip harakat

        if stripped_text[:2] == "ال" and i != 0:

            print("check_al_type -> input: ", stripped_text)
            processed_text, al_type = check_al_type(stripped_text)  # Call the processing function
            if al_type == "شمسية":
                check_al_type_shams_Array.append([before, check_al_type(before)[0]])
            elif al_type == "قمرية":
                check_al_type_qamar_Array.append([before, check_al_type(before)[0]])
            #print("check_al_type -> output: ", processed_text)
            #print("al_type -> output: ", al_type)

            # Reapply harakat to the processed text
            text = reapply_harakat(original_text, processed_text)
            print("final shams and qamar:", text)

        # Main logic to strip harakat, process the word, and reapply harakat
        original_text = text  # Example input with harakat
        stripped_text = strip_harakat(original_text)  # Strip harakat

        # Check and process if the first or second letter is "ا"
        if stripped_text[0] == "ا" or (len(stripped_text) > 1 and stripped_text[1] == "ا"):
            print("check_and_remove_alif")
            # print("check_and_remove_alif input ->", stripped_text)
            processed_text = check_and_remove_alif(stripped_text)  # Call the processing function
            #print("processed_text", processed_text)
            # Reapply harakat to the processed text
            text = reapply_harakat(original_text, processed_text)
            #print("Result:", text)
        else:
            # No changes; return the original text with harakat intact
            final_text = text
            #print("Result:", final_text)

        if any(t in text for t in ["هِ", "هُ"]) and i < len(texts) - 1 and strip_harakat(text)[-1] == "ه":
            print("modify_words_with_haa")
            text = modify_words_with_haa(text,text + " " + texts[i+1])
            modify_words_with_haa_Array.append([before, modify_words_with_haa(before,before + " " + texts[i+1])])


        if any(t in text for t in ["مِ", "مُ"]) and i < len(texts) - 1 and strip_harakat(text)[-1] == "ه":
            print("modify_words_with_meem")
            text = modify_words_with_meem(text,text + " " + texts[i+1])
            modify_words_with_meem_Array.append([before, modify_words_with_meem(before)])

        if any(t in text for t in ["ٌ", "ً", "ٍ"]):
             print("replace_tanween")
             text = replace_tanween(text)
             replace_tanween_Array.append([before, replace_tanween(before)])

        if re.search(r"ّ[َُِ]", text):
            print("replace_shaddah")
            text = replace_shaddah(text)
            replace_shaddah_Array.append([before, replace_shaddah(before)])

        if any(text[i] in "وايى" and text[i + 1] == 'ْ'  for i in range(len(text) - 1)):# and i < len(texts) - 1: #should be first
            print("remove_vowel_with_sukun")
            if i != len(texts) - 1:
                text = remove_vowel_with_sukun(text,texts[i+1])
                remove_vowel_with_sukun_Array.append([before, remove_vowel_with_sukun(before,texts[i+1])])
            else:
                text = remove_vowel_with_sukun(text,text)
                remove_vowel_with_sukun_Array.append([before, remove_vowel_with_sukun(before,before)])

        if "آ" in text:
            print("replace_alif_madda")
            text = replace_alif_madda(text)
            replace_alif_madda_Array.append([before, replace_alif_madda(before)])

        if i == len(texts)-1 and (text[-1].endswith("ِ") or text[-1].endswith("ُ")):
            print("modify_endings -> input:" , text[-1])
            text = modify_endings(text)
            print("modify_endings -> output:" , text)
            modify_endings_Array.append([before, modify_endings(before)])


        if text.endswith("وا"):
            print("remove_alif_if_ends_with_wa")
            text = remove_alif_if_ends_with_wa(text)
            remove_alif_if_ends_with_wa_Array.append([before, remove_alif_if_ends_with_wa(before)])
        # Append the processed word to the final output list
        final_output.append(text)

    # Join the list into a single string with spaces between words
    return ' '.join(final_output)

#==================================
# Flask route to interact with WatsonX model
#==================================

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    word = data.get('word', '')
    version = data.get('version', '')

    if not word:
        return jsonify({'error': 'No word provided'}), 400

    if not version:
        return jsonify({'error': 'No version provided'}), 400

    # Choose the prompt based on the version
    if version == "v1":
        prompt = f"[INST]{word}[/INST]"
        generated_response = model.generate_text(prompt=prompt, guardrails=False)
        return jsonify({
            'original_word': word,
            'version': version,
            'processed_text': generated_response
        })
    else:
       separated_words = extract_and_index_poem(word)
       if separated_words:
            final_text = []
            for separated_word in separated_words:
                final_text.append(process_words(separated_word,len(separated_word)))


            if final_text[0] + " / " + final_text[1] == "T / h":
                return jsonify({
            'original_word': word,
            'version': version,
            'processed_text': "نعتذر : أرجو إعادة صياغة السؤال كما بالامثلة"
        })
            finalword = "الكتابة العروضية :\n"
            finalword += final_text[0] + " / " + final_text[1]
            finalword += "\n" + process_text_bhoor(final_text[0] + " / " + final_text[1]) + "\n\n"

    if replace_shaddah_Array:
        finalword += "تم إستخدام قاعدة فك الحرف المشدد وكتابته حرفين، في الكلمات التالية:-\n"
        for i in range(len(replace_shaddah_Array)):
            if replace_shaddah_Array[i][0] != replace_shaddah_Array[i][1]:
                finalword += replace_shaddah_Array[i][0]+" أصبحت "+replace_shaddah_Array[i][1] + "\n"

    if replace_tanween_Array:
        finalword += "تم إستخدام قاعدة كتابة التنوين نوناً ساكنة، في الكلمات التالية:-\n"
        for i in range(len(replace_tanween_Array)):
            if replace_tanween_Array[i][0] != replace_tanween_Array[i][1]:
                finalword += replace_tanween_Array[i][0]+" أصبحت "+replace_tanween_Array[i][1] + "\n"

    if check_al_type_shams_Array:
        finalword += "تم إستخدام قاعدة حذف 'ال' الشمسية، في الكلمات التالية:-\n"
        for i in range(len(check_al_type_shams_Array)):
            if check_al_type_shams_Array[i][0] != check_al_type_shams_Array[i][1]:

                finalword += check_al_type_shams_Array[i][0]+" أصبحت "+check_al_type_shams_Array[i][1] + "\n"

    if check_al_type_qamar_Array:
        finalword += "تم إستخدام قاعدة حذف 'ا' القمرية، في الكلمات التالية:-\n"
        for i in range(len(check_al_type_qamar_Array)):
            if check_al_type_qamar_Array[i][0] != check_al_type_qamar_Array[i][1]:

                finalword += check_al_type_qamar_Array[i][0]+" أصبحت "+check_al_type_qamar_Array[i][1] + "\n"


    if replace_specific_words_Array:
        finalword += "تم إستخدام قاعدة الاستثناءات، في الكلمات التالية:-\n"
        for i in range(len(replace_specific_words_Array)):
            if replace_specific_words_Array[i][0] != replace_specific_words_Array[i][1]:

               finalword += replace_specific_words_Array[i][0]+" أصبحت "+replace_specific_words_Array[i][1] + "\n"


    if check_and_remove_alif_Array:
        finalword += "تم إستخدام قاعدة حذف حذف همزة الوصل المسبوقة بحرف متحرك ، في الكلمات التالية:-\n"
        for i in range(len(check_and_remove_alif_Array)):
            if check_and_remove_alif_Array[i][0] != check_and_remove_alif_Array[i][1]:
               finalword += check_and_remove_alif_Array[i][0]+" أصبحت "+check_and_remove_alif_Array[i][1] + "\n"


    if modify_words_with_haa_Array:
        finalword += "تم إستخدام قاعدة حذف هاء الغائب المشبعة، في الكلمات التالية:-\n"
        for i in range(len(modify_words_with_haa_Array)):
            if modify_words_with_haa_Array[i][0] != modify_words_with_haa_Array[i][1]:
              finalword += modify_words_with_haa_Array[i][0]+" أصبحت "+modify_words_with_haa_Array[i][1] + "\n"


    if modify_words_with_meem_Array:
        finalword += "تم إستخدام قاعدة حذف ميم الجماعة المشبعة  ، في الكلمات التالية:-\n"
        for i in range(len(modify_words_with_meem_Array)):
            if modify_words_with_meem_Array[i][0] != modify_words_with_meem_Array[i][1]:
               finalword += modify_words_with_meem_Array[i][0]+" أصبحت "+modify_words_with_meem_Array[i][1] + "\n"

    if remove_vowel_with_sukun_Array:
        finalword += "تم إستخدام قاعدة حذف الألف والواو والياء السواكن المتبوعة بساكن، في الكلمات التالية:-\n"
        for i in range(len(remove_vowel_with_sukun_Array)):
            if remove_vowel_with_sukun_Array[i][0] != remove_vowel_with_sukun_Array[i][1]:
                finalword += remove_vowel_with_sukun_Array[i][0]+" أصبحت "+remove_vowel_with_sukun_Array[i][1] + "\n"

    if replace_alif_madda_Array:
        finalword += "تم إستخدام قاعدة فك المد وكتابته همزتين، في الكلمات التالية:-\n"
        for i in range(len(replace_alif_madda_Array)):
            if replace_alif_madda_Array[i][0] != replace_alif_madda_Array[i][1]:
               finalword += replace_alif_madda_Array[i][0]+" أصبحت "+replace_alif_madda_Array[i][1] + "\n"

    if modify_endings_Array:
        finalword += "تم إستخدام قاعدة القافية، في الكلمات التالية:-\n"
        for i in range(len(modify_endings_Array)):
            if modify_endings_Array[i][0] != modify_endings_Array[i][1]:
                finalword += modify_endings_Array[i][0]+" أصبحت "+modify_endings_Array[i][1] + "\n"

    if remove_alif_if_ends_with_wa_Array:
        finalword += "تم إستخدام قاعدة حذف الألف الفارقة بعد واو الجماعة، في الكلمات التالية:-\n"
        for i in range(len(remove_alif_if_ends_with_wa_Array)):
            if remove_alif_if_ends_with_wa_Array[i][0] != remove_alif_if_ends_with_wa_Array[i][1]:
                finalword += remove_alif_if_ends_with_wa_Array[i][0]+" أصبحت "+remove_alif_if_ends_with_wa_Array[i][1] + "\n"



    return jsonify({
            'original_word': word,
            'version': version,
            'processed_text': finalword
        })


#==================================
# Run the app
#==================================
if __name__ == '__main__':
    app.run(debug=True)

