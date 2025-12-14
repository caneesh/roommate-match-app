import { z } from 'zod';

export const questionnaireSchema = z.object({
  sleepScheduleWeekday: z.number().min(0).max(10),
  sleepScheduleWeekend: z.number().min(0).max(10),
  lightSensitivity: z.number().min(0).max(10),
  noiseTolerance: z.number().min(0).max(10),
  quietHoursImportance: z.number().min(0).max(10),

  cleanlinessKitchen: z.number().min(0).max(10),
  cleanlinessBathroom: z.number().min(0).max(10),
  cleanlinessCommon: z.number().min(0).max(10),
  choreFrequency: z.number().min(0).max(7),
  clutterTolerance: z.number().min(0).max(10),

  guestsOvernightPerWeek: z.number().min(0).max(7),
  partnerFrequency: z.number().min(0).max(10),
  partyFrequency: z.number().min(0).max(10),
  socialLevelHome: z.number().min(0).max(10),
  introvertExtrovert: z.number().min(0).max(10),

  thermostatPreference: z.number().min(60).max(80),
  thermostatFlexibility: z.number().min(0).max(10),
  wfhFrequency: z.number().min(0).max(7),
  sharedSpaceWorkNeed: z.number().min(0).max(10),

  foodSharingComfort: z.number().min(0).max(10),
  toiletriesSharingComfort: z.number().min(0).max(10),
  borrowingComfort: z.number().min(0).max(10),

  hasPets: z.boolean(),
  petTypes: z.array(z.string()).optional(),
  hasAllergies: z.boolean(),
  allergyDetails: z.array(z.string()).optional(),
  smokingTolerance: z.number().min(0).max(10),
  vapingTolerance: z.number().min(0).max(10),
  drugTolerance: z.number().min(0).max(10),
  alcoholComfort: z.number().min(0).max(10),

  communicationDirectness: z.number().min(0).max(10),
  communicationChannel: z.enum(['text', 'call', 'in_person', 'any']),
  responseTimeExpectation: z.number().min(0).max(72),
  conflictStyle: z.enum(['collaborative', 'avoidant', 'assertive', 'compromising']),

  budgetStress: z.number().min(0).max(10),
  expenseSplittingPreference: z.enum(['equal', 'by_usage', 'flexible']),

  spiritualityImportance: z.number().min(0).max(10),
  politicalDiscussionComfort: z.number().min(0).max(10),
  sustainabilityImportance: z.number().min(0).max(10),

  dealbreakers: z.array(z.string()),
  flexibleOn: z.array(z.string()),
  petPeeves: z.string().optional(),
  idealRoommateDescription: z.string().optional(),
});

export const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});

export const signupSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
  name: z.string().min(1),
  role: z.enum(['resident', 'operator']),
});

export const propertySchema = z.object({
  name: z.string().min(1),
  address: z.string().min(1),
  city: z.string().min(1),
  state: z.string().length(2),
  zipCode: z.string().min(5),
});

export const unitSchema = z.object({
  propertyId: z.string().uuid(),
  unitNumber: z.string().min(1),
});

export const roomSchema = z.object({
  unitId: z.string().uuid(),
  roomNumber: z.string().min(1),
  totalBeds: z.number().min(1).max(6),
});
