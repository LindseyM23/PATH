export type CategoryGroup = 'essentials' | 'personal_care' | 'career' | 'lifestyle' | 'wealth' | 'misc';

export const CATEGORY_GROUP_LABELS: Record<CategoryGroup, string> = {
  essentials: 'Essentials',
  personal_care: 'Personal Care',
  career: 'Career',
  lifestyle: 'Lifestyle',
  wealth: 'Wealth',
  misc: 'Other',
};

export interface Category {
  id: string;
  name: string;
  group: CategoryGroup;
  icon: string | null;
  is_default: boolean;
  sort_order: number;
}
