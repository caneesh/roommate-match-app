"""
Unit tests for the matching engine
"""
import pytest
from engines.matching_engine import MatchingEngine


@pytest.fixture
def matching_engine():
    return MatchingEngine()


@pytest.fixture
def profile_early_bird():
    """Early bird, clean, quiet profile"""
    return {
        'id': '1',
        'sleep_schedule_weekday': 2,
        'sleep_schedule_weekend': 3,
        'light_sensitivity': 7,
        'noise_tolerance': 3,
        'quiet_hours_importance': 8,
        'cleanliness_kitchen': 8,
        'cleanliness_bathroom': 8,
        'cleanliness_common': 7,
        'chore_frequency': 5,
        'clutter_tolerance': 3,
        'guests_overnight_per_week': 1,
        'partner_frequency': 3,
        'party_frequency': 1,
        'social_level_home': 4,
        'introvert_extrovert': 3,
        'thermostat_preference': 68,
        'thermostat_flexibility': 6,
        'wfh_frequency': 5,
        'shared_space_work_need': 7,
        'food_sharing_comfort': 3,
        'toiletries_sharing_comfort': 2,
        'borrowing_comfort': 4,
        'has_pets': False,
        'pet_types': [],
        'has_allergies': True,
        'allergy_details': ['cats'],
        'smoking_tolerance': 0,
        'vaping_tolerance': 0,
        'drug_tolerance': 0,
        'alcohol_comfort': 6,
        'communication_directness': 8,
        'communication_channel': 'text',
        'response_time_expectation': 12,
        'conflict_style': 'collaborative',
        'budget_stress': 6,
        'expense_splitting_preference': 'equal',
        'spirituality_importance': 3,
        'political_discussion_comfort': 5,
        'sustainability_importance': 8,
        'dealbreakers': ['no_smoking', 'no_pets'],
        'flexible_on': ['thermostat'],
    }


@pytest.fixture
def profile_night_owl():
    """Night owl, social, relaxed profile"""
    return {
        'id': '2',
        'sleep_schedule_weekday': 8,
        'sleep_schedule_weekend': 9,
        'light_sensitivity': 3,
        'noise_tolerance': 8,
        'quiet_hours_importance': 4,
        'cleanliness_kitchen': 5,
        'cleanliness_bathroom': 6,
        'cleanliness_common': 5,
        'chore_frequency': 3,
        'clutter_tolerance': 7,
        'guests_overnight_per_week': 3,
        'partner_frequency': 7,
        'party_frequency': 5,
        'social_level_home': 8,
        'introvert_extrovert': 8,
        'thermostat_preference': 72,
        'thermostat_flexibility': 7,
        'wfh_frequency': 2,
        'shared_space_work_need': 4,
        'food_sharing_comfort': 7,
        'toiletries_sharing_comfort': 5,
        'borrowing_comfort': 8,
        'has_pets': False,
        'pet_types': [],
        'has_allergies': False,
        'allergy_details': [],
        'smoking_tolerance': 3,
        'vaping_tolerance': 4,
        'drug_tolerance': 2,
        'alcohol_comfort': 9,
        'communication_directness': 6,
        'communication_channel': 'any',
        'response_time_expectation': 48,
        'conflict_style': 'compromising',
        'budget_stress': 4,
        'expense_splitting_preference': 'flexible',
        'spirituality_importance': 2,
        'political_discussion_comfort': 7,
        'sustainability_importance': 5,
        'dealbreakers': [],
        'flexible_on': ['cleanliness', 'noise'],
    }


@pytest.fixture
def profile_similar_early_bird():
    """Similar to early bird profile"""
    return {
        'id': '3',
        'sleep_schedule_weekday': 3,
        'sleep_schedule_weekend': 4,
        'light_sensitivity': 6,
        'noise_tolerance': 4,
        'quiet_hours_importance': 7,
        'cleanliness_kitchen': 7,
        'cleanliness_bathroom': 7,
        'cleanliness_common': 7,
        'chore_frequency': 4,
        'clutter_tolerance': 4,
        'guests_overnight_per_week': 1,
        'partner_frequency': 4,
        'party_frequency': 2,
        'social_level_home': 5,
        'introvert_extrovert': 4,
        'thermostat_preference': 69,
        'thermostat_flexibility': 7,
        'wfh_frequency': 4,
        'shared_space_work_need': 6,
        'food_sharing_comfort': 4,
        'toiletries_sharing_comfort': 3,
        'borrowing_comfort': 5,
        'has_pets': False,
        'pet_types': [],
        'has_allergies': False,
        'allergy_details': [],
        'smoking_tolerance': 0,
        'vaping_tolerance': 0,
        'drug_tolerance': 0,
        'alcohol_comfort': 7,
        'communication_directness': 7,
        'communication_channel': 'text',
        'response_time_expectation': 24,
        'conflict_style': 'collaborative',
        'budget_stress': 5,
        'expense_splitting_preference': 'equal',
        'spirituality_importance': 4,
        'political_discussion_comfort': 6,
        'sustainability_importance': 7,
        'dealbreakers': ['no_smoking'],
        'flexible_on': ['thermostat', 'guests'],
    }


def test_high_compatibility_similar_profiles(matching_engine, profile_early_bird, profile_similar_early_bird):
    """Test that similar profiles get high compatibility scores"""
    result = matching_engine.calculate_compatibility(profile_early_bird, profile_similar_early_bird)

    assert result['passes_dealbreakers'] is True
    assert result['score'] > 70, f"Expected high compatibility score, got {result['score']}"
    assert len(result['top_alignments']) > 0
    assert 'category_scores' in result


def test_low_compatibility_opposite_profiles(matching_engine, profile_early_bird, profile_night_owl):
    """Test that opposite profiles get lower compatibility scores"""
    result = matching_engine.calculate_compatibility(profile_early_bird, profile_night_owl)

    assert result['passes_dealbreakers'] is True
    assert result['score'] < 70, f"Expected lower compatibility score, got {result['score']}"
    assert len(result['top_mismatches']) > 0


def test_dealbreaker_violation(matching_engine, profile_early_bird):
    """Test that dealbreaker violations result in failed match"""
    # Create profile with pets (violates early_bird's dealbreaker)
    profile_with_pets = profile_early_bird.copy()
    profile_with_pets['id'] = '4'
    profile_with_pets['has_pets'] = True
    profile_with_pets['pet_types'] = ['cat']
    profile_with_pets['dealbreakers'] = []

    result = matching_engine.calculate_compatibility(profile_early_bird, profile_with_pets)

    assert result['passes_dealbreakers'] is False
    assert result['score'] == 0


def test_sleep_compatibility_scoring(matching_engine):
    """Test sleep compatibility scoring"""
    profile_a = {'sleep_schedule_weekday': 2, 'sleep_schedule_weekend': 2,
                 'light_sensitivity': 5, 'noise_tolerance': 5, 'quiet_hours_importance': 5}
    profile_b = {'sleep_schedule_weekday': 2, 'sleep_schedule_weekend': 2,
                 'light_sensitivity': 5, 'noise_tolerance': 5, 'quiet_hours_importance': 5}

    score = matching_engine._score_sleep_compatibility(profile_a, profile_b)
    assert score > 90, "Identical sleep preferences should score very high"


def test_cleanliness_compatibility_scoring(matching_engine):
    """Test cleanliness compatibility scoring"""
    profile_a = {'cleanliness_kitchen': 8, 'cleanliness_bathroom': 8, 'cleanliness_common': 8}
    profile_b = {'cleanliness_kitchen': 3, 'cleanliness_bathroom': 3, 'cleanliness_common': 3}

    score = matching_engine._score_cleanliness_compatibility(profile_a, profile_b)
    assert score < 40, "Large cleanliness mismatch should score low"


def test_group_matching(matching_engine, profile_early_bird, profile_similar_early_bird, profile_night_owl):
    """Test group matching functionality"""
    profiles = [profile_early_bird, profile_similar_early_bird, profile_night_owl]

    results = matching_engine.match_group(profiles, group_size=2)

    assert len(results) > 0, "Should return at least one group"
    assert all('avg_score' in r for r in results), "All results should have avg_score"
    assert all('group' in r for r in results), "All results should have group members"

    # Best group should be the two similar profiles
    best_group = results[0]
    assert len(best_group['group']) == 2


def test_category_scores_present(matching_engine, profile_early_bird, profile_similar_early_bird):
    """Test that all category scores are calculated"""
    result = matching_engine.calculate_compatibility(profile_early_bird, profile_similar_early_bird)

    expected_categories = ['sleep', 'cleanliness', 'guests', 'temperature', 'communication', 'sharing', 'lifestyle', 'overall']
    for category in expected_categories:
        assert category in result['category_scores'], f"Missing category: {category}"
        assert 0 <= result['category_scores'][category] <= 100, f"Category {category} score out of range"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
