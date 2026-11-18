import { useCallback, useState } from "react";

type Theme = "dark" | "light";

const STORAGE_KEY = "kafka-lab-theme";
const DARK_CLASS = "dark";
const SWITCHING_CLASS = "theme-switching";
const SWITCH_DURATION_MS = 250;

function currentTheme(): Theme {
  return document.documentElement.classList.contains(DARK_CLASS) ? "dark" : "light";
}

function persist(theme: Theme): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    return;
  }
}

export function useTheme(): [Theme, () => void] {
  const [theme, setTheme] = useState<Theme>(currentTheme);

  const toggle = useCallback(() => {
    const next: Theme = currentTheme() === "dark" ? "light" : "dark";
    const root = document.documentElement;
    root.classList.add(SWITCHING_CLASS);
    root.classList.toggle(DARK_CLASS, next === "dark");
    window.setTimeout(() => root.classList.remove(SWITCHING_CLASS), SWITCH_DURATION_MS);
    persist(next);
    setTheme(next);
  }, []);

  return [theme, toggle];
}
