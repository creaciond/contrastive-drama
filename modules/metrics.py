from keyness import log_likelihood
from matplotlib import pyplot as plt
from nltk.corpus import stopwords
from string import punctuation
from wordcloud import WordCloud

import numpy as np
import pandas as pd



def calculate_key_items(target_corpus, reference_corpus, stops):
    """Calculates keyness for both corpora in question.

    Args:
      target_corpus - (list of str) subcorpus 1, as is in database
      reference_corpus - (list of str) subcorpus 2, as is in database
      stops - (list of str) words to omit

    Returns:
      key_items - (list) key items with log-likelihood score
    """
    corpus1_processed = []
    for play_title, play_text in target_corpus[0]:
        filtered_text = []
        items = " ".join(play_text).split()
        for l in items:
            if (l not in punctuation + "—…«»") and (l not in stops) and (l not in ["None", "null"]):
                filtered_text.append(l)
        corpus1_processed.append(filtered_text)

    corpus2_processed = []
    for play_title, play_text in reference_corpus[0]:
        filtered_text = []
        items = " ".join(play_text).split()
        for l in items:
            if (l not in punctuation + "—…«»") and (l not in stops) and (l not in ["None", "null"]):
                filtered_text.append(l)
        corpus2_processed.append(filtered_text)

    key_items = log_likelihood(corpus1_processed, corpus2_processed)
    return key_items


def convert_corpus_to_df(corpus, play_years):
    pos_dict = {param: [] for param in ["year", "NOUN", "VERB", "ADJ", "ADVB", "PREP"]}
    for i, play in enumerate(corpus):
        play_id = play[0]
        play_texts = play[1]
        try:
            pos_dict["year"].append(play_years[play_id])
            this_pos = {pos: 0 for pos in ["NOUN", "VERB", "ADJ", "ADVB", "PREP"]}
            this_count = 0
            for character in play_texts:
                for line in character:
                    for line_item in line:
                        if line_item in this_pos.keys():
                            this_pos[line_item] += 1
                        elif line_item in pos_mappings:
                            this_pos[pos_mappings[line_item]] += 1
                        this_count += 1
            for key in this_pos.keys():
                try:
                    pos_dict[key].append(this_pos[key]/this_count)
                except:
                    pos_dict[key].append(0)
        except:
            pass
    df = pd.DataFrame.from_dict(pos_dict).sort_values(by="year").reset_index().drop(["index"], axis=1)
    return df


def convert_stage_to_df(corpus, play_years):
    pos_dict = {param: [] for param in ["year", "NOUN", "VERB", "ADJ", "ADVB", "PREP"]}
    for i, play in enumerate(corpus):
        play_id = play[0]
        play_texts = play[1]
        try:
            pos_dict["year"].append(play_years[play_id])
            this_pos = {pos: 0 for pos in ["NOUN", "VERB", "ADJ", "ADVB", "PREP"]}
            this_count = 0
            for line in play_texts:
                for line_item in line:
                    if line_item in this_pos.keys():
                        this_pos[line_item] += 1
                    elif line_item in pos_mappings:
                        this_pos[pos_mappings[line_item]] += 1
                    this_count += 1
            for key in this_pos.keys():
                try:
                    pos_dict[key].append(this_pos[key]/this_count)
                except:
                    pos_dict[key].append(0)
        except:
            pass
    df = pd.DataFrame.from_dict(pos_dict).sort_values(by="year").reset_index().drop(["index"], axis=1)
    return df


def plot_frequencies(df, title, path):
    fig = plt.figure(figsize=(12, 9))
    ax = plt.gca()
    colors_for_pos = {
        "NOUN": "#ef476f",
        "VERB": "#ffd166",
        "ADJ": "#06d6a0",
        "ADVB": "#118ab2",
        "PREP": "#073b4c"
    }

    for pos in ["NOUN", "VERB", "ADJ", "ADVB", "PREP"]:
        # scatter for shares
        df.plot(kind="scatter", x="year", y=pos,
                ax=ax, label=pos, color=colors_for_pos[pos], alpha=0.3)
        # linear approximation
        m, b = np.polyfit(df["year"], df[pos], 1)
        y_reg = m * df["year"] + b
        ax.plot(df["year"], y_reg, "-", color=colors_for_pos[pos])
    # labels
    ax.set_xlabel("Year")
    ax.set_ylabel("Part of speech share")
    # title
    ax.set_title(title)
    plt.savefig(path, bbox_inches="tight", dpi=150)
    plt.close()


def plot_words(corpus, stops, title, path):
    fig = plt.figure(figsize=(12, 9), facecolor=None)
    ax = plt.gca()

    text = " ".join([word for word in " ".join(corpus).split(" ")
                     if (word not in punctuation) \
                     and (word not in stops) and (word not in ["None", "null"])])
    # text_words = []
    # for word in corpus.split(" "):
    #     token = word.strip(punctuation + "—…«»")
    #     if (token not in stops) and (token not in punctuation + "—…«»") and (token not in ["None", "null", None]):
    #         text_words.append(token)
    # text = " ".join(text_words)
    wordcloud = WordCloud(
        background_color='white',
        width=1200,
        height=900,
    ).generate(text)
    ax.imshow(wordcloud)
    ax.axis("off")
    ax.set_title(title)
    plt.savefig(path, bbox_inches="tight", dpi=150)
    plt.close()