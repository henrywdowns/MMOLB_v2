# stupid little script i had chatgpt finish for me bc i was lazy and burnt out

def scouting_report():
    from utils import Utils

    scouting_report = Utils.access_json('chicken_scout_reports.json')

    adjective_ratings = {
        "barely": 1,
        "not": 2,
        "decent": 3,
        "very": 4,
        "extremely": 5
    }

    parsed_dict = {}
    keywords = {}
    keywords_scored = {}

    for player, report in scouting_report.items():
        # 1) split into sentences and strip out empties
        sentences = [s.strip() for s in report.replace('\n\n', ' ').split('.') if s.strip()]
        parsed_dict[player] = sentences

        # 2) initialize per-player mappings
        keywords[player] = {}
        keywords_scored[player] = {}

        # 3) skip the first two sentences and scan for adjectives
        for sentence in sentences[2:]:
            words = sentence.split()
            for i, word in enumerate(words):
                if word in adjective_ratings:
                    # determine which following word to grab
                    if word == "decent":
                        # "decent" modifies the word two over
                        if i + 2 < len(words):
                            target = words[i + 2]
                        else:
                            continue
                    else:
                        # other adjectives modify the very next word
                        if i + 1 < len(words):
                            target = words[i + 1]
                        else:
                            continue

                    keywords[player][target] = word
                    keywords_scored[player][target] = adjective_ratings[word]
    return keywords, keywords_scored
