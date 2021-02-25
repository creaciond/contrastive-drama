import requests


class CorpusLoader:
    """Wrapper class for all actions associated with initial text retrieval.

    Contains all functions that access DraCor API and form requests. Further
    processing, e.g. saving to database, morphology parsing, etc., are stored
    in their own classes.

    Attributes:
        language: language of corpus being downloaded
    """

    def __init__(self, language):
        self.corpus_id = language

    def get_corpus_content(self):
        """Makes a request to DraCor API to get all play ids.

        Returns:
            play_ids: (list of str) ids for all plays in the corpus"""
        play_ids = []
        request_link = f"https://dracor.org/api/corpora/{self.corpus_id}"
        response = requests.get(request_link)
        if response:
            all_plays = response.json()["dramas"]
            for play in all_plays:
                play_ids.append(play["id"])
        return play_ids

    def get_play_relations(self, play_id):
        """Downloads a comma-separated file with characters relationships.

        Args:
            play_id: (str) play in question

        Returns:
            relations_data: (list of lists) preprocessed relations
        """
        request_link = f"https://dracor.org/api/corpora/{self.corpus_id}/play/{play_id}/networkdata/csv"
        response = requests.get(request_link)
        relations_data = [line.strip("\n").split(",")
                          for line in response.text.split("\n")]
        return relations_data

    def get_play_text_by_character(self, play_id):
        """Downloads play lines, grouped by character.

        Args:
            play_id: (str) play in question

        Returns:
            characters_data: (list of dicts) lines of play w/keys:
              - text
              - gender
              - label
              - isGroup (for entities like 'crowd')
              - id
              - roles (for RomDraCor)
        """
        request_link = f"https://dracor.org/api/corpora/{self.corpus_id}/play/{play_id}/spoken-text-by-character"
        response = requests.get(request_link)
        characters_data = response.json()
        return characters_data

    def get_play_stage(self, play_id):
        """Downloads stage directions.

        Args:
            play_id: (str) play in question

        Returns:
            directions: (list of str) stage directions as seen in corpus
        """
        request_link = f"https://dracor.org/api/corpora/{self.corpus_id}/play/{play_id}/stage-directions"
        response = requests.get(request_link)
        directions = [line.strip("\n") for line in response.text.split("\n")]
        return directions
