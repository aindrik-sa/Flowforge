export interface ProjectDashboardStats {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  completion_percentage: number;
}

export interface UserProductivityStats {
  completed_last_30_days: number;
  current_pending_tasks: number;
}
