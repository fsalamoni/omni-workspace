import { useEffect } from 'react';
import { ipcBridge } from '@/common';
import { FirebaseStorageService } from '../services/firebase/FirebaseStorageService';
import { auth } from '@/common/firebase';
import { BUILTIN_SKILLS, BUILTIN_ASSISTANTS } from './builtinData';

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

      // --- Built-in Data Mocks ---
      ipcBridge.extensions.getAssistants.provider(async () => {
        try {
          const { ASSISTANT_PRESETS } = await import('@/common/config/presets/assistantPresets');
          return ASSISTANT_PRESETS.map((preset) => {
            const enabledByDefault =
              preset.id === 'word-creator' ||
              preset.id === 'ppt-creator' ||
              preset.id === 'excel-creator' ||
              preset.id === 'academic-paper' ||
              preset.id === 'morph-ppt' ||
              preset.id === 'cowork' ||
              preset.id === 'openclaw-setup' ||
              preset.id === 'star-office-helper' ||
              preset.id === 'story-roleplay' ||
              preset.id === 'moltbook' ||
              preset.id === 'beautiful-mermaid';
            
            return {
              id: `builtin-${preset.id}`,
              name: preset.nameI18n['en-US'],
              nameI18n: preset.nameI18n,
              description: preset.descriptionI18n['en-US'] || '',
              descriptionI18n: preset.descriptionI18n,
              avatar: preset.avatar,
              isPreset: true,
              enabled: enabledByDefault,
              enabledSkills: preset.defaultEnabledSkills || [],
              enabledExtensions: []
            };
          });
        } catch (e) {
          console.error('Failed to load ASSISTANT_PRESETS', e);
          return [];
        }
      });

      ipcBridge.fs.listBuiltinAutoSkills.provider(async () => {
        return BUILTIN_SKILLS;
      });

      ipcBridge.fs.enableSkillsMarket.provider(async () => {
        return { success: true, msg: 'Skills Market enabled in Cloud Mode' };
      });

      ipcBridge.fs.disableSkillsMarket.provider(async () => {
        return { success: true, msg: 'Skills Market disabled in Cloud Mode' };
      });

      ipcBridge.fs.readBuiltinRule.provider(async ({ fileName }) => {
        try {
          const rulesMap = (await import('@/renderer/assets/rulesMap.json')).default;
          // Clean the filename by removing .md extension if present to match the map keys
          const cleanName = fileName.replace('.md', '');
          // Or we can just try both clean and exact
          if (rulesMap[fileName]) return rulesMap[fileName];
          if (rulesMap[`${cleanName}.md`]) return rulesMap[`${cleanName}.md`];
          return '';
        } catch (e) {
          console.error('[Mock] Failed to load rulesMap.json:', e);
          return '';
        }
      });

      ipcBridge.fs.readBuiltinSkill.provider(async ({ fileName }) => {
        try {
          const skillsMap = (await import('@/renderer/assets/skillsMap.json')).default;
          // Clean the filename by removing .md extension if present to match the map keys
          const cleanName = fileName.replace('.md', '');
          if (skillsMap[cleanName]) {
            return skillsMap[cleanName];
          }
          if (fileName === 'aionui-skills' || fileName === 'salomoneui-skills') {
            return `---\nname: aionui-skills\ndescription: "Access the AionUI Skills registry — discover and download AI agent skills."\n---\n\n# AionUI Skills Registry\n\nFetch full instructions:\n\n\`\`\`bash\nmkdir -p ~/.config/aionui-skills\ncurl -s https://skills.aionui.com/SKILL.md > ~/.config/aionui-skills/SKILL.md\n\`\`\`\n\nThen read and follow the instructions in that file.\n`;
          }
          return '';
        } catch (e) {
          console.error('[Mock] Failed to load skillsMap.json:', e);
          return '';
        }
      });

      // --- Assistants (Rules) ---
      ipcBridge.fs.readAssistantRule.provider(async ({ assistantId }) => {
        ensureAuth();
        const data = await FirebaseStorageService.getAssistant(assistantId);
        return data?.rule || '';
      });

      ipcBridge.fs.writeAssistantRule.provider(async ({ assistantId, content }) => {
        ensureAuth();
        await FirebaseStorageService.saveAssistant(assistantId, { rule: content });
        return true;
      });

      ipcBridge.fs.deleteAssistantRule.provider(async ({ assistantId }) => {
        ensureAuth();
        await FirebaseStorageService.saveAssistant(assistantId, { rule: '' });
        return true;
      });

      // --- Assistants (Skills) ---
      ipcBridge.fs.readAssistantSkill.provider(async ({ assistantId }) => {
        ensureAuth();
        const data = await FirebaseStorageService.getAssistant(assistantId);
        return data?.skill || '';
      });

      ipcBridge.fs.writeAssistantSkill.provider(async ({ assistantId, content }) => {
        ensureAuth();
        await FirebaseStorageService.saveAssistant(assistantId, { skill: content });
        return true;
      });

      ipcBridge.fs.deleteAssistantSkill.provider(async ({ assistantId }) => {
        ensureAuth();
        await FirebaseStorageService.saveAssistant(assistantId, { skill: '' });
        return true;
      });

      ipcBridge.fs.listAvailableSkills.provider(async () => {
        const settings = await FirebaseStorageService.getSettings();
        const customSkills = settings.skills || [];
        
        try {
          const ConfigStorage = (await import('@/common/config/storage')).ConfigStorage;
          const isMarketEnabled = await ConfigStorage.get('skillsMarket.enabled');
          if (isMarketEnabled) {
            customSkills.push({
              name: 'aionui-skills',
              description: 'Access the AionUI Skills registry — discover and download AI agent skills.',
              location: 'builtin',
              isCustom: false,
              source: 'builtin'
            });
          }
        } catch (e) {
          console.warn('[FirebaseProviders] Failed to read skillsMarket.enabled', e);
        }
        
        return customSkills;
      });
      
      ipcBridge.fs.getSkillPaths.provider(async () => {
        return { userSkillsDir: '/cloud/skills', builtinSkillsDir: '/cloud/builtin-skills' };
      });
    };

    setupProviders();
    
    return () => {
      // providers persist naturally, no teardown needed for the mock unless we change mode
    };
  }, []);
}
