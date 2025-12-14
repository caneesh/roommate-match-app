"""
Conflict Prediction Engine v1 - Rule-based risk assessment with category breakdown
"""
from typing import Dict, List, Tuple


class ConflictPredictor:
    """Predicts conflict risk based on profile mismatches"""

    def predict_conflict_risk(
        self,
        profile_a: Dict,
        profile_b: Dict,
        compatibility_scores: Dict
    ) -> Dict:
        """
        Predict conflict risk between two profiles

        Returns:
            {
                'overall_risk': float (0-1),
                'risk_level': str ('low', 'medium', 'high'),
                'category_risks': dict,
                'mitigation_tips': list,
                'recommended_house_rules': list
            }
        """
        # Calculate category-specific risks
        category_risks = {
            'sleep': self._assess_sleep_risk(profile_a, profile_b),
            'cleanliness': self._assess_cleanliness_risk(profile_a, profile_b),
            'guests': self._assess_guests_risk(profile_a, profile_b),
            'temperature': self._assess_temperature_risk(profile_a, profile_b),
            'communication': self._assess_communication_risk(profile_a, profile_b),
            'budget': self._assess_budget_risk(profile_a, profile_b),
        }

        # Calculate weighted overall risk
        # Higher weights for high-conflict dimensions
        weights = {
            'cleanliness': 0.25,
            'guests': 0.20,
            'communication': 0.20,
            'sleep': 0.15,
            'temperature': 0.10,
            'budget': 0.10,
        }

        overall_risk = sum(
            category_risks[cat] * weight
            for cat, weight in weights.items()
        )

        # Determine risk level
        if overall_risk < 0.3:
            risk_level = 'low'
        elif overall_risk < 0.6:
            risk_level = 'medium'
        else:
            risk_level = 'high'

        # Generate mitigation tips
        mitigation_tips = self._generate_mitigation_tips(category_risks, profile_a, profile_b)

        # Generate recommended house rules
        house_rules = self._generate_house_rules(category_risks, profile_a, profile_b)

        return {
            'overall_risk': overall_risk,
            'risk_level': risk_level,
            'category_risks': category_risks,
            'mitigation_tips': mitigation_tips,
            'recommended_house_rules': house_rules
        }

    def _assess_sleep_risk(self, a: Dict, b: Dict) -> float:
        """Assess sleep/noise conflict risk (0-1)"""
        weekday_diff = abs(a['sleep_schedule_weekday'] - b['sleep_schedule_weekday'])
        weekend_diff = abs(a['sleep_schedule_weekend'] - b['sleep_schedule_weekend'])
        noise_diff = abs(a['noise_tolerance'] - b['noise_tolerance'])

        # High risk if one is early bird and other is night owl
        schedule_risk = (weekday_diff + weekend_diff) / 20  # Max = 1.0
        noise_risk = noise_diff / 10  # Max = 1.0

        # WFH + noise mismatch increases risk
        wfh_penalty = 0
        if max(a['wfh_frequency'], b['wfh_frequency']) > 3 and noise_diff > 5:
            wfh_penalty = 0.2

        return min(1.0, (schedule_risk * 0.5 + noise_risk * 0.5) + wfh_penalty)

    def _assess_cleanliness_risk(self, a: Dict, b: Dict) -> float:
        """Assess cleanliness conflict risk (0-1)"""
        kitchen_diff = abs(a['cleanliness_kitchen'] - b['cleanliness_kitchen'])
        bathroom_diff = abs(a['cleanliness_bathroom'] - b['cleanliness_bathroom'])
        common_diff = abs(a['cleanliness_common'] - b['cleanliness_common'])

        # Cleanliness mismatches are major conflict drivers
        kitchen_risk = min(1.0, kitchen_diff / 8)
        bathroom_risk = min(1.0, bathroom_diff / 8)
        common_risk = min(1.0, common_diff / 10)

        # Additional risk if one has very high standards and other is messy
        extreme_mismatch = 0
        if (a['cleanliness_kitchen'] > 8 and b['cleanliness_kitchen'] < 4) or \
           (b['cleanliness_kitchen'] > 8 and a['cleanliness_kitchen'] < 4):
            extreme_mismatch = 0.2

        return min(1.0, (kitchen_risk * 0.4 + bathroom_risk * 0.4 + common_risk * 0.2) + extreme_mismatch)

    def _assess_guests_risk(self, a: Dict, b: Dict) -> float:
        """Assess guest-related conflict risk (0-1)"""
        guests_diff = abs(a['guests_overnight_per_week'] - b['guests_overnight_per_week'])
        partner_diff = abs(a['partner_frequency'] - b['partner_frequency'])
        party_diff = abs(a['party_frequency'] - b['party_frequency'])

        guests_risk = min(1.0, guests_diff / 5)
        partner_risk = min(1.0, partner_diff / 10)
        party_risk = min(1.0, party_diff / 8)

        # Higher risk if one wants privacy and other wants social hub
        social_conflict = abs(a['social_level_home'] - b['social_level_home'])
        if social_conflict > 6:
            return min(1.0, (guests_risk * 0.4 + partner_risk * 0.3 + party_risk * 0.3) + 0.2)

        return guests_risk * 0.4 + partner_risk * 0.3 + party_risk * 0.3

    def _assess_temperature_risk(self, a: Dict, b: Dict) -> float:
        """Assess thermostat conflict risk (0-1)"""
        temp_diff = abs(a['thermostat_preference'] - b['thermostat_preference'])
        avg_flexibility = (a['thermostat_flexibility'] + b['thermostat_flexibility']) / 2

        base_risk = min(1.0, temp_diff / 15)

        # Flexibility reduces risk
        flexibility_reduction = avg_flexibility / 20

        return max(0, base_risk - flexibility_reduction)

    def _assess_communication_risk(self, a: Dict, b: Dict) -> float:
        """Assess communication conflict risk (0-1)"""
        directness_diff = abs(a['communication_directness'] - b['communication_directness'])

        # High risk for avoidant + assertive combination
        style_risk = 0
        if (a['conflict_style'] == 'avoidant' and b['conflict_style'] == 'assertive') or \
           (a['conflict_style'] == 'assertive' and b['conflict_style'] == 'avoidant'):
            style_risk = 0.5
        elif a['conflict_style'] == 'avoidant' and b['conflict_style'] == 'avoidant':
            # Both avoidant can lead to festering issues
            style_risk = 0.3

        directness_risk = min(1.0, directness_diff / 10)

        return min(1.0, directness_risk * 0.4 + style_risk * 0.6)

    def _assess_budget_risk(self, a: Dict, b: Dict) -> float:
        """Assess budget/expense conflict risk (0-1)"""
        budget_stress_diff = abs(a['budget_stress'] - b['budget_stress'])

        # High risk if one is stressed about budget and other is not
        stress_risk = min(1.0, budget_stress_diff / 10)

        # Different expense splitting preferences
        preference_risk = 0
        if a['expense_splitting_preference'] != b['expense_splitting_preference']:
            if 'flexible' not in [a['expense_splitting_preference'], b['expense_splitting_preference']]:
                preference_risk = 0.3

        return min(1.0, stress_risk * 0.6 + preference_risk * 0.4)

    def _generate_mitigation_tips(self, risks: Dict, a: Dict, b: Dict) -> List[str]:
        """Generate conflict mitigation tips based on risks"""
        tips = []

        # Sort risks to prioritize highest ones
        sorted_risks = sorted(risks.items(), key=lambda x: x[1], reverse=True)

        for category, risk in sorted_risks[:4]:
            if risk > 0.5:
                if category == 'cleanliness':
                    tips.append("Create a detailed cleaning schedule with specific responsibilities and standards")
                    tips.append("Discuss expectations for shared spaces upfront - use photos to align on 'clean'")
                elif category == 'guests':
                    tips.append("Set clear boundaries for overnight guests and advance notice expectations")
                    tips.append("Designate 'social' vs 'quiet' hours to balance social and private time")
                elif category == 'communication':
                    tips.append("Establish a regular check-in time to discuss any issues before they escalate")
                    tips.append("Agree on your preferred communication method for household matters")
                elif category == 'sleep':
                    tips.append("Create quiet hours agreement and discuss noise expectations during working hours")
                    tips.append("Consider using white noise machines or room dividers if schedules differ")
                elif category == 'temperature':
                    tips.append("Agree on a baseline temperature and use personal fans/heaters as needed")
                elif category == 'budget':
                    tips.append("Set up a shared expense tracking system and discuss money concerns openly")

        # General tip if overall risk is high
        if max(risks.values()) > 0.6:
            tips.append("Schedule monthly household meetings to address concerns proactively")

        return tips[:5]  # Return top 5 tips

    def _generate_house_rules(self, risks: Dict, a: Dict, b: Dict) -> List[str]:
        """Generate recommended house rules based on risks"""
        rules = []

        if risks['sleep'] > 0.4:
            rules.append("Quiet hours: 10 PM - 8 AM on weekdays")
            rules.append("Use headphones for media after 9 PM")

        if risks['cleanliness'] > 0.4:
            rules.append("Kitchen: Clean dishes within 2 hours, wipe counters after use")
            rules.append("Bathroom: Weekly deep clean rotation")
            rules.append("Common areas: 10-minute tidy before bed")

        if risks['guests'] > 0.4:
            rules.append("Overnight guests: 24-hour advance notice required")
            rules.append("Guest limit: Maximum 2 nights per week")

        if risks['communication'] > 0.4:
            rules.append("Monthly house meeting on the first Sunday")
            rules.append("'5-minute rule': Address minor issues within 5 days before they grow")

        if risks['budget'] > 0.3:
            rules.append("Shared expenses: Split equally and log in shared spreadsheet")
            rules.append("Utilities due by the 5th of each month")

        # Universal rules
        rules.append("Respect each other's private spaces and belongings")
        rules.append("Communicate changes to schedules or plans that affect shared space")

        return rules[:8]  # Return top 8 rules
