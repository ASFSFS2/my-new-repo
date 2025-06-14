// Simple authentication without email verification
import { createClient } from '@/lib/supabase/client';

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  success: boolean;
  user?: User;
  error?: string;
}

class SimpleAuth {
  private supabase = createClient();

  async signUp(email: string, password: string): Promise<AuthResponse> {
    try {
      // First, try to sign up the user
      const { data: signUpData, error: signUpError } = await this.supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            email_confirm: true,
          }
        }
      });

      if (signUpError) {
        return { success: false, error: signUpError.message };
      }

      // Immediately sign in the user (bypassing email confirmation)
      const { data: signInData, error: signInError } = await this.supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (signInError) {
        return { success: false, error: signInError.message };
      }

      if (signInData.user) {
        return {
          success: true,
          user: {
            id: signInData.user.id,
            email: signInData.user.email!,
            created_at: signInData.user.created_at,
          }
        };
      }

      return { success: false, error: 'Unknown error occurred' };
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  }

  async signIn(email: string, password: string): Promise<AuthResponse> {
    try {
      const { data, error } = await this.supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        return { success: false, error: error.message };
      }

      if (data.user) {
        return {
          success: true,
          user: {
            id: data.user.id,
            email: data.user.email!,
            created_at: data.user.created_at,
          }
        };
      }

      return { success: false, error: 'Unknown error occurred' };
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  }

  async signOut(): Promise<{ success: boolean; error?: string }> {
    try {
      const { error } = await this.supabase.auth.signOut();
      if (error) {
        return { success: false, error: error.message };
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const { data: { user } } = await this.supabase.auth.getUser();
      if (user) {
        return {
          id: user.id,
          email: user.email!,
          created_at: user.created_at,
        };
      }
      return null;
    } catch (error) {
      return null;
    }
  }

  // Guest access - creates a temporary session
  async signInAsGuest(): Promise<AuthResponse> {
    const guestEmail = `guest_${Date.now()}@neo.local`;
    const guestPassword = `guest_${Math.random().toString(36).substring(7)}`;
    
    return this.signUp(guestEmail, guestPassword);
  }
}

export const simpleAuth = new SimpleAuth();