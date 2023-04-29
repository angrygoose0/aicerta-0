import roman

q_list = [111, 121, 122, 123, 124, 131, 141, 142, 211, 221, 222, 223]

current_question = None
current_primary = None

for item in q_list:
    question = item // 100
    primary = (item // 10) % 10
    secondary = item % 10
    
    if question != current_question:
        current_question = question
        print(f"\nQUESTION {current_question}:")
        
    if primary != current_primary:
        current_primary = primary
        print(f"\n{chr(ord('a') + current_primary - 1)})")
        
    print(f"{roman.toRoman(secondary)})")
