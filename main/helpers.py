def number_to_alphabet(number):
    if 1 <= number <= 26:
        return chr(number + 96)  # Convert number to lowercase alphabet
    else:
        return None  # Return None for numbers outside the range 1-26
    
def alphabet_to_number(letter):
    return ord(letter) - ord('a') + 1

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

def roman_to_number(s):
    values = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}
    total = 0
    prev_value = 0
    for i in s[::-1]:  # Reverse the string
        curr_value = values[i]
        if prev_value > curr_value:
            total -= curr_value
        else:
            total += curr_value
        prev_value = curr_value
    return total

