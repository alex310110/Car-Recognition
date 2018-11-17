#!python
'''
Test against Standford car dataset with annotation from Kaggle:
https://www.kaggle.com/jutrera/stanford-car-dataset-by-classes-folder
'''
import os
import time
import random
from glob import glob

import cv2 as cv
import keras.backend as K
import numpy as np
from console_progressbar import ProgressBar

from utils import load_model


class KaggleTest:
    def __init__(self):
        self.get_annotation()

    def get_annotation(self):
        self.name_map = dict()
        with open('../stanford-car-dataset/names.csv') as f:
            for i, line in enumerate(f):
                self.name_map[i+1] = line.strip()

        self.file_map = dict()
        with open('../stanford-car-dataset/anno_test.csv') as f:
            for line in f:
                line = line.strip().split(',')
                self.file_map[line[0]] = int(line[-1])

    def main(self):
        # init
        pb = ProgressBar(total=100, prefix='Predicting test data',
                         suffix='', decimals=3, length=50, fill='=')
        files = list(map(lambda x: x.replace('\\', '/'),
                         glob('data/test/*')))
        num_samples = len(files)
        wrong_predicts = []
        model = load_model()

        # start predicts
        with open('result.txt', 'w') as out:
            start = time.time()

            for i, path in enumerate(files):
                filename = path.rsplit('/', 1)[-1]
                expected_class_id = self.file_map[filename]

                # predict
                bgr_img = cv.imread(path)
                rgb_img = cv.cvtColor(bgr_img, cv.COLOR_BGR2RGB)
                rgb_img = np.expand_dims(rgb_img, 0)
                preds = model.predict(rgb_img)
                prob = np.max(preds)
                class_id = np.argmax(preds) + 1

                # after predict
                if class_id != expected_class_id:
                    wrong_predicts.append(
                        (path, self.name_map[expected_class_id],
                         self.name_map[class_id], prob))
                out.write('{}\n'.format(str(class_id)))
                pb.print_progress_bar((i + 1) * 100 / num_samples)

        # end and cleanup
        end = time.time()
        seconds = end - start
        K.clear_session()

        if wrong_predicts:
            print("Random 10 wrong predictions:")
            print('\n'.join(map(
                lambda x: '%s should be %s, but '
                'predicted as %s with probability of %f' % x,
                random.sample(wrong_predicts, min(10, len(wrong_predicts)))
            )))
        print('avg fps: {}'.format(str(num_samples / seconds)))
        print('accuracy: %d/%d = %.2f%%' %
              (num_samples - len(wrong_predicts), num_samples,
               100 - len(wrong_predicts) / num_samples * 100))


if __name__ == '__main__':
    KaggleTest().main()
