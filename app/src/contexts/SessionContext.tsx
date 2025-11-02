import React, { createContext, useContext, useState, ReactNode } from 'react';

interface SessionContextType {
  isAuthed: boolean;
  signIn: () => void;
  signOut: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [isAuthed, setIsAuthed] = useState(false);

  const signIn = () => setIsAuthed(true);
  const signOut = () => setIsAuthed(false);

  return (
    <SessionContext.Provider value={{ isAuthed, signIn, signOut }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within SessionProvider');
  }
  return context;
}
