import json
import logging
import requests
import time
from bs4 import BeautifulSoup


def get_corpus_content(corpus_id):
    """Makes a request to DraCor API to get all play ids.

    Returns:
        play_ids: (list of str) ids for all plays in the corpus"""
    play_ids = []
    request_link = f"https://dracor.org/api/corpora/{corpus_id}"
    response = requests.get(request_link)
    if response:
        all_plays = response.json()["dramas"]
        for play in all_plays:
            play_ids.append(play["name"])
    return play_ids



def get_stage_directions(corpus_id, play_id):
    """
    Args:
        play_id: (str) play in question
        corpus_id: (str) corpus

    Returns:
        play_stage: (dict) stage directions of a play
    """
    request_stage = f"https://dracor.org/api/corpora/{corpus_id}/play/{play_id}/stage-directions-with-speakers"
    response_stage = requests.get(request_stage).text.replace("\xa0", " ").split("\n")
    play_stage = {play_id: {"raw": response_stage}}
    return play_stage


def get_characters_and_spoken(corpus_id, play_id):
    """Makes a request to DraCor API and extracts all
    character information and their spoken lines.
    
    Args:
        corpus_id: (str) corpus to request
        play_id: (str) play to parse
    
    Returns:
        characters_info: (dict) character information (name, gender, id)
        play_spoken: (dict) spoken lines as is
    """
    characters_info = {play_id: {}}
    play_spoken = {play_id: {}}
    request_spoken = f"https://dracor.org/api/corpora/{corpus_id}/play/{play_id}/spoken-text-by-character"
    response_spoken = json.loads(requests.get(request_spoken).text.replace("\xa0", " "))
    for item in response_spoken:
        # extract character info
        this_character = {}
        character_id = item["id"]
        this_character["name"] = item["label"]
        this_character["gender"] = item["gender"]
        this_character["relations"] = []
        characters_info[play_id][character_id] = this_character
        # extract spoken lines
        play_spoken[play_id][item["id"]] = {}
        play_spoken[play_id][item["id"]]["raw"] = item["text"]
    return characters_info, play_spoken


def get_play_relations(corpus_id, play_id):
    """Downloads and parses a comma-separated file with characters relationships.

    Args:
        play_id: (str) play in question
        corpus_id: (str) corpus
        characters_info: (dict) extracted characters list

    Returns:
        relations_info: (list of tuples) parsed information about play characters
    """
    request_link = f"https://dracor.org/api/corpora/{corpus_id}/play/{play_id}/relations/gexf"
    response = requests.get(request_link)
    relations_info = []
    relations_xml = BeautifulSoup(response.text, "lxml")
    for relation in relations_xml.find_all("edge"):
        if relation["type"] == "undirected" or relation["label"] in {"associated_with", 
                                                                     "lover_of",
                                                                     "related_with",
                                                                     "siblings"}:
            relations_info.append([relation["source"], relation["label"]])
            relations_info.append([relation["target"], relation["label"]])
        else:
            if relation["label"] == "parent_of":
                relations_info.append((relation["source"], "parent"))
                relations_info.append((relation["target"], "child"))
            else:
                print(relation["label"])
    time.sleep(3)
    return relations_info


def insert_relations(play_id, relations_info, characters_info):
    """Adds extarcted relations to the characters_info dict.
    
    Args:
        play_id: (str) play in question
        relations_info: (list of tuples) parsed information 
          about play characters
        characters_info: (dict) character information 
          (name, gender, id)
    
    Returns:
        characters_info: (dict) updated character information
          (name, gender, id & relations)
    """
    # whoever encoded those plays: hope you're having a good day
    characters_with_typos = {
        "r_dzhekobs": "m-r_dzhekobs", # petrov-ostrov-mira
        "nefyodovnа": "nefyodovna", # babel-maria
        "toroj_sluga": "vtoroj_sluga"
    }
    for character, relation in relations_info:
        character = characters_with_typos[character] if character in characters_with_typos else character
        if relation not in characters_info[play_id][character]["relations"]:
            characters_info[play_id][character]["relations"].append(relation)
    return characters_info


def main():
    corpora = ["rus", "ger", "ita", "shake", "span", "rom", "greek"]
    logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s",
                        filename="download.log",
                        encoding="utf-8", 
                        level=logging.INFO)

    for i in range(len(corpora)):
        corpus_id = corpora[i]
        play_ids = get_corpus_content(corpus_id)
        logging.debug(f"Got corpus content: {corpus_id}")
        for play_id in play_ids:
            logging.info(f"Play: {play_id}")

            logging.info("Extracting characters info and spoken text...")
            characters_info, play_spoken = get_characters_and_spoken(corpus_id, play_id)
            # save characters
            with open(f"./data/raw/{corpus_id}_{play_id}_characters.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(characters_info))
            logging.info("Characters info DONE")
            # save spoken text
            with open(f"./data/raw/{corpus_id}_{play_id}_spoken.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(play_spoken))
            logging.info("Spoken text DONE")
            # extract & save stage directions
            logging.info("Extracting stage directions...")
            play_stage = get_stage_directions(corpus_id, play_id)
            with open(f"./data/raw/{corpus_id}_{play_id}_stage.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(play_stage))
            logging.info("Stage directions DONE")
            # merge
            logging.info("Extracting relations...")
            relations_info = get_play_relations(corpus_id, play_id)
            logging.info("Relations extracted, merging...")
            try:
                characters_info = insert_relations(play_id, relations_info, characters_info)
                with open(f"./data/raw/{corpus_id}_{play_id}_full.json", "w", encoding="utf-8") as f:
                    json.dump(characters_info, f, ensure_ascii=False)
                logging.info("Merge and save DONE")
            except:
                logging.error(f"Merge and save unsuccessful: corpus {corpus_id}, play {play_id}")


if __name__ == "__main__":
    main()
