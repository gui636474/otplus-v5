# -*- coding: utf-8 -*-
"""
OT PLUS GUI v3 - Cliente
Requer: pip install requests
Rode como ADMINISTRADOR.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess, threading, os, sys, ctypes, uuid, datetime, json
import urllib.request, socket

# ================= CONFIG =================
API_URL = "https://SEU-APP.onrender.com"  # ⚠ COLOQUE A URL DO SEU BACKEND
HEARTBEAT_MIN = 5
# ==========================================

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def run(cmd, timeout=600):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return -1, str(e)

def get_hwid():
    try:
        out = subprocess.check_output(
            'reg query "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid',
            shell=True, stderr=subprocess.DEVNULL, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW)
        for l in out.splitlines():
            if "MachineGuid" in l: return l.split()[-1]
    except: pass
    return str(uuid.getnode())

def get_ip():
    for u in ["https://api.ipify.org", "https://icanhazip.com", "https://ifconfig.me/ip"]:
        try:
            with urllib.request.urlopen(u, timeout=5) as r: return r.read().decode().strip()
        except: continue
    return "0.0.0.0"

def api_post(path, data, token=None):
    try:
        req = urllib.request.Request(API_URL + path,
              data=json.dumps(data).encode(),
              headers={"Content-Type": "application/json",
                       **({"Authorization": f"Bearer {token}"} if token else {})})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"ok": False, "reason": "network", "msg": f"Erro de rede: {e}"}

# ================= 120+ OTIMIZAÇÕES =================
TAREFAS = {
"🧹 Limpeza Profunda": [
 ("Temp do usuário", r'del /q /f /s "%TEMP%\*" >nul 2>&1 & for /d %i in ("%TEMP%\*") do @rd /s /q "%i" >nul 2>&1'),
 ("Temp do Windows", r'del /q /f /s "C:\Windows\Temp\*" >nul 2>&1'),
 ("Prefetch", r'del /q /f /s "C:\Windows\Prefetch\*" >nul 2>&1'),
 ("Lixeira", r'PowerShell -Command "Clear-RecycleBin -Force -EA SilentlyContinue"'),
 ("Cache DNS", r'ipconfig /flushdns'),
 ("Cache Windows Update", r'net stop wuauserv & net stop bits & del /q /f /s "C:\Windows\SoftwareDistribution\Download\*" >nul 2>&1 & net start wuauserv & net start bits'),
 ("Logs de eventos", r'for /f "tokens=*" %1 in (\'wevtutil el\') do @wevtutil cl "%1" >nul 2>&1'),
 ("Cache miniaturas", r'del /q /f /s "%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*.db" >nul 2>&1'),
 ("Cache ícones", r'ie4uinit.exe -show & del /q /f /s "%LOCALAPPDATA%\IconCache.db" >nul 2>&1'),
 ("Documentos recentes", r'del /q /f /s "%APPDATA%\Microsoft\Windows\Recent\*" >nul 2>&1'),
 ("WER (relatórios erro)", r'del /q /f /s "%LOCALAPPDATA%\Microsoft\Windows\WER\*" >nul 2>&1 & del /q /f /s "C:\ProgramData\Microsoft\Windows\WER\*" >nul 2>&1'),
 ("Minidumps / MEMORY.DMP", r'del /q /f /s "C:\Windows\Minidump\*" >nul 2>&1 & del /q /f "C:\Windows\MEMORY.DMP" >nul 2>&1'),
 ("Logs CBS", r'del /q /f /s "C:\Windows\Logs\CBS\*" >nul 2>&1'),
 ("Delivery Optimization", r'del /q /f /s "C:\Windows\SoftwareDistribution\DeliveryOptimization\*" >nul 2>&1'),
 ("Cache Chrome", r'del /q /f /s "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache\*" >nul 2>&1'),
 ("Cache Edge", r'del /q /f /s "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache\*" >nul 2>&1'),
 ("Cache Firefox", r'del /q /f /s "%LOCALAPPDATA%\Mozilla\Firefox\Profiles\*\cache2\*" >nul 2>&1'),
 ("Cache Brave", r'del /q /f /s "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Cache\*" >nul 2>&1'),
 ("Cache Opera GX", r'del /q /f /s "%APPDATA%\Opera Software\Opera GX Stable\Cache\*" >nul 2>&1'),
 ("Cache Discord", r'del /q /f /s "%APPDATA%\discord\Cache\*" >nul 2>&1 & del /q /f /s "%APPDATA%\discord\Code Cache\*" >nul 2>&1'),
 ("Cache Spotify", r'del /q /f /s "%LOCALAPPDATA%\Spotify\Storage\*" >nul 2>&1'),
 ("Cache Steam", r'del /q /f /s "C:\Program Files (x86)\Steam\appcache\httpcache\*" >nul 2>&1'),
 ("Windows.old", r'takeown /f C:\Windows.old /r /d y >nul 2>&1 & icacls C:\Windows.old /grant %USERNAME%:F /t >nul 2>&1 & rd /s /q C:\Windows.old >nul 2>&1'),
 ("Pantry / Downloaded Installers", r'del /q /f /s "C:\ProgramData\Microsoft\Windows\WER\*" >nul 2>&1'),
 ("Installers antigos Downloads", r'del /q /f /s "%USERPROFILE%\Downloads\*.tmp" >nul 2>&1'),
 ("Fontes antigas", r'reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Courier 10,12,15" /f >nul 2>&1'),
],

"⚡ CPU / Performance": [
 ("Plano Alto Desempenho", r'powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'),
 ("Plano Ultimate Performance", r'powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1 & powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1'),
 ("Desativar Power Throttling", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling" /v PowerThrottlingOff /t REG_DWORD /d 1 /f'),
 ("Efeitos: desempenho", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f'),
 ("Desativar animações", r'reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f'),
 ("Desativar transparência", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f'),
 ("Sem delay de menu", r'reg add "HKCU\Control Panel\Desktop" /v MenuShowDelay /t REG_SZ /d 0 /f'),
 ("Sem delay de startup", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize" /v StartupDelayInMSec /t REG_DWORD /d 0 /f'),
 ("Shutdown rápido", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control" /v WaitToKillServiceTimeout /t REG_SZ /d 2000 /f'),
 ("Prioridade CPU p/ apps", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v Win32PrioritySeparation /t REG_DWORD /d 38 /f'),
 ("Desativar Core Parking", r'powercfg -setacvalueindex SCHEME_CURRENT SUB_PROCESSOR CPMINCORES 100 & powercfg -setactive SCHEME_CURRENT'),
 ("Frequência mínima 100%", r'powercfg -setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMIN 100 & powercfg -setactive SCHEME_CURRENT'),
 ("Frequência máxima 100%", r'powercfg -setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 100 & powercfg -setactive SCHEME_CURRENT'),
 ("Desativar C-States CPU", r'powercfg -setacvalueindex SCHEME_CURRENT SUB_PROCESSOR IDLEDISABLE 1 & powercfg -setactive SCHEME_CURRENT'),
 ("MMCSS SystemResponsiveness", r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v SystemResponsiveness /t REG_DWORD /d 10 /f'),
 ("Network Throttling Off", r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v NetworkThrottlingIndex /t REG_DWORD /d 4294967295 /f'),
 ("Desativar mitigations Spectre/Meltdown", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v FeatureSettingsOverride /t REG_DWORD /d 3 /f & reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v FeatureSettingsOverrideMask /t REG_DWORD /d 3 /f'),
 ("Desativar Superfetch/SysMain", r'sc stop SysMain & sc config SysMain start= disabled'),
 ("Desativar Windows Search", r'sc stop WSearch & sc config WSearch start= disabled'),
 ("Desativar serviço de erros", r'sc stop WerSvc & sc config WerSvc start= disabled'),
 ("Desativar Fax", r'sc stop Fax & sc config Fax start= disabled'),
 ("Desativar Print Spooler (se não usa impressora)", r'sc stop Spooler & sc config Spooler start= disabled'),
 ("Desativar Xbox Services", r'sc stop XblAuthManager & sc config XblAuthManager start= disabled & sc stop XblGameSave & sc config XblGameSave start= disabled & sc stop XboxNetApiSvc & sc config XboxNetApiSvc start= disabled'),
 ("Desativar Bluetooth (desktop)", r'sc stop bthserv & sc config bthserv start= disabled >nul 2>&1'),
 ("Desativar Sensor Service", r'sc stop SensrSvc & sc config SensrSvc start= disabled >nul 2>&1'),
 ("Desativar Remote Registry", r'sc stop RemoteRegistry & sc config RemoteRegistry start= disabled'),
 ("Desativar HomeGroup", r'sc stop HomeGroupListener & sc config HomeGroupListener start= disabled >nul 2>&1 & sc stop HomeGroupProvider & sc config HomeGroupProvider start= disabled >nul 2>&1'),
 ("Desativar Windows Biometric", r'sc stop WbioSrvc & sc config WbioSrvc start= disabled >nul 2>&1'),
 ("Desativar Tablet Input", r'sc stop TabletInputService & sc config TabletInputService start= disabled >nul 2>&1'),
 ("Desativar Touch Keyboard", r'sc stop TabletInputService & sc config TabletInputService start= disabled >nul 2>&1'),
 ("Desativar Wallet", r'sc stop WalletService & sc config WalletService start= disabled >nul 2>&1'),
],

"🎮 GPU / Gaming": [
 ("Ativar Game Mode", r'reg add "HKCU\Software\Microsoft\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f & reg add "HKCU\Software\Microsoft\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f'),
 ("Desativar Game DVR", r'reg add "HKCU\System\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f & reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v AllowGameDVR /t REG_DWORD /d 0 /f'),
 ("HAGS (GPU Scheduling)", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f'),
 ("Prioridade GPU alta p/ games", r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f'),
 ("Games task priority", r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v Priority /t REG_DWORD /d 6 /f'),
 ("Games Scheduling Category", r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d High /f'),
 ("Games SFIO Priority", r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "SFIO Priority" /t REG_SZ /d High /f'),
 ("Desativar NVIDIA Telemetry", r'sc stop NvTelemetryContainer >nul 2>&1 & sc config NvTelemetryContainer start= disabled >nul 2>&1'),
 ("NVIDIA tweak DPC", r'reg add "HKLM\SOFTWARE\NVIDIA Corporation\Global\NVTweak" /v "RmGpsPsEnablePerCpuCoreDpc" /t REG_DWORD /d 1 /f >nul 2>&1'),
 ("NVIDIA Disable P-State", r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm" /v DisableDynamicPstate /t REG_DWORD /d 1 /f >nul 2>&1'),
 ("AMD Disable Throttling", r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\amdkmdag" /v PP_ThermalAutoThrottlingEnable /t REG_DWORD /d 0 /f >nul 2>&1'),
 ("AMD Disable ULPS", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000" /v EnableUlps /t REG_DWORD /d 0 /f >nul 2>&1'),
 ("Desativar Xbox Game Bar", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f'),
 ("Multi-plane overlay off (input lag)", r'reg add "HKLM\SOFTWARE\Microsoft\Windows\Dwm" /v OverlayTestMode /t REG_DWORD /d 5 /f >nul 2>&1'),
 ("Fullscreen optimizations off", r'reg add "HKCU\System\GameConfigStore" /v GameDVR_FSEBehaviorMode /t REG_DWORD /d 2 /f'),
 ("Desativar captura Xbox Win+G", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v HistoricalCaptureEnabled /t REG_DWORD /d 0 /f'),
],

"🖱️ Input / Latência": [
 ("Desativar aceleração de mouse", r'reg add "HKCU\Control Panel\Mouse" /v MouseSpeed /t REG_SZ /d 0 /f & reg add "HKCU\Control Panel\Mouse" /v MouseThreshold1 /t REG_SZ /d 0 /f & reg add "HKCU\Control Panel\Mouse" /v MouseThreshold2 /t REG_SZ /d 0 /f'),
 ("Mouse 1:1 raw input", r'reg add "HKCU\Control Panel\Mouse" /v MouseSensitivity /t REG_SZ /d 10 /f'),
 ("Desativar Sticky Keys", r'reg add "HKCU\Control Panel\Accessibility\StickyKeys" /v Flags /t REG_SZ /d 506 /f'),
 ("Desativar Filter Keys", r'reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v Flags /t REG_SZ /d 122 /f'),
 ("Desativar Toggle Keys", r'reg add "HKCU\Control Panel\Accessibility\ToggleKeys" /v Flags /t REG_SZ /d 58 /f'),
 ("Desativar Gestos de borda", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\ImmersiveShell\EdgeUI" /v DisableTLCorner /t REG_DWORD /d 1 /f & reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\ImmersiveShell\EdgeUI" /v DisableTRCorner /t REG_DWORD /d 1 /f'),
 ("KB repeat rate rápido", r'reg add "HKCU\Control Panel\Keyboard" /v KeyboardDelay /t REG_SZ /d 0 /f & reg add "HKCU\Control Panel\Keyboard" /v KeyboardSpeed /t REG_SZ /d 31 /f'),
 ("Desativar Narrator", r'reg add "HKCU\Software\Microsoft\Narrator\NoRoam" /v RunningState /t REG_DWORD /d 0 /f >nul 2>&1'),
],

"🌐 Rede / Internet": [
 ("TCP autotuning normal", r'netsh int tcp set global autotuninglevel=normal'),
 ("Desativar heurística ECN", r'netsh int tcp set heuristics disabled'),
 ("Ativar RSS", r'netsh int tcp set global rss=enabled'),
 ("Limpar ARP", r'arp -d * >nul 2>&1'),
 ("Reset TCP/IP + Winsock", r'netsh int ip reset & netsh winsock reset'),
 ("Desativar QoS reservado", r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Psched" /v NonBestEffortLimit /t REG_DWORD /d 0 /f'),
 ("DNS Cloudflare", r'netsh interface ip set dns "Wi-Fi" static 1.1.1.1 >nul 2>&1 & netsh interface ip add dns "Wi-Fi" 1.0.0.1 index=2 >nul 2>&1 & netsh interface ip set dns "Ethernet" static 1.1.1.1 >nul 2>&1 & netsh interface ip add dns "Ethernet" 1.0.0.1 index=2 >nul 2>&1'),
 ("Desativar IPv6", r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters" /v DisabledComponents /t REG_DWORD /d 0xFF /f'),
 ("Desativar NetBIOS", r'PowerShell -Command "Get-WmiObject Win32_NetworkAdapterConfiguration | Where {$_.IPEnabled} | ForEach {$_.SetTcpipNetbios(2)}" >nul 2>&1'),
 ("Desativar LLMNR", r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient" /v EnableMulticast /t REG_DWORD /d 0 /f'),
 ("Otimizar TCP global", r'netsh int tcp set global chimney=disabled & netsh int tcp set global ecncapability=disabled & netsh int tcp set global timestamps=disabled'),
 ("Desativar SMB1", r'PowerShell -Command "Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart -EA SilentlyContinue" >nul 2>&1'),
 ("Desativar Teredo", r'netsh interface teredo set state disabled'),
 ("Desativar Autotuning fraco", r'netsh int tcp set global autotuninglevel=restricted'),
 ("Medir MTU automático", r'netsh interface ipv4 set subinterface "Wi-Fi" mtu=1500 store=persistent >nul 2>&1 & netsh interface ipv4 set subinterface "Ethernet" mtu=1500 store=persistent >nul 2>&1'),
],

"💾 Disco / SSD": [
 ("Otimizar unidade C:", r'defrag C: /O'),
 ("TRIM ativado", r'fsutil behavior set DisableDeleteNotify 0'),
 ("Desativar Last Access Update", r'fsutil behavior set disablelastaccess 1'),
 ("Desativar 8.3 filenames", r'fsutil behavior set disable8dot3 1'),
 ("Aumentar IRPStackSize", r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v IRPStackSize /t REG_DWORD /d 32 /f'),
 ("Desativar indexação em SSD", r'sc config WSearch start= disabled & sc stop WSearch >nul 2>&1'),
 ("Aumentar cache de escrita", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v LargeSystemCache /t REG_DWORD /d 1 /f >nul 2>&1'),
 ("Desativar NTFS Compression", r'PowerShell -Command "Get-ChildItem -Path C:\\ -Recurse -Force -EA SilentlyContinue | Where-Object {$_.Attributes -match \"Compressed\"} | ForEach-Object {compact /u /i /f $_.FullName}" >nul 2>&1'),
 ("SFC /scannow", r'sfc /scannow'),
 ("DISM RestoreHealth", r'DISM /Online /Cleanup-Image /RestoreHealth'),
 ("CHKDSK agendado", r'chkntfs /c C:'),
 ("Check Disk rápido", r'fsutil dirty query C: >nul 2>&1'),
],

"🧠 RAM / Memória": [
 ("Desativar Paging Executive", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v DisablePagingExecutive /t REG_DWORD /d 1 /f'),
 ("Large System Cache", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v LargeSystemCache /t REG_DWORD /d 1 /f'),
 ("ClearPageFileAtShutdown OFF", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v ClearPageFileAtShutdown /t REG_DWORD /d 0 /f'),
 ("Desativar Memory Compression", r'PowerShell -Command "Disable-MMAgent -MemoryCompression -EA SilentlyContinue" >nul 2>&1'),
 ("Prefetch/Superfetch config", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters" /v EnablePrefetcher /t REG_DWORD /d 3 /f & reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters" /v EnableSuperfetch /t REG_DWORD /d 3 /f'),
 ("Limpar Working Set RAM", r'PowerShell -Command "Get-Process | ForEach-Object { try { $_.EmptyWorkingSet() } catch {} }" >nul 2>&1'),
 ("Otimizar uso RAM em background", r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v Start_TrackProgs /t REG_DWORD /d 0 /f'),
],

"🔒 Privacidade": [
 ("Desativar Telemetria", r'sc stop DiagTrack & sc config DiagTrack start= disabled & sc stop dmwappushservice & sc config dmwappushservice start= disabled'),
 ("Bloquear coleta de dados", r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f'),
 ("Desativar Cortana", r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f'),
 ("Desativar anúncios", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SubscribedContent-338388Enabled /t REG_DWORD /d 0 /f'),
 ("Desativar Feedback", r'reg add "HKCU\Software\Microsoft\Siuf\Rules" /v NumberOfSIUFInPeriod /t REG_DWORD /d 0 /f'),
 ("Desativar histórico atividades", r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v EnableActivityFeed /t REG_DWORD /d 0 /f'),
 ("Negar localização", r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" /v Value /t REG_SZ /d Deny /f'),
 ("Desativar Bing no menu", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" /v BingSearchEnabled /t REG_DWORD /d 0 /f'),
 ("Desativar Copilot", r'reg add "HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f'),
 ("Desativar Spotlight", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v RotatingLockScreenEnabled /t REG_DWORD /d 0 /f'),
 ("Desativar Advertising ID", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f'),
 ("Desativar câmera em apps", r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam" /v Value /t REG_SZ /d Deny /f'),
 ("Desativar microfone em apps", r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone" /v Value /t REG_SZ /d Deny /f'),
 ("Desativar sincronização", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\SettingSync" /v SyncPolicy /t REG_DWORD /d 5 /f >nul 2>&1'),
 ("Desativar Wi-Fi Sense", r'reg add "HKLM\SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager\config" /v AutoConnectAllowedOEM /t REG_DWORD /d 0 /f >nul 2>&1'),
],

"📦 Bloatware": [
 ("Remover Xbox apps", r'PowerShell -Command "Get-AppxPackage *xbox* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Groove Music", r'PowerShell -Command "Get-AppxPackage *zunemusic* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Movies & TV", r'PowerShell -Command "Get-AppxPackage *zunevideo* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover 3D Viewer", r'PowerShell -Command "Get-AppxPackage *3d* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Paint 3D", r'PowerShell -Command "Get-AppxPackage *paint3d* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Skype", r'PowerShell -Command "Get-AppxPackage *skype* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover OneNote", r'PowerShell -Command "Get-AppxPackage *onenote* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Solitaire", r'PowerShell -Command "Get-AppxPackage *solitaire* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover News", r'PowerShell -Command "Get-AppxPackage *bingnews* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Weather", r'PowerShell -Command "Get-AppxPackage *bingweather* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Tips", r'PowerShell -Command "Get-AppxPackage *getstarted* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Maps", r'PowerShell -Command "Get-AppxPackage *maps* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Feedback Hub", r'PowerShell -Command "Get-AppxPackage *feedback* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Your Phone", r'PowerShell -Command "Get-AppxPackage *yourphone* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover People", r'PowerShell -Command "Get-AppxPackage *people* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Office Hub", r'PowerShell -Command "Get-AppxPackage *officehub* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover Sticky Notes", r'PowerShell -Command "Get-AppxPackage *stickynotes* | Remove-AppxPackage -EA SilentlyContinue"'),
 ("Remover OneDrive (sistema)", r'taskkill /f /im OneDrive.exe >nul 2>&1 & reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\OneDrive" /v DisableFileSyncNGSC /t REG_DWORD /d 1 /f'),
 ("Sem apps silenciosos", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SilentInstalledAppsEnabled /t REG_DWORD /d 0 /f'),
 ("Remover Widgets", r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Dsh" /v AllowNewsAndInterests /t REG_DWORD /d 0 /f'),
 ("Sem sugestões no menu iniciar", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SystemPaneSuggestionsEnabled /t REG_DWORD /d 0 /f'),
],

"🚀 Boot / Startup": [
 ("Boot com múltiplos núcleos", r'bcdedit /set numproc 8'),
 ("Boot timeout curto", r'bcdedit /timeout 3'),
 ("Desativar boot GUI", r'bcdedit /set bootux disabled'),
 ("Boot advanced options", r'bcdedit /set advancedoptions off'),
 ("Fast boot", r'powercfg /hibernate on >nul 2>&1 & powercfg /h /type reduced >nul 2>&1'),
 ("Desativar recuperação automática", r'bcdedit /set recoveryenabled No >nul 2>&1'),
 ("Boot menu policy", r'bcdedit /set bootmenupolicy standard'),
 ("Desativar verificações de assinatura", r'bcdedit /set nointegritychecks on >nul 2>&1'),
 ("Limpar entradas antigas do boot", r'bcdedit /deletevalue {badmemory} >nul 2>&1'),
],

"🎨 Explorer / UI": [
 ("Mostrar extensões de arquivo", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f'),
 ("Mostrar arquivos ocultos", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v Hidden /t REG_DWORD /d 1 /f'),
 ("Abrir Explorer em Meu PC", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v LaunchTo /t REG_DWORD /d 1 /f'),
 ("Desativar Task View", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowTaskViewButton /t REG_DWORD /d 0 /f'),
 ("Desativar Widgets na taskbar", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarDa /t REG_DWORD /d 0 /f'),
 ("Desativar Chat na taskbar", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarMn /t REG_DWORD /d 0 /f'),
 ("Menu iniciar clássico", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v Start_ShowClassicMode /t REG_DWORD /d 1 /f'),
 ("Expandir pastas no menu", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v Start_TrackDocs /t REG_DWORD /d 1 /f'),
 ("Acelerar menu de contexto", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer" /v MultipleInvokePromptMinimum /t REG_DWORD /d 300 /f'),
 ("Desativar animação de janelas", r'reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f'),
 ("Barra de tarefas pequena", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarSmallIcons /t REG_DWORD /d 1 /f'),
 ("Notificações desativadas", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\PushNotifications" /v ToastEnabled /t REG_DWORD /d 0 /f'),
 ("Foco assistido ON", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\CloudStore\Store\DefaultAccount\Current\default$windows.data.notifications.quiethourssettings" /v Data /t REG_BINARY /d 0 /f >nul 2>&1'),
],

"🔊 Áudio": [
 ("Desativar exclusividade de áudio", r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render" /v DisableExclusiveMode /t REG_DWORD /d 1 /f >nul 2>&1'),
 ("Desativar aprimoramentos de áudio", r'reg add "HKCU\Software\Microsoft\Multimedia\Audio" /v UserDuckingPreference /t REG_DWORD /d 3 /f'),
 ("Sem redução de volume automática", r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render" /v Ducking /t REG_DWORD /d 0 /f >nul 2>&1'),
 ("Desativar serviços de áudio extras", r'sc stop Audiosrv & sc config Audiosrv start= auto >nul 2>&1'),
],

"🛡️ Sistema / Kernel": [
 ("Desativar UAC prompts", r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v ConsentPromptBehaviorAdmin /t REG_DWORD /d 0 /f'),
 ("Desativar SmartScreen", r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v EnableSmartScreen /t REG_DWORD /d 0 /f'),
 ("Desativar reserva de banda", r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Psched" /v NonBestEffortLimit /t REG_DWORD /d 0 /f'),
 ("Desativar Error Reporting", r'sc stop WerSvc & sc config WerSvc start= disabled'),
 ("Desativar Auto-Run", r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 255 /f'),
 ("Desativar AutoPlay", r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\AutoplayHandlers" /v DisableAutoplay /t REG_DWORD /d 1 /f'),
 ("Desativar Defender (perf)", r'PowerShell -Command "Set-MpPreference -DisableRealtimeMonitoring $true -EA SilentlyContinue" >nul 2>&1'),
 ("Desativar Windows Update automático", r'sc stop wuauserv & sc config wuauserv start= disabled >nul 2>&1'),
 ("Desativar Scheduled Defrag", r'schtasks /Change /TN "Microsoft\Windows\Defrag\ScheduledDefrag" /Disable >nul 2>&1'),
 ("Desativar CEIP", r'schtasks /Change /TN "Microsoft\Windows\Customer Experience Improvement Program\Consolidator" /Disable >nul 2>&1'),
 ("Desativar Disk Diagnostic", r'schtasks /Change /TN "Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector" /Disable >nul 2>&1'),
],

"🖥️ Serviços Adicionais": [
 ("Desativar AllJoyn Router", r'sc stop AJRouter & sc config AJRouter start= disabled >nul 2>&1'),
 ("Desativar App Readiness", r'sc stop AppReadiness & sc config AppReadiness start= disabled >nul 2>&1'),
 ("Desativar Connected Devices Platform", r'sc stop CDPSvc & sc config CDPSvc start= disabled >nul 2>&1'),
 ("Desativar Downloaded Maps", r'sc stop MapsBroker & sc config MapsBroker start= disabled >nul 2>&1'),
 ("Desativar Geolocation", r'sc stop lfsvc & sc config lfsvc start= disabled >nul 2>&1'),
 ("Desativar Phone Service", r'sc stop PhoneSvc & sc config PhoneSvc start= disabled >nul 2>&1'),
 ("Desativar PrintWorkflow", r'sc stop PrintWorkflowUserSvc & sc config PrintWorkflowUserSvc start= disabled >nul 2>&1'),
 ("Desativar Retail Demo", r'sc stop RetailDemo & sc config RetailDemo start= disabled >nul 2>&1'),
 ("Desativar SysMain (novamente)", r'sc stop SysMain & sc config SysMain start= disabled >nul 2>&1'),
 ("Desativar Windows Insider", r'sc stop wisvc & sc config wisvc start= disabled >nul 2>&1'),
 ("Desativar Work Folders", r'sc stop WorkFolders & sc config WorkFolders start= disabled >nul 2>&1'),
 ("Desativar Windows Push Notifications", r'sc stop WpnService & sc config WpnService start= disabled >nul 2>&1'),
],

"🔬 Ferramentas / Info": [
 ("Verificar saúde do disco", r'wmic diskdrive get status >nul 2>&1'),
 ("Limpar buffer standby (RAM)", r'PowerShell -Command "Get-Process | ForEach { $_.EmptyWorkingSet() }" >nul 2>&1'),
 ("Info do sistema", r'systeminfo | findstr /C:"OS Name" /C:"Total Physical Memory"'),
 ("Bateria / Energia info", r'powercfg /batteryreport /output "%USERPROFILE%\Desktop\battery.html" >nul 2>&1'),
 ("Relatório energia", r'powercfg /energy /output "%USERPROFILE%\Desktop\energy.html" /duration 60 >nul 2>&1'),
 ("Desativar Todos os Sons do sistema", r'reg add "HKCU\AppEvents\Schemes" /v ".Current" /t REG_SZ /d "" /f >nul 2>&1'),
 ("Sem verificação de disco ao boot", r'chkntfs /x C: >nul 2>&1'),
 ("Desativar System Restore (último)", r'vssadmin delete shadows /all /quiet >nul 2>&1'),
],
}

# ================= APP =================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OT PLUS v3")
        self.geometry("1150x820")
        self.configure(bg="#0a0e13")
        self.hwid = get_hwid()
        self.ip = "..."
        self.token_data = None
        self._hb_stop = False
        threading.Thread(target=self._load_ip, daemon=True).start()
        self._style()
        self._show_login()

    def _load_ip(self):
        self.ip = get_ip()

    def _style(self):
        st = ttk.Style(self); st.theme_use("clam")
        st.configure("TNotebook", background="#0a0e13", borderwidth=0)
        st.configure("TNotebook.Tab", background="#161c24", foreground="#7ee7ff",
                     padding=[12, 8], font=("Consolas", 9, "bold"))
        st.map("TNotebook.Tab", background=[("selected", "#0a0e13")],
               foreground=[("selected", "#39ff14")])
        st.configure("TCheckbutton", background="#0a0e13", foreground="#d6f7ff",
                     font=("Consolas", 9))
        st.map("TCheckbutton", background=[("active", "#0a0e13")])
        st.configure("Progressbar", troughcolor="#161c24", background="#39ff14")

    def _clear(self):
        for w in self.winfo_children(): w.destroy()

    def _show_login(self):
        self._clear()
        self._hb_stop = True
        f = tk.Frame(self, bg="#0a0e13"); f.pack(expand=True, fill="both")
        tk.Label(f, text="⚡ OT PLUS", fg="#39ff14", bg="#0a0e13",
                 font=("Consolas", 44, "bold")).pack(pady=(80, 4))
        tk.Label(f, text="PAINEL DE OTIMIZAÇÃO PRO • v3.0", fg="#7ee7ff",
                 bg="#0a0e13", font=("Consolas", 12)).pack(pady=(0, 40))
        card = tk.Frame(f, bg="#161c24", padx=40, pady=32); card.pack()
        tk.Label(card, text="🔑 Ativação Online", fg="#d6f7ff",
                 bg="#161c24", font=("Consolas", 13, "bold")).pack(pady=(0, 16))
        self.ent_key = tk.Entry(card, font=("Consolas", 14), bg="#0a0e13",
                                fg="#39ff14", insertbackground="#39ff14",
                                justify="center", width=32, relief="flat")
        self.ent_key.pack(ipady=10, pady=(0, 18))
        self.btn_ativar = tk.Button(card, text="🔓  ATIVAR", bg="#39ff14",
                  fg="#001a00", font=("Consolas", 12, "bold"), relief="flat",
                  padx=38, pady=11, cursor="hand2", command=self._do_login)
        self.btn_ativar.pack()
        self.lbl_status = tk.Label(card, text="", fg="#7ee7ff", bg="#161c24",
                                   font=("Consolas", 10))
        self.lbl_status.pack(pady=(14, 0))
        tk.Label(f, text=f"Servidor: {API_URL}", fg="#3a4a5a", bg="#0a0e13",
                 font=("Consolas", 9)).pack(side="bottom", pady=6)
        tk.Label(f, text=f"HWID: {self.hwid[:32]}...", fg="#3a4a5a",
                 bg="#0a0e13", font=("Consolas", 9)).pack(side="bottom")

    def _do_login(self):
        key = self.ent_key.get().strip().upper()
        if not key: return
        self.btn_ativar.config(state="disabled")
        self.lbl_status.config(text="⏳ Validando no servidor...", fg="#7ee7ff")
        threading.Thread(target=self._login_worker, args=(key,), daemon=True).start()

    def _login_worker(self, key):
        if self.ip == "...":
            self.ip = get_ip()
        res = api_post("/api/validate", {"key": key, "hwid": self.hwid, "ip": self.ip})
        self.after(0, lambda: self._login_result(key, res))

    def _login_result(self, key, res):
        self.btn_ativar.config(state="normal")
        if not res.get("ok"):
            self.lbl_status.config(text=f"❌ {res.get('msg', 'Falha')}", fg="#ff5d5d")
            return
        self.token_data = (key, res)
        self._show_main()
        self._start_heartbeat()

    def _start_heartbeat(self):
        self._hb_stop = False
        def loop():
            import time
            while not self._hb_stop:
                time.sleep(HEARTBEAT_MIN * 60)
                if self._hb_stop: return
                key = self.token_data[0]
                res = api_post("/api/validate", {"key": key, "hwid": self.hwid, "ip": self.ip})
                if not res.get("ok"):
                    self.after(0, lambda r=res: messagebox.showerror(
                        "Sessão encerrada", r.get("msg", "Key inválida")))
                    self.after(0, self._show_login)
                    return
        threading.Thread(target=loop, daemon=True).start()

    def _show_main(self):
        self._clear()
        key, data = self.token_data
        head = tk.Frame(self, bg="#0a0e13"); head.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(head, text="⚡ OT PLUS v3", fg="#39ff14", bg="#0a0e13",
                 font=("Consolas", 20, "bold")).pack(side="left")
        tk.Label(head, text=f"  •  {key}", fg="#7ee7ff", bg="#0a0e13",
                 font=("Consolas", 10)).pack(side="left", pady=(8, 0))
        tk.Label(head, text=f"  •  {data.get('days_left',0)} dias restantes",
                 fg="#ffd700", bg="#0a0e13", font=("Consolas", 10)).pack(side="left", pady=(8, 0))

        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=14, pady=6)
        self.vars = {}
        total = 0
        for cat, items in TAREFAS.items():
            fr = tk.Frame(nb, bg="#0a0e13"); nb.add(fr, text=cat)
            for i, (lbl, _) in enumerate(items):
                v = tk.BooleanVar(value=True); self.vars[lbl] = v; total += 1
                ttk.Checkbutton(fr, text=lbl, variable=v).grid(
                    row=i//3, column=i%3, sticky="w", padx=8, pady=3)

        tk.Label(self, text=f"📊 {total} otimizações disponíveis",
                 fg="#7ee7ff", bg="#0a0e13", font=("Consolas", 10, "bold")
                 ).pack(anchor="w", padx=18)

        btns = tk.Frame(self, bg="#0a0e13"); btns.pack(fill="x", padx=14, pady=(4, 6))
        self.btn_run = tk.Button(btns, text="🚀 OTIMIZAR AGORA", bg="#39ff14",
                                 fg="#001a00", font=("Consolas", 12, "bold"),
                                 relief="flat", padx=22, pady=10, cursor="hand2",
                                 command=self._start)
        self.btn_run.pack(side="left")
        tk.Button(btns, text="↺ Tudo", bg="#161c24", fg="#7ee7ff",
                  font=("Consolas", 10, "bold"), relief="flat", padx=12, pady=10,
                  cursor="hand2", command=lambda: [v.set(True) for v in self.vars.values()]
                  ).pack(side="left", padx=6)
        tk.Button(btns, text="✗ Nada", bg="#161c24", fg="#ff5d5d",
                  font=("Consolas", 10, "bold"), relief="flat", padx=12, pady=10,
                  cursor="hand2", command=lambda: [v.set(False) for v in self.vars.values()]
                  ).pack(side="left")

        self.pbar = ttk.Progressbar(self, mode="determinate")
        self.pbar.pack(fill="x", padx=14, pady=(4, 4))
        self.log = scrolledtext.ScrolledText(self, bg="#05080c", fg="#39ff14",
                                             insertbackground="#39ff14",
                                             font=("Consolas", 9), relief="flat", height=10)
        self.log.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self._say("OT PLUS v3 pronto ✅")
        self._say(f"IP: {self.ip} | HWID: {self.hwid[:16]}...")
        self._say(f"{'Admin ✅' if is_admin() else '⚠ Rode como administrador!'}")

    def _say(self, m):
        self.log.insert("end", m + "\n"); self.log.see("end")

    def _start(self):
        sel = [(l, c) for cat in TAREFAS.values() for (l, c) in cat if self.vars[l].get()]
        if not sel:
            messagebox.showinfo("Nada", "Marque algo."); return
        if not messagebox.askyesno("Confirmar", f"Executar {len(sel)} tarefas?\n\nAlgumas demoram (SFC/DISM)."): return
        self.btn_run.config(state="disabled")
        self.pbar["maximum"] = len(sel); self.pbar["value"] = 0
        threading.Thread(target=self._worker, args=(sel,), daemon=True).start()

    def _worker(self, sel):
        ok = fail = 0
        for i, (l, c) in enumerate(sel, 1):
            self._say(f"[{i}/{len(sel)}] ▶ {l}")
            code, out = run(c)
            if code == 0: ok += 1; self._say("   ✅ OK")
            else: fail += 1; self._say(f"   ⚠ {out.strip()[:150]}")
            self.after(0, lambda v=i: self.pbar.configure(value=v))
        self._say(f"\n🏁 Finalizado — OK: {ok} | Falhas: {fail}")
        self._say("💡 Reinicie o PC.\n")
        self.after(0, lambda: self.btn_run.config(state="normal"))
        self.after(0, lambda: messagebox.showinfo("Pronto", f"✅ {ok} | ⚠ {fail}"))


if __name__ == "__main__":
    if os.name != "nt":
        print("Windows only"); sys.exit(1)
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable,
                                            " ".join(sys.argv), None, 1)
        sys.exit(0)
    App().mainloop()