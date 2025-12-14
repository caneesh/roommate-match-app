"""Matching service - orchestrates matching engine"""
from sqlalchemy.orm import Session
from typing import List, Dict
import models
from engines import MatchingEngine, ConflictPredictor


class MatchingService:
    def __init__(self, db: Session):
        self.db = db
        self.matching_engine = MatchingEngine()
        self.conflict_predictor = ConflictPredictor()

    def run_pairwise_match(
        self,
        resident_a_id: str,
        resident_b_id: str,
        match_run_id: str
    ) -> models.MatchResult:
        """Run matching for a pair of residents"""
        # Get profiles and questionnaires
        profile_a = self._get_profile_dict(resident_a_id)
        profile_b = self._get_profile_dict(resident_b_id)

        # Calculate compatibility
        compat_result = self.matching_engine.calculate_compatibility(profile_a, profile_b)

        # Predict conflict risk
        risk_result = self.conflict_predictor.predict_conflict_risk(
            profile_a, profile_b, compat_result['category_scores']
        )

        # Create match result
        match_result = models.MatchResult(
            match_run_id=match_run_id,
            resident_a_id=resident_a_id,
            resident_b_id=resident_b_id,
            compatibility_score=compat_result['score'],
            risk_score=risk_result['overall_risk'],
            risk_level=risk_result['risk_level'],
            category_scores=compat_result['category_scores'],
            category_risks=risk_result['category_risks'],
            top_alignments=compat_result['top_alignments'],
            top_mismatches=compat_result['top_mismatches'],
            mitigation_tips=risk_result['mitigation_tips'],
            recommended_house_rules=risk_result['recommended_house_rules']
        )

        self.db.add(match_result)
        self.db.commit()
        self.db.refresh(match_result)

        return match_result

    def run_group_match(
        self,
        candidate_ids: List[str],
        group_size: int,
        match_run_id: str
    ) -> List[models.MatchResult]:
        """Run matching for a group of candidates"""
        profiles = [self._get_profile_dict(cid) for cid in candidate_ids]

        # Get best group combinations
        group_results = self.matching_engine.match_group(profiles, group_size)

        match_results = []
        # Create match results for top groups (limit to top 10)
        for group_result in group_results[:10]:
            # For each group, create pairwise match results
            group_ids = group_result['group']
            for i, res_a_id in enumerate(group_ids):
                for res_b_id in group_ids[i+1:]:
                    # Check if already created
                    existing = self.db.query(models.MatchResult).filter(
                        models.MatchResult.match_run_id == match_run_id,
                        models.MatchResult.resident_a_id == res_a_id,
                        models.MatchResult.resident_b_id == res_b_id
                    ).first()

                    if not existing:
                        match_result = self.run_pairwise_match(res_a_id, res_b_id, match_run_id)
                        match_results.append(match_result)

        return match_results

    def _get_profile_dict(self, resident_id: str) -> Dict:
        """Get resident profile and questionnaire as dict"""
        profile = self.db.query(models.ResidentProfile).filter(
            models.ResidentProfile.id == resident_id
        ).first()

        if not profile or not profile.questionnaire:
            raise ValueError(f"Profile or questionnaire not found for resident {resident_id}")

        q = profile.questionnaire

        return {
            'id': str(resident_id),
            'sleep_schedule_weekday': q.sleep_schedule_weekday,
            'sleep_schedule_weekend': q.sleep_schedule_weekend,
            'light_sensitivity': q.light_sensitivity,
            'noise_tolerance': q.noise_tolerance,
            'quiet_hours_importance': q.quiet_hours_importance,
            'cleanliness_kitchen': q.cleanliness_kitchen,
            'cleanliness_bathroom': q.cleanliness_bathroom,
            'cleanliness_common': q.cleanliness_common,
            'chore_frequency': q.chore_frequency,
            'clutter_tolerance': q.clutter_tolerance,
            'guests_overnight_per_week': q.guests_overnight_per_week,
            'partner_frequency': q.partner_frequency,
            'party_frequency': q.party_frequency,
            'social_level_home': q.social_level_home,
            'introvert_extrovert': q.introvert_extrovert,
            'thermostat_preference': q.thermostat_preference,
            'thermostat_flexibility': q.thermostat_flexibility,
            'wfh_frequency': q.wfh_frequency,
            'shared_space_work_need': q.shared_space_work_need,
            'food_sharing_comfort': q.food_sharing_comfort,
            'toiletries_sharing_comfort': q.toiletries_sharing_comfort,
            'borrowing_comfort': q.borrowing_comfort,
            'has_pets': q.has_pets,
            'pet_types': q.pet_types or [],
            'has_allergies': q.has_allergies,
            'allergy_details': q.allergy_details or [],
            'smoking_tolerance': q.smoking_tolerance,
            'vaping_tolerance': q.vaping_tolerance,
            'drug_tolerance': q.drug_tolerance,
            'alcohol_comfort': q.alcohol_comfort,
            'communication_directness': q.communication_directness,
            'communication_channel': q.communication_channel,
            'response_time_expectation': q.response_time_expectation,
            'conflict_style': q.conflict_style,
            'budget_stress': q.budget_stress,
            'expense_splitting_preference': q.expense_splitting_preference,
            'spirituality_importance': q.spirituality_importance,
            'political_discussion_comfort': q.political_discussion_comfort,
            'sustainability_importance': q.sustainability_importance,
            'dealbreakers': q.dealbreakers or [],
            'flexible_on': q.flexible_on or [],
        }
