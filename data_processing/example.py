from data_processing.downloader import Downloader
from data_processing.processor import MLSurveyProcessor

# set the variables to access your survey
lsspath = "path/to/your/lss/file"
url = "link/to/your/Lime/Survey"
username = "your_username"
passwd = "your_password"
userid = 1 # find in the lime interface under survey users
surveyid = 1 # find in the lime interface

loader = Downloader(url, username, passwd, userid, surveyid, lsspath)
survey = loader.create_survey()

processor = MLSurveyProcessor(survey)
user_output = processor.process_user_input()
