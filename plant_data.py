import pandas as pd
import matplotlib.pyplot as plt
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


plant_data_dir = '/media/ben/DATA/plantdata'


def compile_plant_data(input_dir, output_file):
    source_dir = os.path.join(plant_data_dir, input_dir)
    counter = 0
    dataset = []
    inception = get_inceptionv3()
    for file in os.listdir(source_dir):
        # find xml files in the directory
        if file.endswith('.xml'):
            if counter % 100 == 0:
                print(counter)
            # read class label from xml file, and get image from specified jpg with name mediaID
            with open(os.path.join(source_dir, file), 'r') as fp:
                bs = BeautifulSoup(fp.read(), features='html.parser')
            mediaID = bs.mediaid.get_text()
            image = cv2.imread(os.path.join(source_dir, mediaID + '.jpg'))
            label = bs.classid.get_text()
            # preprocess image and feed to inception for feature generation
            image = preprocess(image)
            image = tf.data.Dataset.from_tensors([image])
            features = inception.predict(image, verbose=0, steps=1)[0]
            # build the new dict of features and label, and add it to the dataset list
            example = {}
            for i, feature in enumerate(features):
                example['feature' + str(i)] = feature
            example['label'] = label
            dataset.append(example)
            counter += 1
    # write the dataset to a json for future learning
    with open(os.path.join(source_dir, output_file)) as out:
        json.dump(dataset, out)


target_directories = ['test', 'train']
compile_plant_data('train', 'train_compiled.json')
