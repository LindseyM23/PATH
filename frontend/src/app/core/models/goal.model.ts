export interface Goal {
  id: string;
  name: string;
  target_amount: string;
  current_amount: string;
  icon: string | null;
  progress_percent: string;
}
