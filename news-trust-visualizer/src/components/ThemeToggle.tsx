
import React from 'react';
import { useTheme } from '@/context/ThemeContext';
import { Moon, Sun } from 'lucide-react';
import { Toggle } from '@/components/ui/toggle';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

export const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Toggle
          aria-label="Toggle theme"
          onClick={toggleTheme}
          className="bg-transparent hover:bg-muted"
        >
          {theme === 'light' ? (
            <Moon className="h-4 w-4" />
          ) : (
            <Sun className="h-4 w-4" />
          )}
        </Toggle>
      </TooltipTrigger>
      <TooltipContent>
        <p>Toggle {theme === 'light' ? 'dark' : 'light'} mode</p>
      </TooltipContent>
    </Tooltip>
  );
};
