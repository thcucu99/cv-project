import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from utils.request_lib import ImageBlockRequestMaker
import random
import json
from collections import defaultdict



conditions = {
    'list_01': [
        ('https://raw.githubusercontent.com/thcucu99/cv-project/main/images/original/image_95.png', [4,3,2,1]),
        ('https://raw.githubusercontent.com/thcucu99/cv-project/main/images/original/image_96.png', [3, 4, 1, 2]),
        ('https://raw.githubusercontent.com/thcucu99/cv-project/main/images/original/image_97.png', [1, 2, 3, 4]),
    ],
    'list_02': [
        ('https://raw.githubusercontent.com/thcucu99/cv-project/main/images/original/image_1.png', [3, 4, 1, 2]),
        ('https://raw.githubusercontent.com/thcucu99/cv-project/main/images/original/image_2.png', [1, 2, 3, 4]),
        ('https://raw.githubusercontent.com/thcucu99/cv-project/main/images/original/image_3.png', [4,3,2,1]),
    ]
}



request_dir = '../../Dropbox/CV_project/requests/test'
request_maker = ImageBlockRequestMaker(
    conditions = conditions,
    request_dir = request_dir
)


sessions_per_condition = 1
for i in range(sessions_per_condition):
    request_maker.loop_through_condition_list()