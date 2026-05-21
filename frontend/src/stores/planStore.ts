/* ─────────────────────────────────────────────
   OmniWorkspace — Plan Store (Zustand)
   ───────────────────────────────────────────── */

import { create } from 'zustand';
import type { Plan, PlanStepStatus } from '@/types';

interface PlanState {
  activePlan: Plan | null;
  setPlan: (plan: Plan) => void;
  updateStepStatus: (stepId: string, status: PlanStepStatus, result?: string) => void;
  clearPlan: () => void;
}

export const usePlanStore = create<PlanState>((set) => ({
  activePlan: null,

  setPlan: (plan) => set({ activePlan: plan }),

  updateStepStatus: (stepId, status, result) =>
    set((s) => {
      if (!s.activePlan) return s;
      return {
        activePlan: {
          ...s.activePlan,
          steps: s.activePlan.steps.map((step) =>
            step.id === stepId ? { ...step, status, result: result ?? step.result } : step,
          ),
        },
      };
    }),

  clearPlan: () => set({ activePlan: null }),
}));
