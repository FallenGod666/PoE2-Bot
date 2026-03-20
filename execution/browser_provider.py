import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineProfile, QWebEngineScript, QWebEnginePage
from PySide6.QtCore import QUrl, Qt, QTimer
import win32gui
import win32con

class AdBlocker(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        ad_patterns = [
            "googleads", "doubleclick", "adnxs", "advertising", 
            "amazon-adsystem", "taboola", "outbrain", "adservice",
            "pubads", "g.doubleclick.net", "pagead", "googlesyndication",
            "ign.com", "assets.ign.com", "zencoder", "video-guide", "playwire",
            "vtrack", "prebid", "omgid", "moatads"
        ]
        if any(pattern in url for pattern in ad_patterns):
            # print(f"DEBUG BLOCKED: {url}")
            info.block(True)

def inject_adblock_js(profile):
    # JavaScript definitivo para ELIMINAR elementos e silenciar erros
    js_code = """
    (function() {
        const noop = () => Promise.resolve();
        const dummyMethods = {
            play: noop, load: noop, pause: noop, 
            canPlayType: () => '', addTextTrack: () => {},
            setAttribute: () => {}, removeAttribute: () => {},
            style: {}, dataset: {}
        };

        // Anti-criação de vídeos e iframes chatos
        const originalCreate = document.createElement;
        document.createElement = function(tag) {
            const t = tag.toLowerCase();
            if (t === 'video' || t === 'iframe' || t === 'object' || t === 'embed') {
                const dummy = originalCreate.call(document, 'div');
                Object.assign(dummy, dummyMethods);
                dummy.style.display = 'none';
                dummy.style.width = '0.1px';
                dummy.style.height = '0.1px';
                return dummy;
            }
            return originalCreate.apply(document, arguments);
        };
        
        // CSS para garantir sumiço
        const style = document.createElement('style');
        style.innerHTML = `
            video, iframe, [src*="ign.com"], .ign-video-player, .video-player { 
                width: 0.1px !important; 
                height: 0.1px !important; 
                display: none !important; 
                opacity: 0 !important;
                pointer-events: none !important;
            }
        `;
        (document.head || document.documentElement).appendChild(style);

        // Limpeza periódica
        const clean = () => {
            document.querySelectorAll('video, iframe[src*="ign.com"]').forEach(el => {
                if(el.tagName === 'VIDEO') el.pause();
                el.style.display = 'none';
            });
        };
        setInterval(clean, 2000);
        
        // Patch global
        if (window.HTMLMediaElement) {
            Object.assign(HTMLMediaElement.prototype, { play: noop, load: noop, pause: noop });
        }
    })();
    """
    script = QWebEngineScript()
    script.setSourceCode(js_code)
    script.setInjectionPoint(QWebEngineScript.DocumentCreation)
    script.setWorldId(QWebEngineScript.MainWorld)
    script.setRunsOnSubFrames(True)
    profile.scripts().insert(script)

class BrowserEngine(QMainWindow):
    def __init__(self, parent_hwnd, url, url_file, state_file):
        super().__init__()
        self.url_file = url_file
        self.state_file = state_file
        self.parent_hwnd = parent_hwnd
        self.is_detached = False
        
        # Iniciar no estado anexado (frameless)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Criar Perfil persistente/específico
        self.profile = QWebEngineProfile("poe2_bot_profile", self)
        self.interceptor = AdBlocker()
        self.profile.setUrlRequestInterceptor(self.interceptor)
        inject_adblock_js(self.profile)

        self.browser = QWebEngineView(self)
        self.page = QWebEnginePage(self.profile, self.browser)
        self.browser.setPage(self.page)
        
        self.browser.setUrl(QUrl(url))
        self.setCentralWidget(self.browser)
        
        # URL change signal
        self.browser.urlChanged.connect(self.on_url_changed)
        
        # Embed inicial
        win32gui.SetParent(int(self.winId()), parent_hwnd)
        
        # Timer de auto-resize e monitoramento de estado
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.periodic_check)
        self.monitor_timer.start(200) # Check every 200ms
        
        # Initial resize
        self.check_parent_resize()

    def on_url_changed(self, url):
        with open(self.url_file, "w") as f:
            f.write(url.toString())

    def periodic_check(self):
        self.check_state()
        if not self.is_detached:
            self.check_parent_resize()

    def check_state(self):
        if not os.path.exists(self.state_file):
            return
            
        try:
            with open(self.state_file, "r") as f:
                state = f.read().strip()
                
            if state == "detached" and not self.is_detached:
                self.detach_window()
            elif state == "attached" and self.is_detached:
                self.attach_window()
        except Exception:
            pass

    def detach_window(self):
        self.is_detached = True
        
        # Obter posição do bot (pai) para centralizar a nova janela
        try:
            rect = win32gui.GetWindowRect(self.parent_hwnd)
            parent_x, parent_y, parent_w, parent_h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
            
            # Tamanho desejado para o browser desprendido (ex: 800x600 ou manter o atual se for razoável)
            new_w, new_h = 900, 700 
            center_x = parent_x + (parent_w - new_w) // 2
            center_y = parent_y + (parent_h - new_h) // 2
        except:
            center_x, center_y, new_w, new_h = 100, 100, 900, 700

        self.hide()
        # Mudar flags para janela normal sem botão de fechar
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowMinMaxButtonsHint)
        self.setWindowTitle("PoE2 Browser (Anexe para fechar)")
        
        # Desprender do pai
        win32gui.SetParent(int(self.winId()), 0)
        
        # Posicionar e mostrar
        self.setGeometry(center_x, center_y, new_w, new_h)
        self.show()
        self.raise_()
        self.activateWindow()

    def attach_window(self):
        self.is_detached = False
        self.hide()
        # Mudar flags de volta para frameless
        self.setWindowFlags(Qt.FramelessWindowHint)
        # Anexar ao pai
        win32gui.SetParent(int(self.winId()), self.parent_hwnd)
        self.show()
        self.check_parent_resize()

    def closeEvent(self, event):
        """Impede o fechamento da janela se estiver desprendida."""
        if self.is_detached:
            # Não deixa fechar, o usuário deve anexar de volta
            event.ignore()
        else:
            event.accept()

    def check_parent_resize(self):
        try:
            rect = win32gui.GetClientRect(self.parent_hwnd)
            new_w, new_h = rect[2], rect[3]
            if self.width() != new_w or self.height() != new_h:
                self.setGeometry(0, 0, new_w, new_h)
        except Exception:
            # Parent might be closed
            sys.exit(0)

def main():
    if len(sys.argv) < 5:
        print("Usage: browser_provider.py <hwnd> <url> <url_file> <state_file>")
        return
    
    parent_hwnd = int(sys.argv[1])
    initial_url = sys.argv[2]
    url_file = sys.argv[3]
    state_file = sys.argv[4]
    
    app = QApplication(sys.argv)
    
    # Criar .tmp se não existir
    os.makedirs(os.path.dirname(url_file), exist_ok=True)
    
    engine = BrowserEngine(parent_hwnd, initial_url, url_file, state_file)
    engine.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
