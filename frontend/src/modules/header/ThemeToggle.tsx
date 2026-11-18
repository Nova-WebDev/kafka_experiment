import { faMoon, faSun } from "@fortawesome/free-solid-svg-icons";
import { IconButton } from "../../base/IconButton";
import { useTheme } from "../../share/theme";

export function ThemeToggle() {
  const [theme, toggle] = useTheme();
  const nextTheme = theme === "dark" ? "light" : "dark";

  return (
    <IconButton
      icon={theme === "dark" ? faSun : faMoon}
      label={`Switch to ${nextTheme} theme`}
      onClick={toggle}
    />
  );
}
