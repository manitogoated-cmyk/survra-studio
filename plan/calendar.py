import json
long = [  # (title, story key)
 ("He Drifted 438 Days Across the Pacific", "Alvarenga"),
 ("She Fell 3 km Into the Amazon and Walked Out Alone", "Koepcke"),
 ("Trapped in Antarctic Ice for Two Years: Shackleton's Endurance", "Shackleton"),
 ("The Pilot Who Escaped a Jungle Prison Camp", "Dengler"),
 ("133 Days Alone on a Raft", "Poon Lim"),
 ("The Last Person Left on Wrangel Island", "Ada Blackjack"),
 ("3 Days in an Air Bubble at the Bottom of the Sea", "Okene"),
 ("18 Days Trapped in a Flooded Cave", "Thai cave"),
 ("Apollo 13: Four Days to Get Home", "Apollo 13"),
]
moments = {
 "Alvarenga": ["Day 1: a 30-hour fishing trip goes wrong", "The crewmate he barely knew", "He counted 438 days by the moon"],
 "Koepcke": ["She fell from the sky still strapped to her seat", "Her parents' advice that saved her life", "Day 10: she finally found a shelter"],
 "Shackleton": ["The ship that ice crushed like a toy", "800 miles in a lifeboat", "The 36-hour walk across South Georgia"],
 "Dengler": ["The pilot who refused to sign", "Escape from the prison camp", "Weeks in the jungle with nothing"],
 "Poon Lim": ["Alone on a raft for 133 days", "He made a fishhook from a nail", "The ships that didn't stop"],
 "Ada Blackjack": ["The last one left on the island", "She taught herself to hunt to stay alive", "The ship that finally came"],
 "Okene": ["3 days in an air bubble on the seafloor", "The diver who grabbed his hand", "Why he couldn't just swim up"],
 "Thai cave": ["13 people trapped by rising water", "How do you get kids out of a flooded cave?", "The rescue diver who didn't come back"],
 "Apollo 13": ["'Houston, we've had a problem'", "A square filter in a round hole", "The coldest ride home"],
}
whatif = ["What if Earth stopped spinning?", "What if the power grid went down for a year?", "What if you fell overboard in the middle of the Pacific?",
 "What if the Sun went out?", "What if you were lost in a cave with no light?", "What if a supervolcano erupted?", "What if your car went into a river?",
 "What if the internet went down for 30 days?", "What if you were stranded in the Sahara with one bottle of water?", "What if you were left in Antarctica for the winter?",
 "What if you were adrift on a raft with no water?", "What if you got lost in the Amazon?", "What if you were stuck in an elevator for 3 days?",
 "What if a blizzard trapped you in your car?", "What if you woke up on a sinking ship?", "What if you floated 24 hours in a life jacket?",
 "What if you were locked in a walk-in freezer?", "What if you were stranded on an island with one tool?", "What if a solar storm knocked out GPS?",
 "What if an avalanche buried you?", "What if your plane went down in the Arctic?", "What if you were in a lifeboat with 10 strangers?",
 "What if you were trapped in a mine?", "What if you got lost on a glacier?", "What if you fell through the ice on a frozen lake?",
 "What if a rip current pulled you out?", "What if a 50 °C heat wave hit your city?", "What if you were stuck in Everest's death zone?",
 "What if you missed the last plane out of Antarctica?", "What if a volcano erupted next to you?"]
science = ["Why you shouldn't eat snow when you're freezing", "How long can a human last without water?", "Why freezing people take their clothes off",
 "The rule of threes of survival", "Why cold-water shock kills before hypothermia", "Why drinking seawater makes thirst worse",
 "How to be seen from a rescue plane", "Why lost people walk in circles", "Can you drink your own urine? The myth", "Why you shiver",
 "The stages of hypothermia", "How fast frostbite sets in", "How long can you live without food?", "Why old sailors got scurvy",
 "Does a solar still really make water?", "Is it safe to sleep in the snow?", "How far can a person swim?", "Why dehydration scrambles your brain",
 "What high altitude does to your brain", "How a life raft keeps you alive", "Can you survive a fall into water?", "Are sharks the biggest danger at sea?",
 "Why sunburn at sea is so dangerous", "How long can you hold your breath?", "The 1-10-1 rule of cold water", "How polar explorers avoided snow blindness",
 "Why you should stay with your car", "Why a mirror is a survival tool", "What's inside a life raft kit", "Why coconuts saved castaways",
 "How sea turtles fed castaways", "How castaways kept track of time", "Why your body burns more energy in the cold"]
long_days = [2, 5, 9, 12, 16, 19, 23, 26, 30]
mom = [m for _, k in long for m in moments[k]]
lane_of = {}
for _, k in long:
    for m in moments[k]: lane_of[m] = k
rows = []; mi = 0; si = 0; wi = 0
for d in range(1, 31):
    rows.append([d, f"=$B$1+{d-1}", "9:00 AM", "Short", "Survival science", science[si], "Idea", "Needs check", None]); si += 1
    rows.append([d, f"=$B$1+{d-1}", "1:00 PM", "Short", "What-if", whatif[wi], "Idea", "Needs check", None]); wi += 1
    if d in long_days:
        t, k = long[long_days.index(d)]
        rows.append([d, f"=$B$1+{d-1}", "5:00 PM", "Long-form", "True story", t, "Rendered" if k == "Alvarenga" else "Idea",
                     "Checked" if k == "Alvarenga" else "Needs check", "Story: " + k])
    if d in (8, 15, 22):
        rows.append([d, f"=$B$1+{d-1}", "6:00 PM", "Short", "Survival science", science[si], "Idea", "Needs check", None]); si += 1
    else:
        m = mom[mi]; mi += 1
        first = (m == mom[0])
        rows.append([d, f"=$B$1+{d-1}", "6:00 PM", "Short", "True story moment", m,
                     "Rendered" if first else "Idea", "Checked" if lane_of[m] == "Alvarenga" else "Needs check",
                     ("Pilot render exists (50 s). " if first else "") + "From: " + lane_of[m]])
assert si == 33 and wi == 30 and mi == 27, (si, wi, mi)
print(len(rows))
json.dump(rows, open('rows.json', 'w'))
