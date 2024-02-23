from django import template


register = template.Library()

def number_to_alphabet(number):
    number = int(number)
    if 1 <= number <= 26:
        return chr(number + 96)  # Convert number to lowercase alphabet
    else:
        return None  # Return None for numbers outside the range 1-26

def number_to_roman(number):
    roman_numerals = {
        1: "i",
        4: "iv",
        5: "v",
        9: "ix",
        10: "x",
        40: "xl",
        50: "l",
        90: "xc",
        100: "c",
        400: "cd",
        500: "d",
        900: "cm",
        1000: "m"
    }

    result = ""
    for value, numeral in sorted(roman_numerals.items(), reverse=True):
        while number >= value:
            result += numeral
            number -= value

    return result

def number_to_word_upper(n):
    digit_map = {
        0: "ZERO",
        1: "ONE",
        2: "TWO",
        3: "THREE",
        4: "FOUR",
        5: "FIVE",
        6: "SIX",
        7: "SEVEN",
        8: "EIGHT",
        9: "NINE"
    }

    # Split the input number into digits
    digits = [int(digit) for digit in str(n)]

    # Map each digit to its word equivalent using a list comprehension
    words = [digit_map[digit] for digit in digits]

    # Join the words together and return the result
    return " ".join(words)

def saved(n):
    x = n // 5
    return x

def times(n):
    x = n * 100
    return x

def status_class(status):
    return {
        'pending': 'bg-warning',
        'started': 'bg-primary',
        'locked': 'bg-danger',
        'submitted': 'bg-success',
    }.get(status, 'bg-secondary')  # Default to 'bg-secondary' if status is not recognized
    
def score(x):
    # Define a dictionary mapping input values to output strings
    score_map = {
        0: "N0",
        1: "N1",
        2: "N2",
        3: "A3",
        4: "A4",
        5: "M5",
        6: "M6",
        7: "E7",
        8: "E8",
    }
    return score_map.get(x)
    

register.filter('to_alphabet', number_to_alphabet)
register.filter('to_roman', number_to_roman)
register.filter('NUMBER', number_to_word_upper)
register.filter('saved', saved)
register.filter('times', times)
register.filter('status_class', status_class)
register.filter('score', score)

