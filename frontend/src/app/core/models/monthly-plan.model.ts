export interface MonthlyPlan {
  id: string;
  year: number;
  month: number;
  salary_amount: string;
  currency: string;
  allocated_total: string;
  remaining_amount: string;
  savings_total: string;
  on_track: boolean;
}
