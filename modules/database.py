class DatabaseConnector:
    """Wrapper class for actions associated with database.

    Adds new plays, updates data, fetches existing plays and their metadata.
    """

    def __init__(self):
        pass

    def save_play(self, corpus_id, play_id, play_data, save_type):
        """Saves play into database.

        Args:
            corpus_id: (str) corpus play belongs to
            play_id: (str) play in question
            play_data: (dict) data to save
            save_type: (str) flag to either update existing play
            or save a new one
              'new' = play was not in the database before, create an instance
              'upd' = play was updated, modify existing instance
        """
        pass

    def fetch_play_info(self, corpus_id, play_id):
        """Gets metadata for a given play.

        Method is required in cases where final results have to be sorted
        time-wise.

        Args:
            corpus_id: (str) corpus play belongs to
            play_id: (str) play in question

        Returns:
             play_data: (dict)
        """
        pass

    def fetch_play_text(self, corpus_id, play_id, text_type, morph):
        """

        Args:
            corpus_id: (str) corpus play belongs to
            play_id: (str) play in question
            text_type: (str) text to fetch; possible options:
              'all'
              'all_spoken'
              'all_stage'
              'by_gender'
              'by_role' - for Roman corpus only
              'by_relation' - for Russian and German corpora only
            morph: (str) flag for text parsing
              'lemma' = return lemmatized text
              'raw' = return text as is
        Returns:
            play_text:
        """
        pass
