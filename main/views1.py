def mark_text(txt, json_feedback):
    # Create a dictionary that maps each character in the text to its CSS classes
    classes_for_each_char = [set() for _ in range(len(txt))]

    # For each feedback item, mark the corresponding characters with the CSS class
    for feedback in json_feedback:
        # Check if feedback type is not "Achievement", "Merit", or "Excellence" and skip if so
        if feedback['type'] not in ["Achievement", "Merit", "Excellence"]:
            continue

        css_class = "bullet_point" + feedback['bullet_point'].replace("•","_")
        start_index = txt.index(feedback['answer'])
        end_index = start_index + len(feedback['answer'])
        for i in range(start_index, end_index):
            classes_for_each_char[i].add(css_class)

    # Construct the marked-up text
    marked_up_text = ""
    current_classes = set()
    for i, char in enumerate(txt):
        if classes_for_each_char[i] != current_classes:
            # Close the current span(s), if any
            if current_classes:
                marked_up_text += "</span>" * len(current_classes)
            # Open a new span(s) for the new classes
            for css_class in classes_for_each_char[i]:
                marked_up_text += f'<span class="{css_class}">'
            current_classes = classes_for_each_char[i]
        marked_up_text += char
    # Close the final span(s), if any
    if current_classes:
        marked_up_text += "</span>" * len(current_classes)

    return marked_up_text


txt = """
Copper forms an ion with a charge of +2. It requires two negative charges to form a neutral compound. The hydroxide ion has a charge of –1, so two hydroxide ions, with a combined charge of –2 are required to cancel out the charge on the copper ion. The carbonate ion has a charge of –2, so only one carbonate ion is required to cancel out the charge on the copper ion.
"""

json_feedback = [
    {"type":"Achievement","bullet_point":"•1","answer":"It requires two negative charges to form a neutral compound."},
    {"type":"Achievement","bullet_point":"•2","answer":"two hydroxide ions, with a combined charge of –2 are required to cancel out the charge on the copper ion."},
    {"type":"Achievement","bullet_point":"•3","answer":"only one carbonate ion is required to cancel out the charge on the copper ion."},
    {"type":"Merit","bullet_point":"•4","answer":"The hydroxide ion has a charge of –1, so two hydroxide ions"},
    {"type":"Merit","bullet_point":"•5","answer":"The carbonate ion has a charge of –2, so only one carbonate ion"},
    {"type":"Excellence","bullet_point":"•6","answer":"Copper forms an ion with a charge of +2. It requires two negative charges to form a neutral compound."},
    {"type":"Excellence","bullet_point":"•7","answer":"Copper forms an ion with a charge of +2. It requires two negative charges"},
    {"type":"wrong","bullet_point":"•8","answer":"bannas are cool"},
]

marked_up_text = mark_text(txt, json_feedback)
print(marked_up_text)