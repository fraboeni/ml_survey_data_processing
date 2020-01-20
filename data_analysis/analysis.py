import pandas as pd
import seaborn as sns
import numpy as np

from textwrap import wrap

from numpy.random import rand
from numpy.random import seed
from scipy.stats import spearmanr
from scipy.stats import kendalltau
from scipy.stats import mannwhitneyu
from scipy.stats import kruskal
# seed random number generator
seed(1)

def get_data_labels(answer_mapping_df, column):
    """
    Method to obtain all possible answer texts for a given question
    :param DataFrame answer_mapping_df: df containing the table with the mapping from (question code, int) to
        the corresponding text. The int corresponds to an answer code
    :param string column: name of the column
    :return: A list with all the possible text values for the data
    """
    labels = []
    for i in answer_mapping_df[column].columns.values:
        labels.append(answer_mapping_df.xs((column, i), level=('q_code', 'a_code'), axis=1).iloc[0,0])
    return labels