import { db, auth } from '@/common/firebase';
import { collection, doc, setDoc, getDoc, getDocs, deleteDoc, query, orderBy } from 'firebase/firestore';
import type { TChatConversation } from '@/common/config/storage';
import type { TMessage } from '@/common/chat/chatLib';

export class FirebaseStorageService {
  private static get uid() {
    return auth.currentUser?.uid;
  }

  /**
   * Base path: SalomoneUI/{uid}/...
   */
  private static getBasePath() {
    const uid = this.uid;
    if (!uid) return null;
    return `SalomoneUI/${uid}`;
  }

  // --- Conversations ---

  static async saveConversation(conversation: TChatConversation): Promise<void> {
    const basePath = this.getBasePath();
    if (!basePath) return;

    try {
      const docRef = doc(db, `${basePath}/conversations`, conversation.id);
      await setDoc(docRef, {
        ...conversation,
        _syncTime: Date.now()
      }, { merge: true });
    } catch (error) {
      console.error('[Firebase] Failed to save conversation:', error);
    }
  }

  static async getConversations(): Promise<TChatConversation[]> {
    const basePath = this.getBasePath();
    if (!basePath) return [];

    try {
      const q = query(collection(db, `${basePath}/conversations`), orderBy('createTime', 'desc'));
      const snapshot = await getDocs(q);
      return snapshot.docs.map(doc => doc.data() as TChatConversation);
    } catch (error) {
      console.error('[Firebase] Failed to get conversations:', error);
      return [];
    }
  }

  static async deleteConversation(conversationId: string): Promise<void> {
    const basePath = this.getBasePath();
    if (!basePath) return;

    try {
      await deleteDoc(doc(db, `${basePath}/conversations`, conversationId));
      // Optionally delete all messages in this conversation
      // We would need to query and delete or use a Cloud Function
    } catch (error) {
      console.error('[Firebase] Failed to delete conversation:', error);
    }
  }

  // --- Messages ---

  static async saveMessage(message: TMessage): Promise<void> {
    const basePath = this.getBasePath();
    if (!basePath || !message.conversation_id) return;

    try {
      const docRef = doc(db, `${basePath}/chats/${message.conversation_id}/messages`, message.id);
      // Remove any non-serializable fields if necessary, but TMessage should be plain object
      await setDoc(docRef, {
        ...message,
        _syncTime: Date.now()
      }, { merge: true });
    } catch (error) {
      console.error('[Firebase] Failed to save message:', error);
    }
  }

  static async getMessages(conversationId: string): Promise<TMessage[]> {
    const basePath = this.getBasePath();
    if (!basePath) return [];

    try {
      const q = query(collection(db, `${basePath}/chats/${conversationId}/messages`), orderBy('create_time', 'asc'));
      const snapshot = await getDocs(q);
      return snapshot.docs.map(doc => doc.data() as TMessage);
    } catch (error) {
      console.error('[Firebase] Failed to get messages:', error);
      return [];
    }
  }

  // --- Settings (Global configs, localStorage) ---

  static async saveSettings(settingsPatch: Record<string, any>): Promise<void> {
    const basePath = this.getBasePath();
    if (!basePath) return;

    try {
      const docRef = doc(db, `${basePath}/settings`, 'global');
      await setDoc(docRef, {
        ...settingsPatch,
        _syncTime: Date.now()
      }, { merge: true });
    } catch (error) {
      console.error('[Firebase] Failed to save settings:', error);
    }
  }

  static async getSettings(): Promise<Record<string, any>> {
    const basePath = this.getBasePath();
    if (!basePath) return {};

    try {
      const docRef = doc(db, `${basePath}/settings`, 'global');
      const docSnap = await getDoc(docRef);
      if (docSnap.exists()) {
        return docSnap.data();
      }
      return {};
    } catch (error) {
      console.error('[Firebase] Failed to get settings:', error);
      return {};
    }
  }

  // --- Assistants ---

  static async saveAssistant(assistantId: string, data: Record<string, any>): Promise<void> {
    const basePath = this.getBasePath();
    if (!basePath) return;

    try {
      const docRef = doc(db, `${basePath}/assistants`, assistantId);
      await setDoc(docRef, {
        ...data,
        _syncTime: Date.now()
      }, { merge: true });
    } catch (error) {
      console.error('[Firebase] Failed to save assistant:', error);
    }
  }

  static async getAssistant(assistantId: string): Promise<Record<string, any> | null> {
    const basePath = this.getBasePath();
    if (!basePath) return null;

    try {
      const docRef = doc(db, `${basePath}/assistants`, assistantId);
      const docSnap = await getDoc(docRef);
      if (docSnap.exists()) {
        return docSnap.data();
      }
      return null;
    } catch (error) {
      console.error('[Firebase] Failed to get assistant:', error);
      return null;
    }
  }

  static async getAllAssistants(): Promise<Record<string, any>[]> {
    const basePath = this.getBasePath();
    if (!basePath) return [];

    try {
      const q = query(collection(db, `${basePath}/assistants`));
      const snapshot = await getDocs(q);
      return snapshot.docs.map(doc => doc.data());
    } catch (error) {
      console.error('[Firebase] Failed to get all assistants:', error);
      return [];
    }
  }

  static async deleteAssistant(assistantId: string): Promise<void> {
    const basePath = this.getBasePath();
    if (!basePath) return;

    try {
      await deleteDoc(doc(db, `${basePath}/assistants`, assistantId));
    } catch (error) {
      console.error('[Firebase] Failed to delete assistant:', error);
    }
  }

  // --- Sync Listeners ---
  
  /**
   * Utility to observe auth state changes and trigger a full sync
   * or load from Firebase if local is empty.
   */
  static onAuthStateChanged(callback: (user: any) => void) {
    return auth.onAuthStateChanged(callback);
  }
}
