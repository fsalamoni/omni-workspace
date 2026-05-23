import { useEffect } from 'react';
import { ipcBridge } from '@/common';
import { FirebaseStorageService } from '../services/firebase/FirebaseStorageService';
import { auth } from '@/common/firebase';

export function useFirebaseProviders() {
  useEffect(() => {
    // We only want to run this once when the application loads.
    // By calling `.provider()`, we intercept `ipcBridge.x.invoke()` calls LOCALLY
    // instead of sending them to the missing backend WebSocket.

    let isMocking = false;

    // Helper to ensure auth is ready
    const ensureAuth = () => {
      if (!auth.currentUser) throw new Error('[FirebaseProviders] User not authenticated');
    };

    const setupProviders = () => {
      if (isMocking) return;
      isMocking = true;
      console.log('[FirebaseProviders] Intercepting IPC calls for Cloud Native mode');

      // --- Assistants (Rules) ---
      ipcBridge.application.readAssistantRule.provider(async ({ assistantId }) => {
        ensureAuth();
        const data = await FirebaseStorageService.getAssistant(assistantId);
        return data?.rule || '';
      });

      ipcBridge.application.writeAssistantRule.provider(async ({ assistantId, content }) => {
        ensureAuth();
        await FirebaseStorageService.saveAssistant(assistantId, { rule: content });
        return true;
      });

      ipcBridge.application.deleteAssistantRule.provider(async ({ assistantId }) => {
        ensureAuth();
        await FirebaseStorageService.saveAssistant(assistantId, { rule: '' });
        return true;
      });

      // --- Assistants (Skills) ---
      ipcBridge.application.readAssistantSkill.provider(async ({ assistantId }) => {
        ensureAuth();
        const data = await FirebaseStorageService.getAssistant(assistantId);
        return data?.skill || '';
      });

      ipcBridge.application.writeAssistantSkill.provider(async ({ assistantId, content }) => {
        ensureAuth();
        await FirebaseStorageService.saveAssistant(assistantId, { skill: content });
        return true;
      });

      ipcBridge.application.deleteAssistantSkill.provider(async ({ assistantId }) => {
        ensureAuth();
        await FirebaseStorageService.saveAssistant(assistantId, { skill: '' });
        return true;
      });

      // --- Skills Hub ---
      ipcBridge.application.listAvailableSkills.provider(async () => {
        // Here we could fetch cloud-saved skills from Firebase if we had a collection.
        // For now, we return empty or pre-defined, as the user didn't mention custom standalone skills,
        // but if they had them, we should load them from Firebase.
        const settings = await FirebaseStorageService.getSettings();
        return settings.skills || [];
      });
      
      ipcBridge.application.getSkillPaths.provider(async () => {
        return { userSkillsDir: '/cloud/skills', builtinSkillsDir: '/cloud/builtin-skills' };
      });
    };

    setupProviders();
    
    return () => {
      // providers persist naturally, no teardown needed for the mock unless we change mode
    };
  }, []);
}
