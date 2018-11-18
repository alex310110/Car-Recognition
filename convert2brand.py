#!python
'''
Convert annotation to car brands only
'''

import os
from glob import glob
import random


class BrandConverter:
    NAME_CSV = 'devkit/names.csv'
    TRAIN_CSV = 'devkit/anno_train.csv'
    TEST_CSV = 'devkit/anno_test.csv'

    def convert_annotation(self):
        '''convert annotation to brand-based'''
        brands = set()
        idx_mapper = dict()

        # build idx_mapper from old ID to old car make and model
        with open(self.NAME_CSV) as f:
            for i, line in enumerate(f):
                line = line.strip()
                idx_mapper[i+1] = line
                # special case for HUMMER
                if not line.startswith('AM'):
                    brands.add(line.split(' ', 1)[0])
        brands = sorted(list(brands))

        # build idx_mapper from old ID to new brand ID
        brand_mapper = dict()
        for i, b in enumerate(brands):
            brand_mapper[b] = i+1
        # special case for HUMMER
        brand_mapper['AM'] = brand_mapper['HUMMER']
        idx_mapper = {k: brand_mapper[v.split(' ', 1)[0]]
                      for k, v in idx_mapper.items()}

        # update files
        with open(self.TRAIN_CSV) as f:
            buf = [head + ',' + str(idx_mapper[int(idx)]) for head, idx in
                   [line.strip().rsplit(',', 1) for line in f]]
        with open(self.TRAIN_CSV, 'w') as f:
            f.write('\n'.join(buf))

        with open(self.TEST_CSV) as f:
            buf = [head + ',' + str(idx_mapper[int(idx)]) for head, idx in
                   [line.strip().rsplit(',', 1) for line in f]]
        with open(self.TEST_CSV, 'w') as f:
            f.write('\n'.join(buf))

        with open(self.NAME_CSV, 'w') as f:
            f.write('\n'.join(brands))

    def order_files(self):
        '''arrange training files into folders of different classes'''
        # create folder
        with open(self.NAME_CSV) as f:
            num_brands = len(f.readlines())
        for i in range(num_brands):
            os.mkdir('data/train/%04d' % (i+1))
            os.mkdir('data/valid/%04d' % (i+1))

        # move train/valid pics
        train_mapper = dict()
        with open(self.TRAIN_CSV) as f:
            for line in f:
                line = line.strip().split(',')
                train_mapper[line[0]] = int(line[-1])
        for i in glob('data/train/*.jpg'):
            target = i.replace('\\', '/').rsplit('/', 1)
            target = target[0] + ('/%04d/' %
                                  train_mapper[target[1]]) + target[1]
            os.rename(i, target)
        for i in glob('data/valid/*.jpg'):
            target = i.replace('\\', '/').rsplit('/', 1)
            target = target[0] + ('/%04d/' %
                                  train_mapper[target[1]]) + target[1]
            os.rename(i, target)

    def balance_files(self, min_max_factor=2):
        '''reduce the number of files in each class to prevent bias result'''
        # count num of files within each classes in test
        class_map = dict()
        with open(self.TEST_CSV) as f:
            for line in f:
                line = line.split(',')
                filename, class_id = line[0], int(line[-1])
                if class_id not in class_map:
                    class_map[class_id] = []
                class_map[class_id].append(filename)
        class_map = sorted(class_map.items(), key=lambda x: len(x[1]))

        # remove files
        backup_folder = 'data/backup_test/'
        os.makedirs(backup_folder, exist_ok=True)
        max_files = int(len(class_map[0][1]) * min_max_factor)
        for _, v in class_map:
            if len(v) <= max_files:
                continue
            victims = random.sample(v, len(v) - max_files)
            for i in victims:
                os.rename('data/test/' + i, backup_folder + i)

        # count num of files within each classes in train/valid
        def deal_folder(folder_name):
            class_map = sorted([
                (d, [f for f in os.listdir('/'.join(['data', folder_name, d]))])
                for d in os.listdir('data/' + folder_name)
            ], key=lambda x: len(x[1]))

            # remove files
            backup_folder = 'data/backup_%s/' % folder_name
            os.makedirs(backup_folder, exist_ok=True)
            max_files = int(len(class_map[0][1]) * min_max_factor)
            for k, v in class_map:
                if len(v) <= max_files:
                    continue
                victims = random.sample(v, len(v) - max_files)
                for i in victims:
                    os.rename('/'.join(['data', folder_name, k, i]),
                              backup_folder + i)
        deal_folder('train')
        deal_folder('valid')


if __name__ == "__main__":
    bc = BrandConverter()
    bc.convert_annotation()
    bc.order_files()
    bc.balance_files()
