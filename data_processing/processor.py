import re

import pandas as pd
from limepy.wrangle import Survey
from lxml.html import fromstring
from lxml.html.clean import Cleaner


class SurveyProcessor(object):
    """
    A general class to process Lime Survey surveys and bring them into a nice format for analyses.
    """

    def __init__(self, survey):
        """
        Initialization
        :param Survey survey: An object holding the survey to be processed.
        """
        self.survey = survey

    def filter_completed_questions(self, data_df, lastpage=39):
        """
        Function to keep only the data of completed surveys
        :param DataFrame data_df: pandas DF that contains the survey response data
        :param int lastpage: int that specifies what the last question in the survey is (in our it is 39,
                therefor the default value)
        :return DataFrame: A dataframe that contains only the completed results
        """

        # create a boolean mask to check whether the
        is_completed = data_df['lastpage'] == lastpage

        # use the boolean mask to filter the relevant rows in the dataframe
        return data_df[is_completed]

    def clean_question_text(self, text):
        """
        Function to remove all the javascript and formatting from the question text
        :param str text: Text to be cleaned from formatting.
        :return str result: Cleaned text.
        """
        cleaner = Cleaner(
            comments=True,  # True = remove comments
            meta=True,  # True = remove meta tags
            scripts=True,  # True = remove script tags
            embedded=True,  # True = remove embeded tags
        )
        clean_dom = cleaner.clean_html(text)
        cleaner_text = fromstring(clean_dom).text_content()

        # now remove all the \x\n etc. from text
        result = cleaner_text.replace('\n', ' ').replace('\xa0', ' ')
        return result

    def make_answer_code_to_text_mapping(self):
        """
        Method to generate a mapping from answer codes to answer texts
        The form is the following:
            For list questions (single choice):  key=AWA1, value = {A1:'hashdh',A2:'ahsjh',...}
            For multiple choice: key=AWA2, value = {SQ001:'hfafhuhu',SQ002:'ahsuh',...}
            For ranking: key=IMP5, value = {A1:'sdghuu',....}
            For array: key=PRAtable, value = {A1:'faufh',....} --> we could have an individual quesion
                in the array, however they all have the same answer possibilities, so it would be a
                waste of space

        :return dict of dict result: A dictionary with question codes as keys and dictionaries as values
            that hold each answer codes as keys and the corresponding answer text as values
        """
        colnames = list(self.survey.dataframe.columns)

        # this is the dict we return
        mapping = {}

        for qid, question in self.survey.questions.items():

            # this is the dict for the single question with all answer possibilities
            question_map = {}
            if 'answers' in question:
                for scale in question['answers']:
                    for answer in question['answers'][scale]:
                        question_map[answer['code']] = answer['answer']

            elif 'subquestions' in question:  # in multiple choice and ranking
                for scale in question['subquestions']:
                    for sq in question['subquestions'][scale]:
                        key = sq['title']
                        question_map[key] = sq['question']
            mapping[question['title']] = question_map
        return mapping

    def obtain_answer_text(self, q_code, mapping, a_code=[]):
        """
        Method to obtain the long answer text for an answer code in a specific question.
        For ranking we have the shape IMP5[1] and need to lookup the answer code like IMP5[A1]
        :param str q_code: code of the question
        :param str a_code: answer code for which we want to receive the long text, it is not mandatory,
            because in the multiple choice and ranking,
            the answer code is already in the quetion code like in AWA[SQ001], it is SQ001
        :param dict mapping: the dict with all the mappings we have created with make_answer_code_to_text_mapping()

        :return str answertext: The text with the answer.
        """

        # the question code is either in the form AWA1, or AWA2[SQ001]
        # so either we can query the mapping directly or we need to extract what is

        # case extraction (multiple choice, ranking)
        # for array
        if '[' in q_code:
            inner_part = q_code[q_code.find("[") + 1:q_code.find("]")]  # what is inside []
            outer_part = q_code[:q_code.find("[")]  # what is before []
            text = mapping[outer_part][inner_part]

        # case just a plain form like 'AWA1' (list)
        else:
            text = mapping[q_code][a_code]

        return text

    def convert_answer_code_to_int(self, ans_code):
        """
        Method to convert the answer code into an integer. This is for machine readability.
        A1 is translated to 1, SQ001 to 1 etc.
        :param str ans_code: A string containing the answer code.

        :return int: An integer representing the answer code.
        """

        if not isinstance(ans_code, str):
            raise Exception('The answer code should be a string.')

        # one type of multiple choice has also the form of Y for yes and empty for no....
        if ans_code == 'Y':
            return 1
        else:
            ans = re.sub(r"\D", "", ans_code)  # keep only digits
        return int(ans)

    def create_question_overview_df(self):
        """
        Method to create a dataframe that holds a mapping from every question code to
        the corresponding question text and type
        :return DataFrame: Mapping
        """

        questions = self.survey.questions

        # create an empty lists to append the columns to
        all_answer_columns = []
        all_question_names = []
        all_question_types = []
        all_question_indices = []

        # iterate over all questions, q holds the question ID in form of '1', '2', ...
        for q in questions:

            question_code = questions[q]['title']
            question_text = self.clean_question_text(questions[q]['question'])
            question_type = questions[q]['question_type']
            question_index = questions[q]['qid']

            # Process questions according to their type.
            if question_type == "Multiple choice" or question_type == "Multiple choice with comments" or question_type == "Array":
                # iterate over all subquestions (by the format of limepy, the subquestions section always has key '0')
                for s in questions[q]['subquestions']['0']:
                    sub_question_code = (s['title'])
                    sub_question_text = self.clean_question_text(s['question'])

                    merged_code = question_code + "[" + sub_question_code + "]"
                    merged_text = question_text + " - " + sub_question_text
                    all_answer_columns.append(merged_code)
                    all_question_names.append(merged_text)
                    all_question_types.append(question_type)
                    all_question_indices.append(question_index)

            # in Rankin the naming of the "subquestions" is slightly different and called "answer"
            elif question_type == "Ranking":
                # iterate over all possible answers (by the format of limepy,
                # the subquestions section always has key '0')
                for s in questions[q]['answers']['0']:
                    sub_question_code = (s['sortorder'])
                    sub_question_text = self.clean_question_text(s['answer'])

                    merged_code = question_code + "[" + sub_question_code + "]"
                    merged_text = question_text + " - " + sub_question_text
                    all_answer_columns.append(merged_code)
                    all_question_names.append(merged_text)
                    all_question_types.append(question_type)
                    all_question_indices.append(question_index)

            # there is no subtype to be handled, like in normal text
            # and the data can be appended directly
            else:
                all_answer_columns.append(question_code)
                all_question_names.append(question_text)
                all_question_types.append(question_type)
                all_question_indices.append(question_index)

        # Make the dataframe with the Question code as a header and text and type as rows
        survey_answers_df = pd.DataFrame(list(zip(all_question_names, all_question_types, all_question_indices)),
                                         index=all_answer_columns,
                                         columns=['Question', 'Question Type', 'Lime Index']).T

        return survey_answers_df

    def convert_questions_to_df(self):
        """
         This creates "the database scheme" for the survey I made up.
         It has 2 indices, the upper index is the question code as it falls out of Lime Survey (e.g. DEM1)
         The second index refers to specific formats for the question.
         We would like to have several formats (machine readable: int that can be read out
         and put into libraries like seaborn directly, answer code: like it falls out of the survey, and
         answer text, which is the according long text for the answer. This fastens the lookup for machine
         readable and generated results to the real world-answers.
         :return Dataframe: Empty dataframe that has a multi-index structure according to the survey
         """

        questions = self.survey.questions

        # collect all dataframes; for every (sub)question a 2-index dataframe is created
        # so that they can be merged at the end
        frames = []

        # iterate over all questions and treat them according to the question type
        for q in questions:
            question_code = questions[q]['title']
            question_text = self.clean_question_text(questions[q]['question'])
            question_type = questions[q]['question_type']

            # if there is only one element to select (List radio or (List dropdown)
            # create 3 columns: one for machine readable code (e.g. 1,..,n), one for answer code (e.g. A1,...An)
            # and one for long text answer
            if question_type == "List radio" or question_type == "List dropdown":

                second_level_index = ["a_code", "a_text", "a"]
                header = pd.MultiIndex.from_product([[question_code],
                                                     second_level_index], names=['code', 'version'])

                df = pd.DataFrame(columns=header)

                # append the new cdataframe
                frames.append(df)

            # for Multiple choice questions append two columns per answer.
            # a machine readable one (0/1 for no or yes) and one with the text of this subquestion
            # the text field is not really necessary, however, it helps to have it in the row
            # so we can extract it more easily during analyses
            elif question_type == "Multiple choice":

                # iterate over all subquestions (by the format of limepy, the subquestions section always has key '0')
                for s in questions[q]['subquestions']['0']:
                    sub_question_code = (s['title'])
                    merged_code = question_code + "[" + sub_question_code + "]"

                    second_level_index = ["a_text", "a"]
                    header = pd.MultiIndex.from_product([[merged_code],
                                                         second_level_index], names=['code', 'version'])
                    df = pd.DataFrame(columns=header)

                    # append the new cdataframe
                    frames.append(df)

            # if there is only one element to select (List radio or (List dropdown) + a comment
            # create 4 columns: the 3 from list + an additional one for the comment
            elif question_type == "List with comment":

                second_level_index = ["a_code", "a_text", "a", question_code + "[comment]"]
                header = pd.MultiIndex.from_product([[question_code],
                                                     second_level_index],
                                                    names=['code', 'version'])

                df = pd.DataFrame(columns=header)

                # append the new cdataframe
                frames.append(df)

            # for Multiple choice questions append three columns per answer.
            # like Multiple choice + comment field
            elif questions[q]['question_type'] == "Multiple choice with comments":

                # iterate over all subquestions (by the format of limepy, the subquestions section always has key '0')
                for s in questions[q]['subquestions']['0']:
                    sub_question_code = (s['title'])
                    merged_code = question_code + "[" + sub_question_code + "]"

                    second_level_index = ["a_text", "a", question_code + "[" + sub_question_code + "comment]"]
                    header = pd.MultiIndex.from_product([[merged_code],
                                                         second_level_index], names=['code', 'version'])
                    df = pd.DataFrame(columns=header)

                    # append the new cdataframe
                    frames.append(df)

            # here we need 2 columns per possible answer (like multiple choice).
            # One that contains the text.
            # a second one that should be machine readable:
            # Results of the participants are entered with integers. 1 shows highest priority, n lowest,
            # 0 shows that it was not selected by the participant
            elif questions[q]['question_type'] == "Ranking":

                # iterate over all answers (by the format of limepy, the answers section always has key '0')
                for a in questions[q]['answers']['0']:
                    answer_code = a['sortorder']
                    merged_code = question_code + "[" + answer_code + "]"

                    second_level_index = ["a", "a_text"]
                    header = pd.MultiIndex.from_product([[merged_code],
                                                         second_level_index],
                                                        names=['code', 'version'])
                    df = pd.DataFrame(columns=header)

                    # append the new cdataframe
                    frames.append(df)

            # each question in the array is to be treated like a normal list radio question and should therefore
            # receive 3 columns
            elif questions[q]['question_type'] == "Array":

                second_level_index = ["a_code", "a_text", "a"]

                # iterate over all subquestions (by the format of limepy, the subquestions section always has key '0')
                for s in questions[q]['subquestions']['0']:
                    sub_question_code = (s['title'])  # subquestion code
                    merged_code = question_code + "[" + sub_question_code + "]"  # bring the codes together

                    header = pd.MultiIndex.from_product([[merged_code],
                                                         second_level_index], names=['code', 'version'])

                    df = pd.DataFrame(columns=header)

                    # append the new cdataframe
                    frames.append(df)

            # one column for the free text
            elif questions[q]['question_type'] == "Long free text" or questions[q][
                'question_type'] == "Short free text":

                second_level_index = ["a"]
                header = pd.MultiIndex.from_product([[question_code],
                                                     second_level_index], names=['code', 'version'])

                df = pd.DataFrame(columns=header)

                # append the new dataframe
                frames.append(df)

            # Case for questions of which the type is not listed
            else:
                print("error, type not known ", questions[q]['question_type'])

        # create an empty dataframe from all the individual ones
        result = pd.concat(frames)
        return result

    def process_user_input(self, completed_only=True, fill_na=True):
        """
            Take a survey and transform the responses to the pandas dataframe
            :param bool completed_only: If it is true, we only include users that have gone until the end
            :param bool fill_na: If it is true, we fill the NaN values in the dataframe with 0
           :return DataFrame: A filled version of the dataframe with the scheme specified in survey_df
        """

        # extract participant data and question data from survey object
        survey_df = self.convert_questions_to_df() # Create the scheme for the table in form of an empty DataFrame
        data_df = self.survey.dataframe

        # make a copy to not harm the original object
        survey_df_copy = survey_df.copy()

        if completed_only:  # filter out all non completed surveys
            data_df = self.filter_completed_questions(data_df)

        # create the dictionary for mapping
        mapping = self.make_answer_code_to_text_mapping()

        # now iterate over all participants
        for index, row in data_df.iterrows():

            # for each participant, we hold an empty dict to be filled with values
            participant_dict = {}
            my_question_overview_df = self.create_question_overview_df()

            # and over every value that belongs to them
            for columnName, columnData in row.iteritems():

                # when there is no data, we do not need to make an etry
                # pandas creates the nan values automatically when merging the
                # dict into the dataframe
                if pd.isna(columnData):
                    pass  # do nothing for this datapoint, go directly to next

                # if we have one of the 'other' columns, just write their value
                elif 'other' in columnName:

                    outer_part = columnName[:columnName.find("[")]  # what is before []
                    inner_part = columnName
                    index = (outer_part, inner_part)
                    participant_dict[index] = columnData

                # comment columns do not need a type lookup
                # the text can directly be filled into the data
                elif 'comment' in columnName:
                    lookup_name = columnName.replace('comment', '').replace('[]', '')
                    index = (lookup_name, columnName)
                    participant_dict[index] = columnData

                # normal column
                else:

                    # if we have the metadata columns just fill them as they come
                    if columnName in ['submitdate', 'lastpage', 'startlanguage', 'seed', 'startdate', 'datestamp',
                                      'id']:
                        participant_dict[(columnName, '')] = columnData

                    # if we still encounter a question type that we have not foreseen
                    # raise exception - better to be safe than sorry
                    elif columnName not in my_question_overview_df.keys():
                        raise Exception('The column you are trying to enter seems not to fit.', columnName)

                    # for specific question type
                    else:
                        # lookup the question type and behave accordingly
                        question_type = my_question_overview_df[columnName]['Question Type']

                        if question_type == "List radio" or question_type == "List dropdown" or question_type == "List with comment":

                            # answer code
                            participant_dict[(columnName, "a_code")] = columnData

                            # respective text
                            participant_dict[(columnName, "a_text")] = self.obtain_answer_text(columnName, mapping,
                                                                                               columnData)

                            # machine readable answer
                            participant_dict[(columnName, "a")] = self.convert_answer_code_to_int(columnData)

                        elif question_type == "Multiple choice" or question_type == "Multiple choice with comments":
                            # here no answer code needed, because already in column name, e.g. AWA2[SQ001]
                            participant_dict[(columnName, "a_text")] = self.obtain_answer_text(columnName, mapping)
                            participant_dict[(columnName, "a")] = self.convert_answer_code_to_int(columnData)

                        # ranking is a special type. column names have the form of IMP5[1] not IMP5[A1]
                        # because they stand for IMP5[rank 1] has had the following answers
                        elif question_type == "Ranking":
                            # just send IMP as question_name
                            outer_part = columnName[:columnName.find("[")]  # what is before [

                            participant_dict[(columnName, "a_text")] = self.obtain_answer_text(outer_part, mapping,
                                                                                               columnData)
                            participant_dict[(columnName, "a")] = self.convert_answer_code_to_int(columnData)

                        elif question_type == "Array":
                            # answer code
                            participant_dict[(columnName, "a_code")] = columnData

                            # respective text
                            outer_part = columnName[:columnName.find("[")]
                            participant_dict[(columnName, "a_text")] = self.obtain_answer_text(outer_part, mapping,
                                                                                          columnData)

                            # machine readable answer
                            participant_dict[(columnName, "a")] = self.convert_answer_code_to_int(columnData)

                        elif question_type == "Long free text" or question_type == "Short free text":
                            participant_dict[(columnName, 'a')] = columnData


                        # Case for questions of which the type is not listed
                        else:
                            # print("error, type not known ", question_type)
                            pass

                            # print(question_type, columnName)


            survey_df_copy = pd.concat([survey_df_copy, pd.DataFrame.from_records([participant_dict])])

        # set the index to the participant ID in Lime Survey for better comparability
        survey_df_copy = survey_df_copy.set_index('id')
        return survey_df_copy


class MLSurveyProcessor(SurveyProcessor):
    """
    Here we have a class for a concrete survey we are running.
    The "database" scheme is adapted according to the real survey data.
    Therefore, it uses the general structure + extra fields
    """

    def convert_questions_to_df(self):
        # get the general structure from the parent class
        result = super().convert_questions_to_df()

        # and add the concrete fields we need
        # the metadata columns (from the front)
        result.insert(0, "submitdate", [])
        result.insert(0, "lastpage", [])
        result.insert(0, "startlanguage", [])
        result.insert(0, "seed", [])
        result.insert(0, "startdate", [])
        result.insert(0, "datestamp", [])
        result.insert(0, "id", [])

        # now add the 'other' fields to
        result.insert(0, ('AWA2', 'AWA2[other]'), [])
        result.insert(0, ('DEM3', 'DEM3[other]'), [])
        result.insert(0, ('IMP3', 'IMP3[other]'), [])
        result.insert(0, ('IMP3', 'IMP3[othercomment]'), [])
        return result
