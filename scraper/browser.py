import os
import platform
import subprocess
import winreg  # для Windows
import plistlib  # для macOS
from typing import Optional, List


class Browser:
    @staticmethod
    def get_default_browser() -> Optional[str]:
        """Определяет браузер по умолчанию"""
        system = platform.system()

        if system == "Windows":
            return Browser._get_windows_default_browser()
        elif system == "Darwin":  # macOS
            return Browser._get_macos_default_browser()
        elif system == "Linux":
            return Browser._get_linux_default_browser()
        else:
            return None

    @staticmethod
    def _get_windows_default_browser() -> Optional[str]:
        """Определяет браузер по умолчанию в Windows"""
        try:
            # Способ 1: Через реестр
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice") as key:
                prog_id = winreg.QueryValueEx(key, "ProgId")[0]

            browser_map = {
                'ChromeHTML': 'chrome',
                'FirefoxURL': 'firefox',
                'MSEdgeHTM': 'edge',
                'IE.HTTP': 'ie',
                'OperaStable': 'opera',
                'BraveHTML': 'brave'
            }

            return browser_map.get(prog_id, None)

        except Exception:
            try:
                # Способ 2: Через команду
                result = subprocess.run([
                    'reg', 'query',
                    'HKEY_CURRENT_USER\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice',
                    '/v', 'ProgId'
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'ProgId' in line:
                            prog_id = line.split('REG_SZ')[-1].strip()
                            browser_map = {
                                'ChromeHTML': 'chrome',
                                'FirefoxURL': 'firefox',
                                'MSEdgeHTM': 'edge',
                                'IE.HTTP': 'ie'
                            }
                            return browser_map.get(prog_id, None)
            except Exception:
                pass

        return None

    @staticmethod
    def _get_macos_default_browser() -> Optional[str]:
        """Определяет браузер по умолчанию в macOS"""
        try:
            # Через defaults command
            result = subprocess.run([
                'defaults', 'read',
                'com.apple.LaunchServices/com.apple.launchservices.secure',
                'LSHandlers'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'LSHandlerRoleAll = "-";' in line and i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line.startswith('LSHandlerURLScheme = http;'):
                            browser_id = lines[i - 1].strip().strip('"')
                            browser_map = {
                                'com.google.chrome': 'chrome',
                                'org.mozilla.firefox': 'firefox',
                                'com.microsoft.edgemac': 'edge',
                                'com.apple.safari': 'safari',
                                'com.operasoftware.Opera': 'opera',
                                'com.brave.browser': 'brave'
                            }
                            return browser_map.get(browser_id, None)
        except Exception:
            pass

        return None

    @staticmethod
    def _get_linux_default_browser() -> Optional[str]:
        """Определяет браузер по умолчанию в Linux"""
        try:
            # Способ 1: Через xdg-settings
            result = subprocess.run(['xdg-settings', 'get', 'default-web-browser'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                browser = result.stdout.strip()
                browser_map = {
                    'google-chrome.desktop': 'chrome',
                    'firefox.desktop': 'firefox',
                    'microsoft-edge.desktop': 'edge',
                    'opera.desktop': 'opera',
                    'brave-browser.desktop': 'brave'
                }
                return browser_map.get(browser, None)

            # Способ 2: Через mimeapps
            mimeapps_path = os.path.expanduser('~/.config/mimeapps.list')
            if os.path.exists(mimeapps_path):
                with open(mimeapps_path, 'r') as f:
                    content = f.read()
                    if 'x-scheme-handler/http=' in content:
                        lines = content.split('\n')
                        for line in lines:
                            if line.startswith('x-scheme-handler/http='):
                                browser = line.split('=')[1].strip()
                                browser_map = {
                                    'google-chrome.desktop': 'chrome',
                                    'firefox.desktop': 'firefox',
                                    'microsoft-edge.desktop': 'edge'
                                }
                                return browser_map.get(browser, None)

        except Exception:
            pass

        return None

    @staticmethod
    def get_available_browsers() -> List[str]:
        """Возвращает список доступных браузеров в системе"""
        available = []

        # Проверяем Chrome
        if Browser._is_browser_available('chrome'):
            available.append('chrome')

        # Проверяем Firefox
        if Browser._is_browser_available('firefox'):
            available.append('firefox')

        # Проверяем Edge
        if Browser._is_browser_available('edge'):
            available.append('edge')

        # Проверяем Safari (только macOS)
        if platform.system() == "Darwin" and Browser._is_browser_available('safari'):
            available.append('safari')

        return available

    @staticmethod
    def _is_browser_available(browser: str) -> bool:
        """Проверяет, установлен ли браузер"""
        try:
            if browser == 'chrome':
                if platform.system() == "Windows":
                    return os.path.exists(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
                elif platform.system() == "Darwin":
                    return os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
                else:
                    return subprocess.run(['which', 'google-chrome'],
                                          capture_output=True).returncode == 0

            elif browser == 'firefox':
                if platform.system() == "Windows":
                    return os.path.exists(r"C:\Program Files\Mozilla Firefox\firefox.exe")
                elif platform.system() == "Darwin":
                    return os.path.exists("/Applications/Firefox.app/Contents/MacOS/firefox")
                else:
                    return subprocess.run(['which', 'firefox'],
                                          capture_output=True).returncode == 0

            elif browser == 'edge':
                if platform.system() == "Windows":
                    return os.path.exists(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
                elif platform.system() == "Darwin":
                    return os.path.exists("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
                else:
                    return subprocess.run(['which', 'microsoft-edge'],
                                          capture_output=True).returncode == 0

            elif browser == 'safari':
                return platform.system() == "Darwin" and os.path.exists("/Applications/Safari.app")

        except Exception:
            return False

        return False
