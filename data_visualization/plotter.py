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

    def make_mapping_from_labels(self, labels):
        """
        A method to create a dict with keys=answer text and value=answer text with \n after 20 char.
        This dict can be used by pandas to replace the normal text by the formated text.
        :param list of strings labels: holds all possible answer texts for a question with line breaks as they fall
            out of the obtain_labels() function
        :return dict: with a mapping from normal text as key to text with linebreaks
        """
        dicc = {}
        for i in range(len(labels)):
            stripped = labels[i].replace("\n"," ")
            dicc[stripped]=labels[i]

        return dicc

    def make_countplot(self, df, x_name, title="", x_axlabel="", x_labels=[], labels_newline=True):
        """
        Method to create a countplot for the property of x_name
        :param DataFrame df: contains the data to be plotted (so filtering should take place outside the method)
                         the dataframe column names should contain the names specified in the following 2 params
        :param string x_name: name of the column to plot on the x-axis
        :param string title: Title of the plot
        :param string x_axlabel: Subtitle of the x-axis
        :param list of strings x_labels: The labels that should be displayed at the x axis (and their order through list order)
        :param bool labels_newline: If the labels that we provide in x_labels or y_labels contain linebreaks
        """
        # if labels have a new line, we need to match them over the labels in the dataframe given
        if labels_newline:
            d1 = self.make_mapping_from_labels(x_labels)
            df = df.replace(d1)

        ax = sns.countplot(x=x_name, data=df, order=x_labels).set_title('Awareness with respect to demographics',
                                                                        fontsize=18)
        plt.xticks(rotation=70)

        # if user wants to set axis labels manually
        if x_axlabel:
            plt.xlabel(x_axlabel)

        return ax

    def make_grouped_countplot(self, df, x_name, y_name, title="", x_axlabel="", y_axlabel="", x_labels=[], y_labels=[],
                               labels_newline=True):
        """
        Method to create a countplot for the two properties given for x and y
        :param DataFrame df: contains the data to be plotted (so filtering should take place outside the method)
                         the dataframe column names should contain the names specified in the following 2 params
        :param string x_name: name of the column to plot on the x-axis
        :param string y_name: name of the column to plot on as groups (each has a different color)
        :param string title: Title of the plot
        :param string x_axlabel: Subtitle of the x-axis
        :param string y_axlabel: Subtitle of the y-axis
        :param list of strings x_labels: The labels that should be displayed at the x axis (and their order through list order)
        :param list of strings y_labels: The labels that should appear in the legend of the grouping
        :param bool labels_newline: If the labels that we provide in x_labels or y_labels contain linebreaks
        """
        # if labels have a new line, we need to match them over the labels in the dataframe given
        # otherwise, they are not put to the correct bin of the diagram (because the plotting function maps over names)
        if labels_newline:
            d1 = self.make_mapping_from_labels(x_labels)
            d2 = self.make_mapping_from_labels(y_labels)
            d = {**d1, **d2}
            df = df.replace(d)

        ax = sns.countplot(x=x_name, hue=y_name, data=df, order=x_labels, hue_order=y_labels).set_title(title,
                                                                                                        fontsize=18)
        plt.xticks(rotation=70)

        # if user wants to set axis labels manually
        if x_axlabel:
            plt.xlabel(x_axlabel)
        if y_axlabel:
            plt.ylabel(y_axlabel)
        return ax
