import cv2
import os
import tensorflow as tf
from bs4 import BeautifulSoup
import json
from tensorflow import keras


def preprocess(image):
    resized_image = tf.image.resize(image, [299, 299])
    final_image = keras.applications.inception_v3.preprocess_input(resized_image)
    return final_image


def get_inceptionv3():
    base_model = keras.applications.inception_v3.InceptionV3(include_top=False, weights='imagenet',
                                                             input_shape=(299, 299, 3), pooling='avg')
    return base_model


plant_data_dir = 'D:\\plantdata'


def compile_plant_data(input_dir, output_file, parallel_num):
    source_dir = os.path.join(plant_data_dir, input_dir)
    counter = 0
    dataset = []
    inception = get_inceptionv3()
    label_list = []
    image_list = []
    examples = os.listdir(source_dir)
    for file in examples:
        if file.endswith('xml'):
            # find xml files in the directory
            if counter % 100 == 0:
                print(counter)
                print('len of dataset is currently:', len(dataset))
                if len(dataset) > 0:
                    print('len of index 1 and -1 are', len(dataset[0]), len(dataset[len(dataset) - 1]))
            # read class label from xml file, and get image from specified jpg with name mediaID
            try:
                with open(os.path.join(source_dir, file), 'r') as fp:
                    bs = BeautifulSoup(fp.read(), features='html.parser', from_encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    fp.close()
                    with open(os.path.join(source_dir, file), 'r', encoding='iso-8859-1') as fp:
                        bs = BeautifulSoup(fp.read(), features='html.parser', from_encoding='utf-8')
                except:
                    print('could not decode characters in file:', file)
                    continue
            mediaID = bs.mediaid.get_text()
            image_list.append(preprocess(cv2.imread(os.path.join(source_dir, mediaID + '.jpg'))))
            label_list.append(bs.classid.get_text())
            # fee images into inception in groups to improve total runtime
            if len(image_list) >= parallel_num:
                feature_list = inception.predict(tf.data.Dataset.from_tensors(image_list), verbose=0, steps=1)
                # build the new dict of features and label, and add it to the dataset list
                example = []
                for data, label in zip(feature_list, label_list):
                    for i, feature in enumerate(data):
                        example.append(float(feature))
                    example.append(int(label))
                    dataset.append(example)
                    example = []
                image_list.clear()
                # clear tracker lists and write to outfile
                label_list.clear()
            counter += 1
    # finish the last even if there are less than parallel_num
    if len(image_list) > 0:
        feature_list = inception.predict(tf.data.Dataset.from_tensors(image_list), verbose=0, steps=1)
        for data, label in zip(feature_list, label_list):
            for i, feature in enumerate(data):
                example.append(float(feature))
            example.append(int(label))
            dataset.append(example)
    with open(os.path.join(plant_data_dir, output_file), 'w') as out:
        json.dump(dataset, out)


target_directories = ['test', 'train']
for dir in target_directories:
    compile_plant_data(dir, dir + '_compiled.json', 8)
