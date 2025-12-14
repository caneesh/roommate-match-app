"""
Matching Engine v1 - Rules-based compatibility scoring with explainability
"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import itertools


@dataclass
class DimensionWeight:
    """Weight configuration for compatibility dimensions"""
    # High impact dimensions
    cleanliness: float = 3.0
    guests: float = 3.0
    sleep_noise: float = 2.5
    communication: float = 2.5

    # Medium impact dimensions
    thermostat: float = 1.5
    wfh: float = 1.5
    social: float = 1.5
    sharing: float = 1.5

    # Lower impact dimensions
    lifestyle: float = 1.0
    values: float = 1.0


class MatchingEngine:
    """Core matching engine for roommate compatibility"""

    def __init__(self, weights: Optional[DimensionWeight] = None):
        self.weights = weights or DimensionWeight()

    def calculate_compatibility(
        self,
        profile_a: Dict,
        profile_b: Dict
    ) -> Dict:
        """
        Calculate compatibility between two profiles

        Returns:
            {
                'score': float (0-100),
                'category_scores': dict,
                'top_alignments': list,
                'top_mismatches': list,
                'passes_dealbreakers': bool
            }
        """
        # Check dealbreakers first
        passes_dealbreakers = self._check_dealbreakers(profile_a, profile_b)

        if not passes_dealbreakers:
            return {
                'score': 0,
                'category_scores': {},
                'top_alignments': [],
                'top_mismatches': ['Failed dealbreaker check'],
                'passes_dealbreakers': False
            }

        # Calculate category scores
        category_scores = {
            'sleep': self._score_sleep_compatibility(profile_a, profile_b),
            'cleanliness': self._score_cleanliness_compatibility(profile_a, profile_b),
            'guests': self._score_guests_compatibility(profile_a, profile_b),
            'temperature': self._score_temperature_compatibility(profile_a, profile_b),
            'communication': self._score_communication_compatibility(profile_a, profile_b),
            'sharing': self._score_sharing_compatibility(profile_a, profile_b),
            'lifestyle': self._score_lifestyle_compatibility(profile_a, profile_b),
        }

        # Calculate weighted overall score
        weighted_scores = {
            'sleep': category_scores['sleep'] * self.weights.sleep_noise,
            'cleanliness': category_scores['cleanliness'] * self.weights.cleanliness,
            'guests': category_scores['guests'] * self.weights.guests,
            'temperature': category_scores['temperature'] * self.weights.thermostat,
            'communication': category_scores['communication'] * self.weights.communication,
            'sharing': category_scores['sharing'] * self.weights.sharing,
            'lifestyle': category_scores['lifestyle'] * self.weights.lifestyle,
        }

        total_weight = sum([
            self.weights.sleep_noise,
            self.weights.cleanliness,
            self.weights.guests,
            self.weights.thermostat,
            self.weights.communication,
            self.weights.sharing,
            self.weights.lifestyle,
        ])

        overall_score = sum(weighted_scores.values()) / total_weight
        category_scores['overall'] = overall_score

        # Generate explanations
        top_alignments = self._generate_alignments(category_scores, profile_a, profile_b)
        top_mismatches = self._generate_mismatches(category_scores, profile_a, profile_b)

        return {
            'score': overall_score,
            'category_scores': category_scores,
            'top_alignments': top_alignments[:3],
            'top_mismatches': top_mismatches[:3],
            'passes_dealbreakers': True
        }

    def match_group(
        self,
        profiles: List[Dict],
        group_size: int
    ) -> List[Dict]:
        """
        Find best group matches from a pool of candidates

        Returns list of groups ranked by average compatibility
        """
        if len(profiles) < group_size:
            return []

        results = []

        # Generate all possible combinations
        for combo in itertools.combinations(profiles, group_size):
            # Calculate pairwise compatibility for all pairs in the group
            pairs_scores = []
            total_score = 0
            min_score = 100

            for i, profile_a in enumerate(combo):
                for profile_b in combo[i+1:]:
                    result = self.calculate_compatibility(profile_a, profile_b)
                    if not result['passes_dealbreakers']:
                        # Group fails if any pair fails dealbreakers
                        total_score = 0
                        min_score = 0
                        break
                    pairs_scores.append(result['score'])
                    total_score += result['score']
                    min_score = min(min_score, result['score'])

                if min_score == 0:
                    break

            if min_score > 0:  # Only include groups where all pairs pass
                avg_score = total_score / len(pairs_scores) if pairs_scores else 0
                results.append({
                    'group': [p['id'] for p in combo],
                    'avg_score': avg_score,
                    'min_score': min_score,
                    'pair_scores': pairs_scores
                })

        # Sort by average score (with minimum score as tiebreaker)
        results.sort(key=lambda x: (x['avg_score'], x['min_score']), reverse=True)

        return results

    def _check_dealbreakers(self, profile_a: Dict, profile_b: Dict) -> bool:
        """Check if profiles violate each other's dealbreakers"""
        dealbreakers_a = set(profile_a.get('dealbreakers', []))
        dealbreakers_b = set(profile_b.get('dealbreakers', []))

        # Common dealbreaker checks
        if 'no_pets' in dealbreakers_a and profile_b.get('has_pets'):
            return False
        if 'no_pets' in dealbreakers_b and profile_a.get('has_pets'):
            return False

        if 'no_smoking' in dealbreakers_a and profile_b.get('smoking_tolerance', 0) > 5:
            return False
        if 'no_smoking' in dealbreakers_b and profile_a.get('smoking_tolerance', 0) > 5:
            return False

        if 'no_overnight_guests' in dealbreakers_a and profile_b.get('guests_overnight_per_week', 0) > 2:
            return False
        if 'no_overnight_guests' in dealbreakers_b and profile_a.get('guests_overnight_per_week', 0) > 2:
            return False

        return True

    def _score_sleep_compatibility(self, a: Dict, b: Dict) -> float:
        """Score sleep schedule and noise compatibility (0-100)"""
        # Sleep schedule alignment (weekday and weekend)
        weekday_diff = abs(a['sleep_schedule_weekday'] - b['sleep_schedule_weekday'])
        weekend_diff = abs(a['sleep_schedule_weekend'] - b['sleep_schedule_weekend'])
        sleep_score = 100 - (weekday_diff + weekend_diff) * 5

        # Noise tolerance alignment
        noise_diff = abs(a['noise_tolerance'] - b['noise_tolerance'])
        noise_score = 100 - noise_diff * 10

        # Light sensitivity consideration
        light_diff = abs(a['light_sensitivity'] - b['light_sensitivity'])
        light_score = 100 - light_diff * 8

        return (sleep_score * 0.5 + noise_score * 0.3 + light_score * 0.2)

    def _score_cleanliness_compatibility(self, a: Dict, b: Dict) -> float:
        """Score cleanliness compatibility (0-100)"""
        kitchen_diff = abs(a['cleanliness_kitchen'] - b['cleanliness_kitchen'])
        bathroom_diff = abs(a['cleanliness_bathroom'] - b['cleanliness_bathroom'])
        common_diff = abs(a['cleanliness_common'] - b['cleanliness_common'])

        # Cleanliness mismatches are highly problematic
        kitchen_score = 100 - kitchen_diff * 12
        bathroom_score = 100 - bathroom_diff * 12
        common_score = 100 - common_diff * 10

        return (kitchen_score + bathroom_score + common_score) / 3

    def _score_guests_compatibility(self, a: Dict, b: Dict) -> float:
        """Score guest and social compatibility (0-100)"""
        guests_diff = abs(a['guests_overnight_per_week'] - b['guests_overnight_per_week'])
        partner_diff = abs(a['partner_frequency'] - b['partner_frequency'])
        party_diff = abs(a['party_frequency'] - b['party_frequency'])

        guests_score = 100 - guests_diff * 15
        partner_score = 100 - partner_diff * 10
        party_score = 100 - party_diff * 12

        return (guests_score * 0.4 + partner_score * 0.3 + party_score * 0.3)

    def _score_temperature_compatibility(self, a: Dict, b: Dict) -> float:
        """Score thermostat compatibility (0-100)"""
        temp_diff = abs(a['thermostat_preference'] - b['thermostat_preference'])
        avg_flexibility = (a['thermostat_flexibility'] + b['thermostat_flexibility']) / 2

        # If both are flexible, mismatch matters less
        base_score = 100 - temp_diff * 5
        flexibility_bonus = avg_flexibility * 2

        return min(100, base_score + flexibility_bonus)

    def _score_communication_compatibility(self, a: Dict, b: Dict) -> float:
        """Score communication style compatibility (0-100)"""
        directness_diff = abs(a['communication_directness'] - b['communication_directness'])

        # Conflicting conflict styles
        conflict_penalty = 0
        if (a['conflict_style'] == 'avoidant' and b['conflict_style'] == 'assertive') or \
           (a['conflict_style'] == 'assertive' and b['conflict_style'] == 'avoidant'):
            conflict_penalty = 20

        # Response time expectations
        response_diff = abs(a['response_time_expectation'] - b['response_time_expectation'])
        response_score = 100 - (response_diff / 72) * 30  # Normalize to 0-72 hours

        directness_score = 100 - directness_diff * 8

        return max(0, (directness_score * 0.5 + response_score * 0.5) - conflict_penalty)

    def _score_sharing_compatibility(self, a: Dict, b: Dict) -> float:
        """Score sharing preferences compatibility (0-100)"""
        food_diff = abs(a['food_sharing_comfort'] - b['food_sharing_comfort'])
        toiletries_diff = abs(a['toiletries_sharing_comfort'] - b['toiletries_sharing_comfort'])
        borrowing_diff = abs(a['borrowing_comfort'] - b['borrowing_comfort'])

        food_score = 100 - food_diff * 10
        toiletries_score = 100 - toiletries_diff * 8
        borrowing_score = 100 - borrowing_diff * 10

        return (food_score + toiletries_score + borrowing_score) / 3

    def _score_lifestyle_compatibility(self, a: Dict, b: Dict) -> float:
        """Score overall lifestyle compatibility (0-100)"""
        # Introvert/extrovert alignment
        social_diff = abs(a['introvert_extrovert'] - b['introvert_extrovert'])
        social_score = 100 - social_diff * 8

        # WFH overlap (can be problematic if both WFH and need space)
        wfh_overlap = min(a['wfh_frequency'], b['wfh_frequency'])
        shared_space_need = (a['shared_space_work_need'] + b['shared_space_work_need']) / 2
        wfh_penalty = 0
        if wfh_overlap > 3 and shared_space_need > 7:
            wfh_penalty = 15

        # Substance tolerance alignment
        alcohol_diff = abs(a['alcohol_comfort'] - b['alcohol_comfort'])
        alcohol_score = 100 - alcohol_diff * 8

        return max(0, (social_score * 0.5 + alcohol_score * 0.3 + (100 - wfh_penalty) * 0.2))

    def _generate_alignments(self, scores: Dict, a: Dict, b: Dict) -> List[str]:
        """Generate top alignment descriptions"""
        alignments = []

        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for category, score in sorted_categories[:5]:
            if score > 80:
                if category == 'sleep':
                    alignments.append(f"Similar sleep schedules and noise preferences (score: {score:.0f})")
                elif category == 'cleanliness':
                    alignments.append(f"Aligned cleanliness standards (score: {score:.0f})")
                elif category == 'guests':
                    alignments.append(f"Compatible guest and social preferences (score: {score:.0f})")
                elif category == 'communication':
                    alignments.append(f"Similar communication styles (score: {score:.0f})")
                elif category == 'temperature':
                    alignments.append(f"Agreement on temperature preferences (score: {score:.0f})")

        return alignments

    def _generate_mismatches(self, scores: Dict, a: Dict, b: Dict) -> List[str]:
        """Generate top mismatch descriptions"""
        mismatches = []

        sorted_categories = sorted(scores.items(), key=lambda x: x[1])

        for category, score in sorted_categories[:5]:
            if score < 60 and category != 'overall':
                if category == 'sleep':
                    mismatches.append(f"Different sleep schedules may cause friction (score: {score:.0f})")
                elif category == 'cleanliness':
                    mismatches.append(f"Cleanliness standards differ significantly (score: {score:.0f})")
                elif category == 'guests':
                    mismatches.append(f"Divergent preferences for guests and socializing (score: {score:.0f})")
                elif category == 'communication':
                    mismatches.append(f"Different communication styles need attention (score: {score:.0f})")

        return mismatches
