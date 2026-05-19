import pytest

from app.services.ranking import calculate_score, rank_trips


class TestCalculateScore:
    def test_low_price_high_rating(self):
        score = calculate_score(100.0, 5.0, 1000.0)
        assert score == pytest.approx(0.95)

    def test_high_price_low_rating(self):
        score = calculate_score(1000.0, 1.0, 1000.0)
        assert score == pytest.approx(0.1)

    def test_price_zero_rating_zero(self):
        score = calculate_score(0.0, 0.0, 1000.0)
        assert score == pytest.approx(0.5)

    def test_rating_exceeds_five(self):
        score = calculate_score(500.0, 10.0, 1000.0)
        assert score == pytest.approx(0.75)

    def test_half_price_half_rating(self):
        score = calculate_score(500.0, 2.5, 1000.0)
        assert score == pytest.approx(0.5)

    def test_zero_price(self):
        score = calculate_score(0.0, 5.0, 1000.0)
        assert score == pytest.approx(1.0)

    def test_price_exceeds_max(self):
        score = calculate_score(2000.0, 5.0, 1000.0)
        assert score == pytest.approx(0.5)

    def test_both_zero(self):
        score = calculate_score(0.0, 0.0, 1000.0)
        assert score == pytest.approx(0.5)


class TestRankTrips:
    def test_rank_by_score(self):
        trips = [
            {"price": 500, "rating": 3.0},
            {"price": 200, "rating": 5.0},
            {"price": 800, "rating": 2.0},
        ]
        ranked = rank_trips(trips)
        assert ranked[0]["price"] == 200
        assert ranked[1]["price"] == 500
        assert ranked[2]["price"] == 800

    def test_empty_list(self):
        assert rank_trips([]) == []

    def test_single_trip(self):
        trips = [{"price": 300, "rating": 4.0}]
        ranked = rank_trips(trips)
        assert len(ranked) == 1
        assert ranked[0]["price"] == 300

    def test_max_price_override(self):
        trips = [
            {"price": 500, "rating": 3.0},
            {"price": 100, "rating": 2.0},
        ]
        ranked = rank_trips(trips, max_price=1000.0)
        assert ranked[0]["price"] == 100
