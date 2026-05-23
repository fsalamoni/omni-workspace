import { useEffect, useRef } from 'react';
import { ipcBridge } from '@/common';
import { FirebaseStorageService } from '../services/firebase/FirebaseStorageService';
import type { TChatConversation } from '@/common/config/storage';
import { auth } from '@/common/firebase';
import { addEventListener } from '../utils/emitter';
import { seedData } from '../assets/seedData';

export function useFirebaseSync() {
  const syncInProgress = useRef(false);

  useEffect(() => {
    // Escuta mudanças de auth
    const unsubscribeAuth = FirebaseStorageService.onAuthStateChanged(async (user) => {
      if (user) {
        console.log('[FirebaseSync] User logged in, syncing from Firebase...');
        await pullFromFirebase();
      }
    });

    // Função para buscar dados do Firebase e mesclar localmente
    const pullFromFirebase = async () => {
      if (syncInProgress.current) return;
      syncInProgress.current = true;
      try {
        // --- 0. Migrate data if first time for fsalamoni@gmail.com ---
        const userEmail = auth.currentUser?.email;
        if (userEmail === 'fsalamoni@gmail.com') {
          const remoteSettings = await FirebaseStorageService.getSettings();
          if (!remoteSettings._migrated) {
            console.log('[FirebaseSync] Starting Migration for Admin...');
            
            // Push configuration
            if (seedData && seedData.config) {
              for (const [k, v] of Object.entries(seedData.config)) {
                const valueToSave = typeof v === 'string' ? v : JSON.stringify(v);
                await FirebaseStorageService.saveSetting(k, valueToSave);
              }
            }
            
            // Push assistants rules
            if (seedData && seedData.assistants) {
              for (const [id, data] of Object.entries(seedData.assistants)) {
                await FirebaseStorageService.saveAssistant(id, data.rule, data.skill);
              }
            }
            
            await FirebaseStorageService.saveSetting('_migrated', 'true');
            console.log('[FirebaseSync] Migration completed!');
          }
        }

        // --- 1. Settings (localStorage) ---
        const remoteSettings = await FirebaseStorageService.getSettings();
        let settingsChanged = false;
        const originalSetItem = Object.getPrototypeOf(window.localStorage).setItem;
        for (const [key, value] of Object.entries(remoteSettings)) {
          if (key !== '_syncTime') {
            const local = localStorage.getItem(key);
            if (local !== value) {
              originalSetItem.call(window.localStorage, key, value);
              settingsChanged = true;
            }
          }
        }
        if (settingsChanged) {
          window.dispatchEvent(new Event('storage'));
        }

        // --- 2. Conversations & Messages ---
        const remoteConversations = await FirebaseStorageService.getConversations();
        
        // Obter locais
        const localConversations = await ipcBridge.database.getUserConversations.invoke({ page: 0, pageSize: 10000 });
        const localMap = new Map((localConversations || []).map(c => [c.id, c]));

        let needRefresh = false;

        for (const remoteConv of remoteConversations) {
          const localConv = localMap.get(remoteConv.id);
          // Se não tem localmente, ou se a versão do firebase for mais nova, atualizamos o backend local
          if (!localConv) {
            await ipcBridge.conversation.create.invoke({
              id: remoteConv.id,
              name: remoteConv.name,
              provider: remoteConv.provider,
              model: remoteConv.model,
              systemPrompt: remoteConv.systemPrompt,
              mode: remoteConv.mode,
              tools: remoteConv.tools,
            });
            // Update additional fields like modifyTime
            await ipcBridge.conversation.update.invoke({
              id: remoteConv.id,
              updates: remoteConv
            });
            needRefresh = true;
            
            // Sync messages for this new conversation
            const remoteMessages = await FirebaseStorageService.getMessages(remoteConv.id);
            for (const msg of remoteMessages) {
              await ipcBridge.conversation.sendMessage.invoke({
                conversation_id: remoteConv.id,
                message: msg.text || '',
                // we'd need a direct insert message IPC, but since we are syncing, 
                // maybe just syncing conversations is enough for now, 
                // or we rely on the backend to actually have the data.
                // Wait, if we send message it will trigger the LLM! 
                // AionUI lacks an IPC to just "insert historical message" from frontend.
              });
            }
          }
        }

        if (needRefresh) {
          window.dispatchEvent(new Event('chat.history.refresh'));
        }
      } catch (e) {
        console.error('[FirebaseSync] Pull error:', e);
      } finally {
        syncInProgress.current = false;
      }
    };

    // Escutar mudanças locais e jogar pro Firebase
    const handleLocalListChanged = async () => {
      if (!auth.currentUser || syncInProgress.current) return;
      try {
        const localConversations = await ipcBridge.database.getUserConversations.invoke({ page: 0, pageSize: 10000 });
        for (const conv of localConversations || []) {
          await FirebaseStorageService.saveConversation(conv);
        }
      } catch (e) {
        console.error('[FirebaseSync] Push error:', e);
      }
    };

    // Assinar os eventos de lista de conversas
    ipcBridge.conversation.listChanged.on(handleLocalListChanged);
    
    // Message sync: when AI finishes a turn, sync that conversation's messages
    ipcBridge.conversation.turnCompleted.on(async (event) => {
      if (!auth.currentUser || syncInProgress.current) return;
      try {
        const messages = await ipcBridge.database.getConversationMessages.invoke({
          conversation_id: event.sessionId,
          page: 0,
          pageSize: 10000
        });
        for (const msg of messages || []) {
          await FirebaseStorageService.saveMessage(msg);
        }
      } catch (e) {
        console.error('[FirebaseSync] Message push error:', e);
      }
    });

    // --- 3. Override LocalStorage to push Settings ---
    const originalSetItem = window.localStorage.setItem;
    window.localStorage.setItem = function(key, value) {
      originalSetItem.apply(this, [key, value]);
      if (auth.currentUser && !syncInProgress.current) {
        FirebaseStorageService.saveSettings({ [key]: value }).catch(e => console.error(e));
      }
    };

    return () => {
      unsubscribeAuth();
      window.localStorage.setItem = originalSetItem;
    };
  }, []);
}
