from pathlib import Path
from limepy import download
from limepy.wrangle import Survey
from io import StringIO
import pandas as pd

class Downloader():
    """
    The downloader class serves as a method to access the limepy API
    """
    def __init__(self, url, username, password, userid, surveyid, lsspath):
        self.url = url
        self.username = username
        self.password = password
        self.userid = userid
        self.surveyid = surveyid

        if not lsspath.endswith('.lss'):
            raise Exception("You need to specify the path to a lss file with the survey structure.")
        self.lsspath = lsspath  # path to the lss file with survey structure

    def download_data(self):
        """
        A method to download the data over the Lime Survey API.
        :return DataFrame data: returns the raw data
        """

        data = download.get_responses(self.url, self.username, self.password, self.userid, self.surveyid)
        data_df = pd.read_csv(StringIO(data), sep=';')
        return data_df

    def write_data_as_csv(self, data, path):
        """
        A method to write out the data obtained.
        :param DataFrame data: Data that should be written.
        :param str path: Path to where the data should be written. (e.g. "Data.csv")
        """

        path = Path(path)
        data.to_csv(path)

    def load_survey_structure(self):
        """
        Method to load the Lime Survey description file .lss
        :return str structure: Survey Structure
        """

        my_structure = open(self.lsspath).read()
        return my_structure

    def create_survey(self):
        """
        Method to create a survey object.
        :return Survey survey: The survey object with all the data
        """

        data = self.download_data()
        structure = self.load_survey_structure()

        survey = Survey(data, structure)
        return survey
