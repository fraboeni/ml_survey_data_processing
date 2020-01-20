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

def reorder_labels(labels, order):
    """
    Sometimes for plots or ranking statistics, we want the answer labels to have a certain order. This method reorders
        the given labels to how we want them.
    :param list of string labels: The answers that are possible for the question.
    :param list of int order: The indices where the element should go. E.g. [1,0] means put the first element to index
        1 and the second to 0. (They are chaning places)
    :return: Answers in their new order.
    """
    new_ordered_labels = [0 for i in range(len(labels))]
    for i in range(len(order)):
        new_ordered_labels[i] = labels[order[i]]
    return new_ordered_labels