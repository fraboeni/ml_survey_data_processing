import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from statsmodels.graphics.mosaicplot import mosaic
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
        :return: Axis of plot
        """
        dicc = {}
        for i in range(len(labels)):
            stripped = labels[i].replace("\n"," ")
            dicc[stripped]=labels[i]

        return dicc

    def make_countplot(self, df, x_name, title="", x_axlabel="", x_labels=[], labels_newline=True,ax=None):
        """
        Method to create a countplot for the property of x_name
        :param DataFrame df: contains the data to be plotted (so filtering should take place outside the method)
                         the dataframe column names should contain the x_name
        :param string x_name: name of the column to plot on the x-axis
        :param string title: Title of the plot
        :param string x_axlabel: Subtitle of the x-axis
        :param list of strings x_labels: The labels that should be displayed at the x axis (and their order through list order)
        :param bool labels_newline: If the labels that we provide in x_labels or y_labels contain linebreaks
        :return: Axis of plot
        """
        # if labels have a new line, we need to match them over the labels in the dataframe given
        if labels_newline:
            d1 = self.make_mapping_from_labels(x_labels)
            df = df.replace(d1)

        if not x_labels:
            ax = sns.countplot(x=x_name, data=df, ax=ax).set_title(title, fontsize=18)
        else:
            ax = sns.countplot(x=x_name, data=df, order=x_labels,ax=ax).set_title(title, fontsize=18)
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
        :return: Axis of plot
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

    def make_crosstable(self, df, x_name, y_name, x_labels, y_labels, relative_frequencies=False, labels_newline=True):
        """
        Function to create a crosstable plotting two properties of the data against each other.
        Either the total count of elements is displayed or their relative frequency.
        :param DataFrame df: contains the data to be plotted (so filtering should take place outside the method)
                         the dataframe column names should contain the names specified in the following 2 params
        :param string x_name: name of the column to plot on the x-axis
        :param string y_name: name of the column to plot on the y-axis
        :param list of strings x_labels: The labels that should be displayed at the x axis
        :param list of strings y_labels: The labels that should appear in the legend of the grouping
        :param bool relative_frequencies: If we want to plot relative frequencies (otherwise total count)
        :param bool labels_newline: If the labels that we provide in x_labels or y_labels contain linebreaks
        :return: Contingency table as a dataframe
        """
        # pandas crosstab function expects e.g. to get 2 arrays. Those should have same length.
        # If we want all possible combinations of e.g. [1,2] and [3,4,5], we need to bring it in the form of
        # [1,1,1,2,2,2] --> for x_labels we do that
        # [3,4,5,3,4,5] --> for y_labels we do that
        repetitions = len(y_name)

        # get from [a,b,c] to [a,a,a,b,b,b,c,c,c] if repetitions = 3 for example
        new_labels = []
        for label in x_labels:
            for i in range(repetitions):
                new_labels.append(label)
        x_labels = new_labels
        y_labels = len(x_labels) * y_labels

        ser_x = pd.Series.from_array(x_labels)
        ser_y = pd.Series.from_array(y_labels)

        # make an empty crosstable containing all combinations listed above
        # this is the "scheme" of out crosstable
        df_empty = pd.crosstab(ser_x, ser_y, dropna=False)
        df_empty.replace(df_empty, 0, inplace=True)  # create empfty cross tab

        if labels_newline:
            d1 = self.make_mapping_from_labels(x_labels)
            d2 = self.make_mapping_from_labels(y_labels)
            d = {**d1, **d2}
            df = df.replace(d)

        # now extract the series from the dataframe that contain the survey data
        a = df[x_name]
        b = df[y_name]

        # also make a crosstable out of them, by default it will contain the counts
        df_joint = pd.crosstab(a, b)

        # now insert the one with the correct counts to the one with the correct schema
        df_new = df_empty.add(df_joint, fill_value=0, axis='index')

        if relative_frequencies:
            # row relative frequency by division through sum of row/column
            df_new = df_new.div(df_new.sum(axis=1), axis=0)

        return df_new

    def make_heatmap(self, df_cross, title="", annot=False):
        """
        This method gets a contingency table and plots it as a heatmap
        :param DataFrame df_cross: A contingency table in form of a dataframe
        :param string title: Title of the plot
        :param bool annot: If we want the counts written in the cells of the heatmap
        :return: plot axis
        """
        ax = sns.heatmap(df_cross, annot=annot).set_title(title, fontsize=18)
        return ax

    def make_mosaic_plot(self, df, x_name, y_name, title="", annot=False):
        """
        :param DataFrame df: contains the data to be plotted (so filtering should take place outside the method)
                         the dataframe column names should contain the names specified in the following 2 params
        :param string x_name: name of the column to plot on the x-axis
        :param string y_name: name of the column to plot on the y-axis
        :param string title: Title of the plot
        :param bool annot: If we want the lables written in the cells of the mosaic
        :return: Axis
        """
        # helper funciont to make it possible to have no text inside the blocks
        def return_empty(key):
            return ''
        if annot:
            b, ax = mosaic(df, [x_name, y_name],label_rotation=[70,0])
        else:
            b, ax = mosaic(df, [x_name,y_name], labelizer=return_empty,label_rotation=[70,0])
        b.suptitle(title, fontsize=18)
        plt.xticks(rotation=70)
        return ax

    def make_boxplots(self, df, x_name, y_name, title="", x_axlabel="", y_axlabel="", x_labels=[], y_labels=[],
                      labels_newline=True):
        """
        Method to create multiple boxplot for the two properties given for x and y
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
        :return: Axis of plot
        """
        # if labels have a new line, we need to match them over the labels in the dataframe given
        if labels_newline:
            d1 = self.make_mapping_from_labels(x_labels)
            d2 = self.make_mapping_from_labels(y_labels)
            d = {**d1, **d2}
            df = df.replace(d)
        if not x_labels:
            ax = sns.boxplot(x=x_name, y=y_name, data=df, whis=np.inf).set_title(title, fontsize=18)
        else:
            ax = sns.boxplot(x=x_name, y=y_name, data=df, whis=np.inf, order=x_labels).set_title(title, fontsize=18)
        plt.xticks(rotation=70)
        plt.yticks([i for i in range(0, len(y_labels))], y_labels)

        # if user wants to set axis labels manually
        if x_axlabel:
            plt.xlabel(x_axlabel)
        if y_axlabel:
            plt.ylabel(y_axlabel)
        return ax