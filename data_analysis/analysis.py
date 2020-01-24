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
from scipy.stats import chi2_contingency
from scipy.stats import chi2
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

def make_pandas_replacement_dict(new_ordered_labels):
    """
    Makes a dictionary with {text : int} mapping. The int is the index in the list of the element. We use that to assign
        new values to pandas dataframes for analysis. This is because, if we reorder the labels, we cannot use the integer
        in the 'a' column that we have anyways, so we need to create ourselves new integer lables in the correct order.
    :param list of string new_ordered_labels: The answers (in new order) to a certain question
    :return: Dictionary with mapping that pandas can use.
    """
    dicc = {}
    for i in range(len(new_ordered_labels)):
        dicc[new_ordered_labels[i]]=i
    return dicc

def calculate_spearman_corr(data1,data2):
    # calculate spearman's correlation
    coef, p = spearmanr(data1, data2)
    print('Spearmans correlation coefficient: %.3f' % coef)
    # interpret the significance
    alpha = 0.05
    if p > alpha:
        print('Samples are uncorrelated (fail to reject H0) p=%.3f' % p)
    else:
        print('Samples are correlated (reject H0) p=%.3f' % p)

def calculate_kendall_corr(data1,data2):
    # calculate kendall's correlation
    coef, p = kendalltau(data1, data2)
    print('Kendall correlation coefficient: %.3f' % coef)
    # interpret the significance
    alpha = 0.05
    if p > alpha:
        print('Samples are uncorrelated (fail to reject H0) p=%.3f' % p)
    else:
        print('Samples are correlated (reject H0) p=%.3f' % p)

def caluclate_mannwhitneyu(data1, data2):
    # compare samples: two data arrays
    stat, p = mannwhitneyu(data1, data2)
    print('Statistics=%.3f, p=%.3f' % (stat, p))
    # interpret
    alpha = 0.05
    if p > alpha:
        print('Same distribution (fail to reject H0)')
    else:
        print('Different distribution (reject H0)')

def calculate_kruskalwallis(data_arrays):
    # compare samples --> generalization of mannwhitneyu test. For not only 2, but several samples
    stat, p = kruskal(*data_arrays)
    print('Statistics=%.3f, p=%.3f' % (stat, p))
    # interpret
    alpha = 0.05
    if p > alpha:
        print('Same distributions (fail to reject H0)')
    else:
        print('Different distributions (reject H0)')

def calculate_chi_square(contigency_table):
    # contigency table should hold the frequencies

    # convert it to numpy for value check
    arr = np.asarray(contigency_table)

    # check if all cell values are over 5
    if len(arr[arr<5]) > 0:
        print("For Chi-Square to make sense, the values in each cell need to be >=5!")
    else:
        stat, p, dof, expected = chi2_contingency(contigency_table)
        print('dof=%d' % dof)
        print('Expected frequency table '+expected)

        # interpret test-statistic
        prob = 0.95
        critical = chi2.ppf(prob, dof)
        print('probability=%.3f, critical=%.3f, stat=%.3f' % (prob, critical, stat))
        if abs(stat) >= critical:
            print('Dependent (reject H0)')
        else:
            print('Independent (fail to reject H0)')

        # interpret p-value
        alpha = 1.0 - prob
        print('significance=%.3f, p=%.3f' % (alpha, p))
        if p <= alpha:
            print('Dependent (reject H0)')
        else:
            print('Independent (fail to reject H0)')