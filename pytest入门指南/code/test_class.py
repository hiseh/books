class TestClass:
    def test_one(self):
        x = 'this'
        assert 'h' in x

    def test_two(self):
        x = 'hello'
        assert hasattr(x, 'index')

    def test_function(self, record_xml_property):
        record_xml_property("example_key", 1)
        assert 0
