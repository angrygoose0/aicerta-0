import json
import os

x = """
{
"questions": [
    {
    "question": "(a)(i)",
    "feedback": [
        {
        "type": "Achievement",
        "bullet_point": "•13",
        "answer": "As the temperature of the vinegar/ acid/ mixture  increases"
        },
        {
        "type": "Achievement",
        "bullet_point": "•14",
        "answer": "the particles move faster and have more energy"
        },
        {
        "type": "Achievement",
        "bullet_point": "•15",
        "answer": "more successful collisions per second, and the reaction will occur faster"
        },
        {
        "type": "Merit",
        "bullet_point": "•16",
        "answer": "There are more collisions per second between the reacting particles due to faster speed"
        },
        {
        "type": "Merit",
        "bullet_point": "•17",
        "answer": "more of these collisions have enough energy to cause a reaction"
        },
        {
        "type": "Excellence",
        "bullet_point": "•18",
        "answer": "increasing the temperature will cause more successful collisions per second, and the reaction will occur faster"
        }
    ],
    "achievement": "3",
    "merit": "2",
    "excellence": "1"
    },
    {
    "question": "(b)(i)",
    "feedback": [
        {
        "type": "Achievement",
        "bullet_point": "•19",
        "answer": "A: Fast B: Slower C: No reaction"
        },
        {
        "type": "Achievement",
        "bullet_point": "•20",
        "answer": "There are more reactant particles, so more collisions per second"
        },
        {
        "type": "Merit",
        "bullet_point": "•21",
        "answer": "A: Reaction is fast, there are many reactant particles, so more collisions. B: Reaction is slowing, as there are fewer particles to collide. C: Reaction has stopped, as there are no more reactant particles to collide"
        },
        {
        "type": "Excellence",
        "bullet_point": "•22",
        "answer": "Section A: The steep line shows the reaction is fast. There are more reactant particles, so more collisions per second. More product particles are being formed, including more gas, so more gas is collected.  Section B: The line is less steep, so the reaction has slowed. There are fewer reactant particles, so fewer successful collisions per second and so less product is being made, so the volume of gas increases less quickly.  Section C: The line is horizontal so the reaction has stopped because one of the reactants has been used up, so there are no more collisions between reacting particles, so no gas is produced"
        }
    ],
    "achievement": "2",
    "merit": "1",
    "excellence": "1"
    },
    {
    "question": "(c)(i)",
    "feedback": [
        {
        "type": "Achievement",
        "bullet_point": "•23",
        "answer": "The concentration of the solution is changed"
        }
    ],
    "achievement": "1",
    "merit": "0",
    "excellence": "0"
    },
    {
    "question": "(c)(ii)",
    "feedback": [
        {
        "type": "Achievement",
        "bullet_point": "•24",
        "answer": "less successful collisions occur per second, and the rate of reaction is slower"
        },
        {
        "type": "Achievement",
        "bullet_point": "•25",
        "answer": "In the diluted acid, there are fewer acid particles / H+ ions / vinegar particles in the same volume of the acid"
        },
        {
        "type": "Achievement",
        "bullet_point": "•26",
        "answer": "Because there are fewer to collide, less successful collisions occur per second, and the rate of reaction is slower"
        },
        {
        "type": "Merit",
        "bullet_point": "•27",
        "answer": "When water is added, the acid is diluted. In the diluted acid, there are fewer acid particles / H+ ions / vinegar particles in the same volume of the acid. Because of this, there are fewer particles available to collide with the sodium hydrogen carbonate particles"
        },
        {
        "type": "Excellence",
        "bullet_point": "•28",
        "answer": "Because there are fewer to collide, less successful collisions occur per second, and the rate of reaction is slower"
        }
    ],
    "achievement": "3",
    "merit": "1",
    "excellence": "1"
    }
]
}
"""

y=0
data = json.loads(x)
for question in data['questions']:
    # Extract the feedbacks for the current question
    feedbacks = question['feedback']
    
    print(str(feedbacks))
    y +=1
    for feedback in feedbacks:
        print(feedback)
        print(y)
        