from plugin.db_utils import update_check


def test_answer():
    assert update_check((1,2,3), (1,2,5), [(1,2,2)]) == False
    assert update_check((1,2,3), (1,2,5), [(1,2,3)]) == False
    assert update_check((1,2,3), (1,2,5), [(1,2,4)]) == True
    assert update_check((1,2,3), (1,2,5), [(1,2,5)]) == True
    assert update_check((1,2,3), (1,2,5), [(1,2,6)]) == True
