from guidata.tests.all_features import TestParameters
from guidata.dataset.datatypes import DataSetGroup

if __name__ == "__main__":
    # Create QApplication
    import guidata
    _app = guidata.qapplication()

    e1 = TestParameters("DataSet #1")
    e2 = TestParameters("DataSet #2")
    g = DataSetGroup( [e1, e2], title='Parameters group' )
    g.edit()
    print(e1)
    g.edit()
