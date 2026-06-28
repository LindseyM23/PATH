import { CategoryGroup } from './category.model';

export interface Allocation {
  category_id: string;
  category_name: string;
  group: CategoryGroup;
  icon: string | null;
  allocated_amount: string;
}
