import pytest
from ai_processor import classifier
from utils.exceptions import ClassifierException

class TestClassifier:
    def test_classify_valid_data(self):
        data = {"text": "sample content"}
        result = classifier.classify(data)
        assert result is not None
    
    def test_classify_empty_data(self):
        with pytest.raises(ClassifierException):
            classifier.classify({})
