import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "TestService"
    _svc_display_name_ = "Test Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        self.main()

    def main(self):
        run()


if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(AppServerSvc)

# pyinstaller --noconfirm --onefile --windowed --icon "C:/Users/Dominik/Desktop/Im a dolphin/icon.ico" --clean --disable-windowed-traceback --add-data "C:/Users/Dominik/Desktop/Im a dolphin/windows_service/screenMessage.pyw;."  "C:/Users/Dominik/Desktop/Im a dolphin/windows_service/service.py"
# sc create "atest" binPath="C:\Users\Dominik\Desktop\service.exe" start=auto error=ignore DisplayName="atest"

import win32api, win32con, win32gui, win32ui, base64, random

count = 1

def run():
    hInstance = win32api.GetModuleHandle()
    className = "svchost."

    # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633576(v=vs.85).aspx
    # win32gui does not support WNDCLASSEX.
    wndClass = win32gui.WNDCLASS()
    # http://msdn.microsoft.com/en-us/library/windows/desktop/ff729176(v=vs.85).aspx
    wndClass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
    wndClass.lpfnWndProc = wndProc
    wndClass.hInstance = hInstance
    wndClass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
    wndClass.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
    wndClass.lpszClassName = className
    # win32gui does not support RegisterClassEx
    wndClassAtom = win32gui.RegisterClass(wndClass)

    # http://msdn.microsoft.com/en-us/library/windows/desktop/ff700543(v=vs.85).aspx
    # Consider using: WS_EX_COMPOSITED, WS_EX_LAYERED, WS_EX_NOACTIVATE, WS_EX_TOOLWINDOW, WS_EX_TOPMOST, WS_EX_TRANSPARENT
    # The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
    exStyle = (
        win32con.WS_EX_COMPOSITED
        | win32con.WS_EX_LAYERED
        | win32con.WS_EX_NOACTIVATE
        | win32con.WS_EX_TOPMOST
        | win32con.WS_EX_TRANSPARENT
    )

    # http://msdn.microsoft.com/en-us/library/windows/desktop/ms632600(v=vs.85).aspx
    # Consider using: WS_DISABLED, WS_POPUP, WS_VISIBLE
    style = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE

    # http://msdn.microsoft.com/en-us/library/windows/desktop/ms632680(v=vs.85).aspx
    hWindow = win32gui.CreateWindowEx(
        exStyle,
        wndClassAtom,
        None,  # WindowName
        style,
        0,  # x
        0,  # y
        win32api.GetSystemMetrics(win32con.SM_CXSCREEN),  # width
        round(win32api.GetSystemMetrics(win32con.SM_CYSCREEN) * 0.93),  # height
        None,  # hWndParent
        None,  # hMenu
        hInstance,
        None,  # lpParam
    )

    # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633540(v=vs.85).aspx
    win32gui.SetLayeredWindowAttributes(
        hWindow, 0x00FFFFFF, 255, win32con.LWA_COLORKEY | win32con.LWA_ALPHA
    )

    # http://msdn.microsoft.com/en-us/library/windows/desktop/dd145167(v=vs.85).aspx
    # win32gui.UpdateWindow(hWindow)

    # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633545(v=vs.85).aspx
    win32gui.SetWindowPos(
        hWindow,
        win32con.HWND_TOPMOST,
        0,
        0,
        0,
        0,
        win32con.SWP_NOACTIVATE
        | win32con.SWP_NOMOVE
        | win32con.SWP_NOSIZE
        | win32con.SWP_SHOWWINDOW,
    )

    # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633548(v=vs.85).aspx
    # win32gui.ShowWindow(hWindow, win32con.SW_SHOW)

    win32gui.PumpMessages()

def wndProc(hWnd, message, wParam, lParam):
    if message == win32con.WM_PAINT:
        hdc, paintStruct = win32gui.BeginPaint(hWnd)

        dpiScale = win32ui.GetDeviceCaps(hdc, win32con.LOGPIXELSX) / 60.0
        fontSize = 24

        # http://msdn.microsoft.com/en-us/library/windows/desktop/dd145037(v=vs.85).aspx
        lf = win32gui.LOGFONT()
        lf.lfFaceName = "Roboto"
        lf.lfHeight = int(round(dpiScale * fontSize))
        # lf.lfWeight = 150
        # Use nonantialiased to remove the white edges around the text.
        lf.lfQuality = win32con.NONANTIALIASED_QUALITY
        hf = win32gui.CreateFontIndirect(lf)
        win32gui.SelectObject(hdc, hf)

        rect = win32gui.GetClientRect(hWnd)

        r = random.randint(0, 254)
        g = random.randint(0, 254)
        b = random.randint(0, 254)
        setColor(hdc, rect, hWnd, paintStruct, r, g, b)
        return 0

    elif message == win32con.WM_DESTROY:
        win32gui.PostQuitMessage(0)
        return 0

    else:
        return win32gui.DefWindowProc(hWnd, message, wParam, lParam)

def setColor(hdc, rect, hWnd, paintStruct, r, g, b):
    win32gui.SetTextColor(hdc, win32api.RGB(r, g, b))

    # http://msdn.microsoft.com/en-us/library/windows/desktop/dd162498(v=vs.85).aspx
    win32gui.DrawText(
        hdc,
        "WEEEEEE",  # base64.b64decode("TWVpbiBOYW1lIGlzdCBKYW4gSGVpbG1hbm4=").decode("utf-8"),
        -1,
        rect,
        win32con.DT_BOTTOM | win32con.DT_RIGHT | win32con.DT_SINGLELINE,
    )
    win32gui.EndPaint(hWnd, paintStruct)
    