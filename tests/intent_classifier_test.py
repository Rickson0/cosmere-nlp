from preprocessing.intent_classifier import classify_intent


rafo = "So which of the roles played by Hoid is my favorite. I would probably say Dust from Warbreaker. I just like-- That's the most true storyteller he's been, kind of based on oral storytelling tradition and things like that. I can't tell you. You'll have to read and find out whether you'll find him in Dalinar's flashbacks or not."
confirmation = "Yes it is... the real trick is... making sure that I fit in, for instance, <em>White Sand</em> and things with the proper amount... because I haven't released that book series yet, I have to make sure while we're doing the graphic novel, that it fits the chronology, which is why I can't quite canonize things yet."
ambiguous = "Yeah, I've warned them. I will write it at the length that feels right."

assert classify_intent(rafo) == "RAFO"
assert classify_intent(confirmation) == "CONFIRMED"
assert classify_intent(ambiguous) == "NONE"
