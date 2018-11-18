#!python
'''
Convert annotation to car brands only
'''


class BrandConverter:
    NAME_CSV = 'devkit/names.csv'
    TRAIN_CSV = 'devkit/anno_train.csv'
    TEST_CSV = 'devkit/anno_test.csv'

    def convert_annotation(self):
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


if __name__ == "__main__":
    bc = BrandConverter()
    bc.convert_annotation()
