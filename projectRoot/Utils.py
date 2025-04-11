import regex as re
import jsonpickle

INFO_REGEX_CURLY = r'\{(?:[^{}]|(?R))*\}'

def extract_json(text, which):
    # Find all matches in the text
    matches = re.findall(INFO_REGEX_CURLY, text, flags=re.DOTALL)
    counter = 0
    for match in matches:
        if counter == which:
            return match
        counter += 1

def escape_curly_braces(s):
    return s.replace("{", "{{").replace("}", "}}")

def de_escape_curly_braces(s):
    return s.replace("{{", "{").replace("}}", "}")

def clean_json_string(json_string):
    pattern = r'^```json\s*(.*?)\s*```$'
    cleaned_string = re.sub(pattern, r'\1', json_string, flags=re.DOTALL)
    return cleaned_string.strip()

def adapt_output_to_bot(output):
    return escape_curly_braces(jsonpickle.encode(output))