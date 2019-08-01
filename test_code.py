import os
import pytest
import resolveDependencyTree as target

def test_merge_dict_func():
    fdict=target.merge_two_dicts({'a':{1}},{'b':{2}})
    assert fdict  == {'a':{1},'b':{2}}

def test_data_dir():
    assert os.path.exists("data/"), 'the data directory should be in the same folder as python script'

def test_content_of_data_folder():
    assert len(os.listdir("data/") ) > 0, 'the data folder is empty; add distribution folders to it'
