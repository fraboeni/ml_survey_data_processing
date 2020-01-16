import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

from textwrap import wrap

plt.rcParams['figure.figsize'] = (10, 6)  # set parameters for the plots


class Plotter():
    """
    A class to create python plots for given data.
    """

    def __init__(self, answer_mapping_df, question_mapping_df):
        """
        Initialization
        :param DataFrame answer_mapping_df: A df holding a mapping from answer codes to all possible text
                answers per question.
        :param DataFrame question_mapping_df: A df holding a mapping from question code to corresponding type and text.
        """
        self.answer_mapping_df = answer_mapping_df
        self.question_mapping_df = question_mapping_df

    def obtain_labels(self, col_name, line_break=True):
        """
        Method to obtain labels for the plot
        :param string col_name: The name (question code) of the question that we want the answers for
        :param bool line_break: Whether or not to break the lines after 20 chars (looks nicer for the plot)
        :return list of all possible answer strings for the given question
        """
        labels = []
        # iterate over all possible answer values
        for i in self.answer_mapping_df[col_name].columns.values:
            labels.append(self.answer_mapping_df.xs((col_name, i), level=('q_code', 'a_code'), axis=1).iloc[0, 0])

        if line_break:
            labels = ['\n'.join(wrap(l, 20)) for l in labels]

        return labels
