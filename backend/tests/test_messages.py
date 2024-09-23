from app.messages import MessageStatus, ResultMessage


def test_success():
    result = ResultMessage.success("OK")
    assert result.status == MessageStatus.SUCCESS
    assert result.message == "OK"


def test_fail():
    result = ResultMessage.fail("Failure")
    assert result.status == MessageStatus.FAIL
    assert result.message == "Failure"


def test_error():
    result = ResultMessage.error("Error")
    assert result.status == MessageStatus.ERROR
    assert result.message == "Error"
