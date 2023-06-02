from django import template

register = template.Library()

def number_to_alphabet(number):
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

register.filter('to_alphabet', number_to_alphabet)
register.filter('to_roman', number_to_roman)
