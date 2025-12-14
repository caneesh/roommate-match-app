export type UserRole = 'resident' | 'operator' | 'admin';

export type RiskLevel = 'low' | 'medium' | 'high';

export type CommunicationStyle = 'direct' | 'indirect' | 'mixed';
export type ConflictStyle = 'collaborative' | 'avoidant' | 'assertive' | 'compromising';
export type ChannelPreference = 'text' | 'call' | 'in_person' | 'any';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  createdAt: Date;
}

export interface QuestionnaireAnswers {
  // Sleep & Noise (0-10 scales)
  sleepScheduleWeekday: number; // 0=early bird, 10=night owl
  sleepScheduleWeekend: number;
  lightSensitivity: number; // 0=none, 10=very sensitive
  noiseTolerance: number; // 0=very quiet, 10=tolerates loud
  quietHoursImportance: number; // 0=not important, 10=very important

  // Cleanliness (0-10 scales)
  cleanlinessKitchen: number; // 0=very messy, 10=spotless
  cleanlinessBathroom: number;
  cleanlinessCommon: number;
  choreFrequency: number; // times per week
  clutterTolerance: number; // 0=minimalist, 10=ok with clutter

  // Guests & Social (0-10 scales)
  guestsOvernightPerWeek: number; // 0-7
  partnerFrequency: number; // 0=never, 10=always
  partyFrequency: number; // 0=never, 10=weekly
  socialLevelHome: number; // 0=private sanctuary, 10=social hub
  introvertExtrovert: number; // 0=introvert, 10=extrovert

  // Environment
  thermostatPreference: number; // degrees F (60-80)
  thermostatFlexibility: number; // 0=rigid, 10=very flexible
  wfhFrequency: number; // days per week (0-7)
  sharedSpaceWorkNeed: number; // 0=never, 10=always

  // Sharing & Boundaries
  foodSharingComfort: number; // 0=never, 10=always
  toiletriesSharingComfort: number;
  borrowingComfort: number;

  // Substances & Lifestyle
  hasPets: boolean;
  petTypes?: string[];
  hasAllergies: boolean;
  allergyDetails?: string[];
  smokingTolerance: number; // 0=none, 10=ok
  vapingTolerance: number;
  drugTolerance: number;
  alcoholComfort: number; // 0=none, 10=ok

  // Communication
  communicationDirectness: number; // 0=very indirect, 10=very direct
  communicationChannel: ChannelPreference;
  responseTimeExpectation: number; // hours (0-72)
  conflictStyle: ConflictStyle;

  // Budget & Expenses
  budgetStress: number; // 0=none, 10=very stressed
  expenseSplittingPreference: string; // 'equal' | 'by_usage' | 'flexible'

  // Values & Priorities
  spiritualityImportance: number; // 0-10
  politicalDiscussionComfort: number; // 0-10
  sustainabilityImportance: number; // 0-10

  // Open text
  dealbreakers: string[];
  flexibleOn: string[];
  petPeeves?: string;
  idealRoommateDescription?: string;
}

export interface MatchResult {
  id: string;
  residentAId: string;
  residentBId: string;
  compatibilityScore: number; // 0-100
  riskScore: number; // 0-1
  riskLevel: RiskLevel;
  categoryScores: CategoryScores;
  categoryRisks: CategoryRisks;
  topAlignments: string[];
  topMismatches: string[];
  mitigationTips: string[];
  recommendedHouseRules: string[];
  createdAt: Date;
}

export interface CategoryScores {
  sleep: number;
  cleanliness: number;
  guests: number;
  temperature: number;
  communication: number;
  sharing: number;
  lifestyle: number;
  overall: number;
}

export interface CategoryRisks {
  sleep: number;
  cleanliness: number;
  guests: number;
  temperature: number;
  communication: number;
  budget: number;
  overall: number;
}

export interface Property {
  id: string;
  operatorOrgId: string;
  name: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  totalUnits: number;
  createdAt: Date;
}

export interface Unit {
  id: string;
  propertyId: string;
  unitNumber: string;
  totalRooms: number;
  totalBeds: number;
}

export interface Room {
  id: string;
  unitId: string;
  roomNumber: string;
  totalBeds: number;
}

export interface Bed {
  id: string;
  roomId: string;
  bedNumber: string;
  isOccupied: boolean;
  currentResidentId?: string;
}

export interface MatchRun {
  id: string;
  operatorOrgId: string;
  propertyId: string;
  bedId?: string;
  candidateIds: string[];
  groupSize: number;
  status: 'pending' | 'completed' | 'failed';
  createdBy: string;
  createdAt: Date;
  completedAt?: Date;
}

export interface Event {
  id: string;
  eventName: string;
  userId?: string;
  operatorOrgId?: string;
  properties?: Record<string, any>;
  createdAt: Date;
}
