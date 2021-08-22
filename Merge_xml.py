import glob
import xml.etree.ElementTree as ET
import os
import csv
from operator import itemgetter
import wavSpliter
from os import listdir
import os.path



def get_id(row_attrib):
    need_to_cut = row_attrib['{http://nite.sourceforge.net/}id']
    lst = need_to_cut.split('.')
    return int(lst[2].replace(',', ''))


def open_xml(file_path):
    mytree = ET.parse(file_path)
    myroot = mytree.getroot()
    ans = []
    for i, row in enumerate(myroot):
        if row.tag == 'w':
            dict = {}
            dict['id'] = get_id(row.attrib)
            dict['starttime'] = row.attrib['starttime']
            dict['endtime'] = row.attrib['endtime']
            dict['text'] = row.text
            dict['speaker'] = file_path.split('.')[1]
            dict['c'] = row.attrib['c']
            ans.append(dict)
    return ans


def merge_lists(list_of_lists):
    ans = []
    for lst in list_of_lists:
        for hs in lst:
            ans.append(hs)
    return ans


# after i have the merged hash
def isnt_end_of_sentence(word):
    return word not in [',', '.', '!', '?', ':', ';']


def is_end_of_sentence(word):
    return word in ['.', '!', '?', ':', ';']


def isnt_number(word):
    return word not in ['0', 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']


def make_windows2(list_of_dict, file_path, audioName):
    window_size = 10
    countPath = 0
    ans = []
    sentence = ''
    need_to_end = window_size
    end = 0.0

    for i, dic in enumerate(list_of_dict):
        if dic['c'] == 'W' or dic['c'] == '.' or dic['c'] == 'CM' or dic['c'] == 'APOSS':
            if dic['starttime'] == '' and dic['endtime'] == '' and dic['text'] != '-':  # skip background sounds
                continue
            start_time = dic['starttime']
            if start_time == '':
                if is_end_of_sentence(dic['text']):
                    sentence += dic['text'] + ' '

                elif dic['text'] == '-' or "'" in dic['text']:
                    sentence += dic['text']

                elif sentence != '' and (sentence[-1] == "'" or sentence[-1] == "-"):
                    sentence += dic['text']

                elif sentence != '' and sentence[-1] != ' ':
                    sentence += ' ' + dic['text']

                else:
                    sentence += dic['text']

            else:  # word have start time
                start_time = float(dic['starttime'])
                if need_to_end <= start_time:  # end of windows size
                    if not isnt_end_of_sentence(dic['text']):
                        sentence += dic['text']
                    need_to_end += window_size
                    # tmp_dict = {'': i, 'audio_filepath': file_path + str(countPath) + '_' + audioName, 'text': sentence}
                    # tmp_dict = {'filepath': file_path + str(countPath) + '_' + audioName, 'text': sentence}

                    tmp_dict = {'filepath': file_path + str(countPath) + '_' + audioName, 'text': str(sentence)}
                    countPath += window_size
                    if len(sentence) != 0:
                        ans.append(tmp_dict)
                    sentence = ''

                if sentence == '':  # start of a sentence and have a start time
                    if isnt_end_of_sentence(dic['text']):
                        sentence += dic['text']
                        end = start_time + window_size
                        continue

                elif is_end_of_sentence(dic['text']):  # add the end of sentence and space
                    sentence += dic['text'] + ' '

                elif dic['text'] == ',':
                    sentence += dic['text'] + ' '

                elif sentence[-1] != ' ':
                    sentence += ' ' + dic['text']
                else:
                    sentence += dic['text']

    return ans


def make_windows(list_of_dict, file_path, audioName):
    window_size = 10
    countPath = 0
    ans = []

    for i, dic in enumerate(list_of_dict):
        sentence = ''
        start_time = dic['starttime']
        if start_time == '':
            sentence += dic['text']
        else:
            start_time = float(start_time)
            time_limit = start_time + window_size
            end_time = start_time
            dict_tmp = dic
            idx = i
            while idx < len(list_of_dict) and (dict_tmp['starttime'] == '' or float(dict_tmp['starttime']) < time_limit):
                if dict_tmp['starttime'] != '' and float(dict_tmp['starttime']) < time_limit and isnt_end_of_sentence(dict_tmp['text']):
                    sentence += ' '
                if dict_tmp['starttime'] == '' and isnt_number(dict_tmp['text']):
                    if len(dict_tmp['text']) > 1:
                        sentence += ' ' + dict_tmp['text']
                    else:
                        sentence += dict_tmp['text']

                elif dict_tmp['starttime'] != '':
                    sentence += dict_tmp['text']
                end_time = dict_tmp['endtime']
                if end_time != '':
                    end_time = float(end_time)

                idx += 1
                if idx < len(list_of_dict):
                    dict_tmp = list_of_dict[idx]
                else:
                    break
                if dict_tmp['text'] == ',' and sentence[-1] == ' ':
                    sentence = sentence[0:-1]

            tmp_dict = {'': i, 'audio_filepath': file_path + str(countPath) + '_' + audioName, 'text': sentence[1:]}
            ans.append(tmp_dict)
            countPath += 10
            # print(tmp_dict)
    return ans


def makeDire(dirName):
    try:
        # Create target Directory
        os.mkdir(dirName)
        print("Directory ", dirName, " Created ")
    except FileExistsError:
        print("Directory ", dirName, " already exists")


def makeCSV(folderPath, fileName, savePath1, file1):
    xml_files = filter(lambda name: (fileName in name), glob.glob(folderPath + '\\' + r'/*.xml'))
    xml_files = map(lambda xmlFile: (open_xml(xmlFile)), xml_files)
    asd = merge_lists(xml_files)
    sorted_list = sorted(asd, key=itemgetter('id'))

    # to_model = make_windows(sorted_list, 'C:\\Users\\Maor\\PycharmProjects\\speech2text\\audios\\', 'Bdb001.interaction.wav')
    to_model = make_windows2(sorted_list, savePath1, file1)
    # print(to_model)
    keys = to_model[0].keys()
    # print(keys)
    if not os.path.exists('mycsvfile.csv'):
        with open('mycsvfile.csv', 'w', newline='') as output_file:  # TODO save CSV for each xml
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(to_model)
    else:
        with open('mycsvfile.csv', 'a+', newline='') as output_file:  # TODO save CSV for each xml
            dict_writer = csv.DictWriter(output_file, keys)
            # dict_writer.writeheader()
            dict_writer.writerows(to_model)


mypath = 'C:\Kalif\Ariel University\Computer_Science\C\sms C\speech2text\icsi dataset\Signals'
makeDire('audios2')

for folder in listdir(mypath):
    wavFolder = mypath + '\\' + folder
    # print(wavFolder)
    savePath = 'audios2\\' + folder
    file = listdir(wavFolder)[0]  # get the long audio wav


    # makeDire(savePath)  # make a dir to save all the split waves
    # split_wav = wavSpliter.SplitWavAudioMubin(wavFolder, file, savePath) # split audios
    # split_wav.multiple_split(min_per_split=10) # split audios


    makeCSV('Words', folder, savePath+'\\', file)


# folder = listdir(mypath)[-1]
# wavFolder = mypath + '\\' + folder
#
# savePath = 'audios2\\' + folder
# file = listdir(wavFolder)[0]  # get the long audio wav
# makeDire(savePath)
# split_wav = wavSpliter.SplitWavAudioMubin(wavFolder, file, savePath)
# split_wav.multiple_split(min_per_split=10)
# makeCSV('Words', folder, savePath+'\\', file)
