'use client';

import { useEffect } from 'react';

/**
 * HydrationFix - Fixes hydration mismatches caused by browser extensions
 * 
 * This component handles the common issue where browser extensions (like Grammarly)
 * add attributes to the DOM that don't exist during server-side rendering,
 * causing React hydration errors.
 */
export default function HydrationFix() {
  useEffect(() => {
    // Remove extension-added attributes that cause hydration mismatches
    const body = document.body;
    
    if (body) {
      // Remove Grammarly attributes
      body.removeAttribute('data-new-gr-c-s-check-loaded');
      body.removeAttribute('data-gr-ext-installed');
      
      // Remove other common extension attributes
      body.removeAttribute('data-grammarly-shadow-root');
      body.removeAttribute('data-grammarly');
      
      // Remove any other extension attributes that might cause issues
      const attributesToRemove = Array.from(body.attributes)
        .filter(attr => 
          attr.name.startsWith('data-grammarly') ||
          attr.name.startsWith('data-new-gr') ||
          attr.name.startsWith('data-gr-ext')
        )
        .map(attr => attr.name);
      
      attributesToRemove.forEach(attr => {
        body.removeAttribute(attr);
      });
    }
  }, []);

  // This component doesn't render anything
  return null;
}
