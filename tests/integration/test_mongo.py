from counter.adapters.count_repo import CountMongoDBRepo
from counter.domain.models import ObjectCount


class TestMongoRepo:

    def setup_method(self):
        self.repo = CountMongoDBRepo(host="localhost",port=27017,database="test_counter")
        counter_col = self.repo._CountMongoDBRepo__get_counter_col()
        counter_col.delete_many({})

    def test_insert_new_counts(self):
        self.repo.update_values([ObjectCount("cat", 2),ObjectCount("dog", 1)])
        result = sorted(self.repo.read_values(),key=lambda x: x.object_class)
        assert result == [ObjectCount("cat", 2),ObjectCount("dog", 1)]

    def test_increment_existing_counts(self):
        self.repo.update_values([ObjectCount("cat", 5)])
        self.repo.update_values([ObjectCount("cat", 2)])
        result = self.repo.read_values(["cat"])
        assert result == [ObjectCount("cat", 7)]