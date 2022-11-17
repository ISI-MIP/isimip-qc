import logging as python_logging

VRDETAIL = 23
CHECKING = 22
SUMMARY = 21

python_logging.addLevelName(VRDETAIL, 'VRDETAIL')
python_logging.addLevelName(CHECKING, 'CHECKING')
python_logging.addLevelName(SUMMARY, 'SUMMARY')
