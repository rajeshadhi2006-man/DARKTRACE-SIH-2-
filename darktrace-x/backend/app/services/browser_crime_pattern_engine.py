"""
DARKTRACE-X // Forensic Browser Crime Pattern Intelligence Engine
Exhaustive catalog and classification of 80+ desktop, mobile, privacy, open-source,
enterprise, historical, and developer browsers mapped to cybercrime behavioral patterns,
OPSEC failure detection, and threat actor de-anonymization vectors.
"""
import re
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

# ==============================================================================
# MASTER BROWSER CRIME PATTERN REGISTRY
# ==============================================================================

BROWSER_REGISTRY: List[Dict[str, Any]] = [
    # --------------------------------------------------------------------------
    # 1. MAJOR DESKTOP / MOBILE BROWSERS
    # --------------------------------------------------------------------------
    {
        "id": "google_chrome",
        "name": "Google Chrome",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile", "Apple ecosystem"],
        "engine": "Blink / V8",
        "regex": r"(?<!Edg/)(?<!OPR/)(?<!Vivaldi/)(?<!Brave/)(?<!YaBrowser/)(?<!Chrome Canary)Chrome/(?!.*(Mobile/|Android))(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Fatal OPSEC leak when accessing dark web staging mirrors or illicit drop zones. Suspect utilized default clearnet browser exposing hardware IDs.",
        "opsec_vulnerabilities": "Rich Sec-CH-UA Client Hints, WebRTC candidate enumeration exposes LAN/WAN IP interfaces, granular Canvas/WebGL hardware signature.",
        "deanon_vectors": ["WebRTC STUN traversal", "Client Hints hardware platform disclosure", "Google sync profile tokens", "Canvas noise fingerprinting"],
        "typical_crime_contexts": ["Accidental clearnet access to hidden services", "Carding panel login without proxy", "Phishing kit staging administration"]
    },
    {
        "id": "mozilla_firefox",
        "name": "Mozilla Firefox",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile", "Apple ecosystem"],
        "engine": "Gecko",
        "regex": r"Firefox/(?!.*(Mobile|Android|Nightly|Focus|ESR|LibreWolf|Waterfox|Floorp))(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Standard Gecko browser without Tor privacy hardening. Often configured with manual SOCKS5 proxies by novice operators, leaking DNS queries.",
        "opsec_vulnerabilities": "Remote DNS resolution bypass if SOCKS5 proxy lacks socks5h:// protocol, exposed system font list, audio context fingerprinting.",
        "deanon_vectors": ["DNS leak over UDP", "AudioBuffer latency profiling", "Font enumeration fingerprinting"],
        "typical_crime_contexts": ["Manual SOCKS proxy browsing", "Darknet forum scraping", "Telegram web session hijack"]
    },
    {
        "id": "microsoft_edge",
        "name": "Microsoft Edge",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile", "Apple ecosystem", "Enterprise / specialized"],
        "engine": "Blink / EdgeHTML",
        "regex": r"Edg/(?!.*(Canary|Dev|Beta))(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Default corporate OS browser. High probability of insider threat or infected enterprise endpoint used as a pivot point for data exfiltration.",
        "opsec_vulnerabilities": "SmartScreen telemetry headers, Microsoft telemetry device identifier, Active Directory Kerberos token pass-through.",
        "deanon_vectors": ["SmartScreen hash inspection", "Windows Defender telemetry correlation", "Enterprise tenant ID discovery"],
        "typical_crime_contexts": ["Corporate espionage", "Internal data exfiltration", "Ransomware reconnaissance"]
    },
    {
        "id": "apple_safari",
        "name": "Apple Safari",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile", "Apple ecosystem"],
        "engine": "WebKit",
        "regex": r"Version/(?:\d+).*Safari/(?:\d+)(?!.*(Chrome|Chromium|Edg|OPR|Brave))",
        "sample_ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "macOS / iOS native browsing. Apple Private Relay may mask egress IP, but WebKit canvas and audio rendering create highly unique host fingerprints.",
        "opsec_vulnerabilities": "Metal API GPU shader rendering characteristics, Apple iCloud Private Relay egress IP blocks, system font smoothing.",
        "deanon_vectors": ["Metal WebGL renderer hashing", "iCloud relay egress mapping", "macOS CoreText font metric profiling"],
        "typical_crime_contexts": ["High-value crypto theft", "Sim swapping coordination on macOS", "VIP targeted social engineering"]
    },
    {
        "id": "opera",
        "name": "Opera",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile", "Apple ecosystem"],
        "engine": "Blink",
        "regex": r"OPR/(?!.*(GX|Developer))(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/111.0.0.0",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Built-in free proxy VPN frequently abused by low-tier cybercriminals under the false belief that it provides bulletproof darknet anonymity.",
        "opsec_vulnerabilities": "Opera proxy egress IP ranges are well cataloged and log-compliant under subpoena, WebRTC leaks true client IP behind proxy.",
        "deanon_vectors": ["Opera Proxy egress infrastructure attribution", "WebRTC STUN interface leak", "Telemetry device UUID"],
        "typical_crime_contexts": ["Low-level credential stuffing", "Stolen credit card testing", "DDoS booter panel control"]
    },
    {
        "id": "opera_gx",
        "name": "Opera GX",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile"],
        "engine": "Blink",
        "regex": r"OPR/(?:\d+).*Opera GX|OPX/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0 (Edition GX)",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Gaming-oriented browser heavily prevalent among juvenile threat actors, Discord-based RAT operators, and swatting / SIM swap gangs.",
        "opsec_vulnerabilities": "Extensive custom audio and Discord rich presence integration hooks, GPU hardware limiter telemetry leaks.",
        "deanon_vectors": ["Discord RPC connection inspection", "Twitch/Discord token cross-referencing", "Hardware concurrency profiling"],
        "typical_crime_contexts": ["Discord malware syndicates", "Minecraft/Roblox account drainers", "Swatting-as-a-service"]
    },
    {
        "id": "brave",
        "name": "Brave",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile", "Privacy/security-focused", "Apple ecosystem", "Android-focused"],
        "engine": "Blink",
        "regex": r"Brave/(?:\d+)|Chrome/.*(?=.*Brave)|brave_fingerprint",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Brave/126.0.0.0",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Privacy browser with built-in Tor tabs and ad-blocking used by mid-tier threat actors for cryptocurrency management and forum trading.",
        "opsec_vulnerabilities": "Farbling introduces pseudo-random noise to canvas, but the farbling seed can be reverse-correlated within the same browsing session.",
        "deanon_vectors": ["Farbling seed noise correlation", "Brave Rewards crypto wallet link", "Chromium component updater IP logs"],
        "typical_crime_contexts": ["Crypto drainer development", "Darknet escrow trading", "Counterfeit currency exchange"]
    },
    {
        "id": "vivaldi",
        "name": "Vivaldi",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile", "Android-focused"],
        "engine": "Blink",
        "regex": r"Vivaldi/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Vivaldi/6.8.3381.46",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Highly customized power-user browser. Advanced window and tab configuration creates a statistically unique client footprint.",
        "opsec_vulnerabilities": "Unique custom UI dimensions and panel layouts alter window.outerWidth/Height ratios, distinct extension ecosystem.",
        "deanon_vectors": ["Viewport aspect-ratio uniqueness", "Client panel metrics", "Vivaldi community account sync"],
        "typical_crime_contexts": ["Dark web intelligence monitoring", "Underground market shopping", "Multi-account forum management"]
    },
    {
        "id": "arc",
        "name": "Arc",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile"],
        "engine": "Blink",
        "regex": r"Arc/(?:\d+)|Chrome/.*Arc",
        "sample_ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Arc/1.45.0",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Modern cloud-synced Chromium browser. Used by tech-savvy attackers; relies on cloud spaces which generate identifiable centralized synchronization metadata.",
        "opsec_vulnerabilities": "Arc sync backend connectivity, sidebar layout dimensions, WebKit/Chromium hybrid signatures on macOS.",
        "deanon_vectors": ["Arc cloud sync endpoint traffic", "Custom Easel/Space metadata", "macOS window server hooks"],
        "typical_crime_contexts": ["Cloud infrastructure compromises", "API key harvesting", "SaaS token theft"]
    },
    {
        "id": "zen_browser",
        "name": "Zen Browser",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile", "Privacy/security-focused"],
        "engine": "Gecko",
        "regex": r"Zen/(?:\d+)|Firefox/.*Zen",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Zen/1.0.0-a.30",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Emerging privacy-focused vertical-tab Gecko browser. Used by modern privacy hobbyists and underground actors moving away from Chrome.",
        "opsec_vulnerabilities": "Gecko-based compact letterboxing variations, custom CSS layout properties leaked via window metrics.",
        "deanon_vectors": ["Zen custom profile structure", "Gecko vertical-tab viewport offsets", "Release version delta tracking"],
        "typical_crime_contexts": ["Underground coding communities", "Exploit sharing", "Zero-day broker discussions"]
    },
    {
        "id": "duckduckgo_browser",
        "name": "DuckDuckGo Browser",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile", "Privacy/security-focused", "Apple ecosystem", "Android-focused"],
        "engine": "WebView / WebKit / Blink",
        "regex": r"DuckDuckGo/(?:\d+)|DDG/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 DuckDuckGo/7 Safari/605.1.15",
        "risk_tier": "MODERATE_EVASION_SIGNAL",
        "crime_behavior": "Consumer privacy browser. Automatically blocks 3rd-party trackers and wipes sessions; utilized for single-use reconnaissance runs.",
        "opsec_vulnerabilities": "Smokescreen tracker-blocking headers produce a distinct fingerprint of blocked vs allowed script assets.",
        "deanon_vectors": ["Smokescreen tracker filter list probing", "WebView system-level font leak", "Fire button clearing timing anomalies"],
        "typical_crime_contexts": ["OSINT reconnaissance on targets", "Doxing investigations", "Initial victim discovery"]
    },
    {
        "id": "tor_browser",
        "name": "Tor Browser",
        "primary_category": "Privacy/security-focused",
        "categories": ["Major desktop/mobile", "Privacy/security-focused"],
        "engine": "Gecko (Tor Hardened)",
        "regex": r"rv:1(?:28|15)\.0.*Gecko/20100101 Firefox/1(?:28|15)\.0",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "The gold standard of darknet criminal operations. Deployed by drug market vendors, ransomware negotiators, and weapon distributors.",
        "opsec_vulnerabilities": "Letterboxing modulo 200x100 viewport, UTC timezone lock, disabled WebRTC. Fatal flaw: If actor changes window size or enables JavaScript, unique fingerprint created.",
        "deanon_vectors": ["Window resizing canvas measurement", "Tor Circuit correlation via consensus clocks", "Circuit end-to-end traffic timing analysis"],
        "typical_crime_contexts": ["Darknet market administration", "Ransomware negotiation chat portals", "State-sponsored whistleblower targeting"]
    },
    {
        "id": "mullvad_browser",
        "name": "Mullvad Browser",
        "primary_category": "Privacy/security-focused",
        "categories": ["Major desktop/mobile", "Privacy/security-focused"],
        "engine": "Gecko (Mullvad Hardened)",
        "regex": r"MullvadBrowser/(?:\d+)|rv:128\.0.*Mullvad",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0 MullvadBrowser/13.5",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Tor Browser technology without the Tor network (designed for high-tier VPN routing). Common among sophisticated financial fraudsters avoiding Tor exit node blocks.",
        "opsec_vulnerabilities": "Matches Tor Browser fingerprint in DOM/Letterboxing, but egresses through clearnet commercial VPN IPs rather than onion relays.",
        "deanon_vectors": ["VPN wireguard IP handshake", "Letterboxing over clearnet correlation", "Payment correlation with Mullvad vouchers"],
        "typical_crime_contexts": ["Bank wire fraud", "Stolen credit card cashing", "Crypto tumbling operations"]
    },
    {
        "id": "waterfox",
        "name": "Waterfox",
        "primary_category": "Privacy/security-focused",
        "categories": ["Major desktop/mobile", "Privacy/security-focused"],
        "engine": "Gecko",
        "regex": r"Waterfox/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0 Waterfox/6.0.14",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Independent Gecko fork supporting legacy NPAPI / XUL plugins. Frequently utilized to interact with legacy banking malware command panels.",
        "opsec_vulnerabilities": "Legacy plugin execution capabilities leave distinctive DOM footprints; outdated Gecko engine versions expose unpatched CVEs.",
        "deanon_vectors": ["Legacy plugin enum (Java/Silverlight)", "Outdated Gecko vulnerability probing", "User-Agent token leakage"],
        "typical_crime_contexts": ["Legacy banking trojan C2 operations", "Retro exploit kit hosting", "Archived leak exploration"]
    },
    {
        "id": "librewolf",
        "name": "LibreWolf",
        "primary_category": "Privacy/security-focused",
        "categories": ["Major desktop/mobile", "Privacy/security-focused"],
        "engine": "Gecko",
        "regex": r"LibreWolf/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0 LibreWolf/127.0",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Stripped, privacy-hardened Firefox build with telemetry completely disabled. Used by privacy purists and operational security consultants in cybercrime groups.",
        "opsec_vulnerabilities": "Strict RFP (Resist Fingerprinting) mode spoofing common resolutions and timezone to UTC; easily isolated as LibreWolf due to specific canvas readback noise.",
        "deanon_vectors": ["RFP canvas noise signature", "Absence of Google/Mozilla safe browsing queries", "WebGL masked vendor string"],
        "typical_crime_contexts": ["Cybercrime infrastructure provisioning", "Bulletproof hosting administration", "Encrypted communication relay"]
    },
    {
        "id": "pale_moon",
        "name": "Pale Moon",
        "primary_category": "Privacy/security-focused",
        "categories": ["Major desktop/mobile", "Privacy/security-focused"],
        "engine": "Goanna (Gecko Fork)",
        "regex": r"PaleMoon/(?:\d+)|Goanna/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Goanna/6.6 PaleMoon/33.1.0",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Goanna layout engine browser. Highly anomalous in 2026; immediately identifies the user as an eccentric technical operator or legacy malware distributor.",
        "opsec_vulnerabilities": "Distinctive Goanna rendering engine flaws and non-standard ECMAScript implementations create a mathematically unique fingerprint.",
        "deanon_vectors": ["Goanna JavaScript engine feature matrix", "Non-standard DOM prototypes", "HTTP header ordering anomaly"],
        "typical_crime_contexts": ["Phreaking / legacy telecommunications fraud", "Specialized botnet management", "Underground exploit archives"]
    },
    {
        "id": "seamonkey",
        "name": "SeaMonkey",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile"],
        "engine": "Gecko",
        "regex": r"SeaMonkey/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0 SeaMonkey/2.53.18",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "All-in-one Internet suite (browser, email, newsgroup, IRC). Often observed in old-school IRC carding networks and automated usenet scrapers.",
        "opsec_vulnerabilities": "Integrated IRC/mail clients frequently leak system username and hostname via default HELO / client handshake.",
        "deanon_vectors": ["Integrated mailer HELO/EHLO hostname leaks", "IRC identity crossover", "Ancient Gecko layout metrics"],
        "typical_crime_contexts": ["IRC cybercrime syndicates", "Usenet dump harvesting", "Legacy spam bot deployment"]
    },
    {
        "id": "floorp",
        "name": "Floorp",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile"],
        "engine": "Gecko",
        "regex": r"Floorp/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0 Floorp/11.14.0",
        "risk_tier": "MODERATE_EVASION_SIGNAL",
        "crime_behavior": "Japanese open-source Firefox fork with high UI customizability. Observed among East Asian threat actors and cyber-syndicates.",
        "opsec_vulnerabilities": "Custom Floorp navigator extensions and unique split-screen layout dimensions.",
        "deanon_vectors": ["Floorp API properties", "Regional language preference headers", "Custom split-view aspect ratio"],
        "typical_crime_contexts": ["East Asian underground market trading", "Manga/content piracy rings", "Cryptocurrency phishing"]
    },
    {
        "id": "orion",
        "name": "Orion",
        "primary_category": "Apple ecosystem",
        "categories": ["Major desktop/mobile", "Apple ecosystem"],
        "engine": "WebKit",
        "regex": r"Orion/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15 Orion/0.99.127",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "WebKit browser on macOS with native Chrome and Firefox extension support. Used by advanced Apple-based security researchers and threat actors.",
        "opsec_vulnerabilities": "Hybrid WebKit rendering combined with Chromium extension storage APIs creates an extremely rare, easily trackable footprint.",
        "deanon_vectors": ["WebKit DOM with Chrome.runtime API coexistence", "macOS keychain integration", "Zero telemetry filter signature"],
        "typical_crime_contexts": ["Targeted iOS/macOS exploit testing", "High-tier crypto wallet draining", "Executive spear-phishing"]
    },
    {
        "id": "yandex_browser",
        "name": "Yandex Browser",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile"],
        "engine": "Blink",
        "regex": r"YaBrowser/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.4.1.912 Yowser/2.5 Safari/537.36",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Russian Chromium browser. Extremely common in Russian underground forums (XSS, Exploit.in, RAMP) when actors fail to route through isolated VMs.",
        "opsec_vulnerabilities": "Deep Yandex Passport authentication tokens, Alice voice assistant telemetry, Russian ISP DNS resolution traces.",
        "deanon_vectors": ["Yandex UID cookies", "Yandex Cloud telemetry beaconing", "Cyrillic primary language headers"],
        "typical_crime_contexts": ["Russian-speaking cybercrime forums", "Ransomware affiliate coordination", "Initial access broker negotiations"]
    },
    {
        "id": "samsung_internet",
        "name": "Samsung Internet",
        "primary_category": "Android-focused",
        "categories": ["Major desktop/mobile", "Android-focused"],
        "engine": "Blink",
        "regex": r"SamsungBrowser/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 14; SAMSUNG SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.6167.101 Mobile Safari/537.36",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Pre-installed Android browser on Samsung hardware. Indicates direct physical mobile device usage by the suspect rather than an isolated forensic VM.",
        "opsec_vulnerabilities": "Exposes exact Samsung hardware build model (e.g. SM-S928B Galaxy S24 Ultra), Android OS version, battery status API, Knox Knox-attestation flags.",
        "deanon_vectors": ["Exact mobile hardware model correlation", "Battery Status API depletion tracing", "Cellular carrier APN headers"],
        "typical_crime_contexts": ["Mobile banking malware smishing", "SIM swap OTP capture", "WhatsApp / Telegram fraud coordination"]
    },
    {
        "id": "uc_browser",
        "name": "UC Browser",
        "primary_category": "Android-focused",
        "categories": ["Major desktop/mobile", "Android-focused"],
        "engine": "U4 / Blink",
        "regex": r"UCBrowser/(?:\d+)|UCWEB",
        "sample_ua": "Mozilla/5.0 (Linux; U; Android 13; en-US; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/100.0.4896.58 UCBrowser/13.4.0.1306 Mobile Safari/537.36",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Alibaba-owned mobile browser popular in South Asia and Southeast Asia. Heavy cloud data compression proxies route through Alibaba servers.",
        "opsec_vulnerabilities": "UC proxy servers inject carrier headers, IMSI/IMEI-derived identifiers, and geo-location coordinates into HTTP headers.",
        "deanon_vectors": ["UC Cloud acceleration proxy logs", "Leaked cellular network identifiers", "Geo-targeted ad injection tokens"],
        "typical_crime_contexts": ["Mule account laundering in South Asia", "Fake loan app syndicates", "Pig butchering scam call centers"]
    },
    {
        "id": "qq_browser",
        "name": "QQ Browser",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile"],
        "engine": "Blink / Trident",
        "regex": r"MQQBrowser/(?:\d+)|QQBrowser/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36 QQBrowser/11.5.5240.400",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Tencent-developed browser prevalent in Chinese cyber operations, APT activity, and gambling syndicates.",
        "opsec_vulnerabilities": "Tencent QQ OpenID tokens, Chinese domestic CDN tracking, client machine GUID broadcast in telemetry packets.",
        "deanon_vectors": ["QQ numerical user identifier leaks", "Tencent cloud telemetry logs", "Chinese system codepage encoding"],
        "typical_crime_contexts": ["Chinese APT espionage staging", "Underground gambling platform ops", "Telecommunications fraud syndicates"]
    },
    {
        "id": "baidu_browser",
        "name": "Baidu Browser",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile"],
        "engine": "Blink / T5",
        "regex": r"BaiduBrowser/(?:\d+)|baidubrowser|BaiduHD",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 BaiduBrowser/4.3.0.0",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Baidu search-integrated client. Associated with Chinese domestic fraud rings and gray-hat crawler infrastructure.",
        "opsec_vulnerabilities": "Baidu ctid hardware fingerprinting, unencrypted coordinate broadcasts in early versions.",
        "deanon_vectors": ["Baidu Baiduid cookie tracking", "GPS coordinate cache leaks", "Hardware MAC address broadcast in legacy builds"],
        "typical_crime_contexts": ["Search engine poisoning campaigns", "Phishing traffic redirection", "Blackhat SEO networks"]
    },
    {
        "id": "huawei_browser",
        "name": "Huawei Browser",
        "primary_category": "Android-focused",
        "categories": ["Major desktop/mobile", "Android-focused"],
        "engine": "Blink",
        "regex": r"HuaweiBrowser/(?:\d+)|HUAWEI/.*Browser",
        "sample_ua": "Mozilla/5.0 (Linux; Android 12; HarmonyOS; NOH-AN00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 HuaweiBrowser/14.0.5.302 Mobile Safari/537.36",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "HarmonyOS native client. Directly indicates a physical Huawei smartphone without Google Mobile Services.",
        "opsec_vulnerabilities": "HMS (Huawei Mobile Services) push tokens, device serial hashes, HarmonyOS operating system flags.",
        "deanon_vectors": ["Huawei HMS device identifier", "HarmonyOS build signature", "Regional carrier network headers"],
        "typical_crime_contexts": ["Mobile botnet staging", "Foreign exchange scam apps", "State-nexus grey infrastructure"]
    },
    {
        "id": "avast_secure_browser",
        "name": "Avast Secure Browser",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile"],
        "engine": "Blink",
        "regex": r"Avast/(?:\d+)|AvastSecureBrowser",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Avast/124.0.0.0",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Chromium fork bundled with Avast Antivirus. Novice threat actors mistakenly use it believing an antivirus company's browser hides their malicious activity.",
        "opsec_vulnerabilities": "Avast backend analytics ping back telemetry on every visited host, providing third-party server logs of the threat actor's browsing.",
        "deanon_vectors": ["Avast Cloud telemetry correlation", "License / Installation GUID", "Anti-fingerprint header anomalies"],
        "typical_crime_contexts": ["Novice cybercrime operations", "Malicious forum browsing", "Amateur malware acquisition"]
    },
    {
        "id": "avg_secure_browser",
        "name": "AVG Secure Browser",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile"],
        "engine": "Blink",
        "regex": r"AVG/(?:\d+)|AVGSecureBrowser",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 AVG/124.0.0.0",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Clone of Avast Secure Browser under the AVG brand. Shares identical telemetry and cloud DNS logging infrastructure.",
        "opsec_vulnerabilities": "Continuous telemetry beaconing to Gen Digital security cloud, fixed extension IDs.",
        "deanon_vectors": ["Gen Digital security telemetry records", "Unique extension pairing ID", "Default proxy bypass"],
        "typical_crime_contexts": ["Carding attempts", "Fake tech support operations", "Cracked software distribution"]
    },
    {
        "id": "aloha_browser",
        "name": "Aloha Browser",
        "primary_category": "Android-focused",
        "categories": ["Major desktop/mobile", "Android-focused", "Apple ecosystem"],
        "engine": "Blink / WebKit",
        "regex": r"AlohaBrowser/(?:\d+)|Aloha/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 AlohaBrowser/5.6.2",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Mobile browser featuring integrated free unlimited VPN and crypto wallet. Extensively used in illicit media distribution, carding, and Telegram scams.",
        "opsec_vulnerabilities": "Built-in Aloha VPN endpoint IPs are shared across thousands of users; however, WebRTC and WebGL hardware parameters remain unmasked.",
        "deanon_vectors": ["Aloha VPN exit cluster matching", "Unmasked mobile GPU WebGL string", "Integrated Aloha crypto wallet address inspection"],
        "typical_crime_contexts": ["Dark web mobile piracy", "Illicit image trading", "Cryptocurrency scam distribution"]
    },
    {
        "id": "kiwi_browser",
        "name": "Kiwi Browser",
        "primary_category": "Android-focused",
        "categories": ["Major desktop/mobile", "Android-focused"],
        "engine": "Blink",
        "regex": r"Kiwi Chrome/(?:\d+)|Kiwi/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 14; 2201123G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36 Kiwi Chrome/124.0.6367.82",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Android browser with full desktop Chrome extension support. Top weapon of mobile carders using cookie injectors, anti-detect extensions, and auto-fill scripts.",
        "opsec_vulnerabilities": "Extension IDs injected into the DOM (e.g. MetaMask, Cookie-Editor, Violentmonkey) leak the exact attack toolkit of the mobile criminal.",
        "deanon_vectors": ["DOM extension asset probing (web_accessible_resources)", "Android device hardware model disclosure", "Canvas fingerprint from mobile Adreno/Mali GPU"],
        "typical_crime_contexts": ["Mobile session hijacking", "Cookie injection fraud", "Automated mobile checkout bots"]
    },
    {
        "id": "via_browser",
        "name": "Via Browser",
        "primary_category": "Android-focused",
        "categories": ["Major desktop/mobile", "Android-focused"],
        "engine": "Android WebView",
        "regex": r"Via/(?:\d+)|ViaBrowser",
        "sample_ua": "Mozilla/5.0 (Linux; Android 13; M2012K11AC Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36 Via/5.2.1",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Ultra-lightweight (<2MB) Android browser. Deployed in burner phones, automated ADB click-fraud farms, and throwaway mobile operations.",
        "opsec_vulnerabilities": "Via identifier token in User-Agent, Android WebView security quirks, leaks underlying Android OS build fingerprint.",
        "deanon_vectors": ["Android WebView build string", "Hardware screen density metric", "Click-fraud automation timing pattern"],
        "typical_crime_contexts": ["Ad-click fraud farms", "Burner phone darknet operations", "SMS stealer landing access"]
    },
    {
        "id": "dolphin_browser",
        "name": "Dolphin Browser",
        "primary_category": "Android-focused",
        "categories": ["Major desktop/mobile", "Android-focused"],
        "engine": "WebKit / Dolphin Engine",
        "regex": r"DolphinBrowser/(?:\d+)|Dolfin/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; U; Android 11; en-US; SM-G988B) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/2.3.4.15 DolphinBrowser/12.2.9 Mobile Safari/534.30",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Pioneering gesture-based mobile browser. Now mostly legacy; presence indicates outdated burner hardware or automated emulators.",
        "opsec_vulnerabilities": "Historical plaintext search query broadcast vulnerabilities, legacy WebKit DOM quirks.",
        "deanon_vectors": ["Legacy WebKit rendering engine discrepancies", "Unencrypted network broadcast traces", "Emulator artifact detection"],
        "typical_crime_contexts": ["Legacy Android botnets", "Emulator-based referral fraud", "Old burner device operations"]
    },
    {
        "id": "puffin_browser",
        "name": "Puffin Browser",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile"],
        "engine": "Cloud-based Blink",
        "regex": r"Puffin/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Puffin/9.7.2.51367AP",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Cloud-rendering browser executing on remote US/Singapore servers. Abused to bypass local firewalls and geo-restrictions.",
        "opsec_vulnerabilities": "Puffin cloud servers inject client IP forwarding headers (`X-Forwarded-For`), immediately unmasking the threat actor's real origin IP.",
        "deanon_vectors": ["X-Forwarded-For origin IP header leak", "Cloudmosa data center subnet correlation", "Client WebSocket handshake timing"],
        "typical_crime_contexts": ["Bypassing government school/office blocks", "Evading geo-blocked phishing targets", "Web scraping without local proxy"]
    },
    {
        "id": "ecosia_browser",
        "name": "Ecosia Browser",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile"],
        "engine": "Blink",
        "regex": r"Ecosia/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 Ecosia/120.0.0.0",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Green-initiative Chromium browser. Rare in cybercrime; typically indicates decoy browsing or an inadvertent clearnet search by an operative.",
        "opsec_vulnerabilities": "Default Chromium telemetry and search suggestion auto-complete requests sent to Ecosia/Bing backends.",
        "deanon_vectors": ["Ecosia/Bing search request metadata", "Standard Chromium hardware hints", "Local cache timestamp correlation"],
        "typical_crime_contexts": ["Decoy background browsing", "Casual threat actor browsing", "OSINT discovery"]
    },
    {
        "id": "arc_search",
        "name": "Arc Search",
        "primary_category": "Major desktop/mobile",
        "categories": ["Major desktop/mobile", "Apple ecosystem"],
        "engine": "WebKit",
        "regex": r"ArcSearch/(?:\d+)|ArcMobile/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ArcSearch/1.12.0",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "AI-powered mobile search browser by The Browser Company. Uses 'Browse for Me' AI web scrapers which trigger distinct automated query patterns.",
        "opsec_vulnerabilities": "AI proxy fetching headers from Arc cloud infrastructure, iOS device viewport parameters.",
        "deanon_vectors": ["Arc cloud AI synthesis IP addresses", "iPhone hardware viewport metrics", "Cloud sync UUID headers"],
        "typical_crime_contexts": ["Target automated intelligence gathering", "Quick mobile OSINT", "Modern social engineering"]
    },
    {
        "id": "firefox_focus",
        "name": "Firefox Focus",
        "primary_category": "Privacy/security-focused",
        "categories": ["Major desktop/mobile", "Privacy/security-focused", "Android-focused", "Apple ecosystem"],
        "engine": "GeckoView / WebKit",
        "regex": r"Focus/(?:\d+)|Klar/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36 Focus/125.0",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Dedicated single-tab privacy browser with permanent incognito mode and tracker blocking. Used for burner link verification and SMS phishing inspection.",
        "opsec_vulnerabilities": "Absence of cookies and storage is itself a distinct anomaly. Android GeckoView or iOS WebKit engine quirks reveal underlying OS.",
        "deanon_vectors": ["Sessionless zero-storage behavioral profile", "Aggressive tracker block fingerprint", "Mobile viewport dimensions"],
        "typical_crime_contexts": ["Checking phishing landing page health", "Single-use SMS payload verification", "Burner crypto invoice checking"]
    },
    {
        "id": "edge_canary",
        "name": "Microsoft Edge Canary",
        "primary_category": "Developer / testing browsers",
        "categories": ["Major desktop/mobile", "Developer / testing browsers"],
        "engine": "Blink",
        "regex": r"EdgA?/(?:\d+).*(?:Canary|Edg/(?:1[3-9]\d|2\d\d))",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.2680.0 Canary",
        "risk_tier": "DEV_MALWARE_AUTHOR_STAGING",
        "crime_behavior": "Bleeding-edge daily Microsoft test build. Highly correlated with exploit developers and zero-day researchers testing V8 browser sandbox escapes.",
        "opsec_vulnerabilities": "Canary version numbers update daily, pinpointing the exact machine state and compilation timestamp of the attacker's workstation.",
        "deanon_vectors": ["Daily build version increment tracking", "V8 experimental flag detection", "Microsoft telemetry crash dumps"],
        "typical_crime_contexts": ["Browser sandbox escape research (V8 exploits)", "Zero-day vulnerability weaponization", "Pre-release exploit testing"]
    },
    {
        "id": "chrome_canary",
        "name": "Chrome Canary",
        "primary_category": "Developer / testing browsers",
        "categories": ["Major desktop/mobile", "Developer / testing browsers"],
        "engine": "Blink",
        "regex": r"Chrome/(?:1[3-9]\d|2\d\d)\..*Safari.*Canary|Chrome/.*Canary",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6630.0 Safari/537.36 Canary",
        "risk_tier": "DEV_MALWARE_AUTHOR_STAGING",
        "crime_behavior": "Nightly Google build used by exploit writers developing V8 JIT compiler bugs and WebAssembly zero-days.",
        "opsec_vulnerabilities": "Daily build sub-version string gives forensic investigators a 24-hour window of when the attacker compiled or installed their browser.",
        "deanon_vectors": ["Exact 24h build string correlation", "V8 experimental JIT engine features", "Unstripped developer debugging hooks"],
        "typical_crime_contexts": ["V8 JIT exploit development", "WebAssembly shellcode delivery", "Darknet zero-day sales proofs"]
    },
    {
        "id": "chrome_beta",
        "name": "Chrome Beta",
        "primary_category": "Developer / testing browsers",
        "categories": ["Major desktop/mobile", "Developer / testing browsers"],
        "engine": "Blink",
        "regex": r"Chrome/(?:\d+\.\d+\.\d+\.\d+).*Beta",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.17 Safari/537.36 Beta",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Preview build 1 month ahead of stable. Threat actors verify that their exploit or phishing kit will not be broken by upcoming Chrome updates.",
        "opsec_vulnerabilities": "Beta build channel header disclosure, Client Hints Sec-CH-UA-Full-Version-List flag.",
        "deanon_vectors": ["Sec-CH-UA full version list", "Beta feature gate test probes", "Google diagnostic crash reports"],
        "typical_crime_contexts": ["Phishing kit compatibility pre-testing", "Malvertising bypass verification", "Exploit longevity testing"]
    },
    {
        "id": "firefox_nightly",
        "name": "Firefox Nightly",
        "primary_category": "Developer / testing browsers",
        "categories": ["Major desktop/mobile", "Developer / testing browsers"],
        "engine": "Gecko",
        "regex": r"Firefox/(?:1[3-9]\d|2\d\d)\.0a1",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0a1",
        "risk_tier": "DEV_MALWARE_AUTHOR_STAGING",
        "crime_behavior": "Daily unstable Mozilla build. Used by security researchers, SpiderMonkey JavaScript engine exploit developers, and darknet tool authors.",
        "opsec_vulnerabilities": "SpiderMonkey experimental features, daily build changeset ID in navigator.buildID exposes exact repository commit.",
        "deanon_vectors": ["navigator.buildID exact commit matching", "SpiderMonkey JIT flags", "Mozilla Telemetry Opt-in IP dumps"],
        "typical_crime_contexts": ["SpiderMonkey engine vulnerability research", "Tor Browser upstream zero-day hunting", "Experimental cyber weapons"]
    },

    # --------------------------------------------------------------------------
    # 2. PRIVACY / SECURITY-FOCUSED BROWSERS
    # --------------------------------------------------------------------------
    {
        "id": "ungoogled_chromium",
        "name": "Ungoogled Chromium",
        "primary_category": "Privacy/security-focused",
        "categories": ["Privacy/security-focused", "Linux / open-source browsers"],
        "engine": "Blink",
        "regex": r"Ungoogled|Chromium/(?:\d+).*Ungoogled",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.126 Safari/537.36 (Ungoogled)",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Chromium with all Google background services, WebRTC STUN dependencies, and binaries removed. Preferred by high-end hackers for clean clearnet tasks.",
        "opsec_vulnerabilities": "Failure to load Google accounts, blocked WebRTC STUN requests, and lack of default Google public DNS fallback create a unique fingerprint.",
        "deanon_vectors": ["Complete absence of Google Web Services traffic", "Custom font metric rendering on Linux", "Manual WebRTC configuration traces"],
        "typical_crime_contexts": ["Initial access broker staging", "Ransomware data leak site maintenance", "Private exploit brokerage"]
    },
    {
        "id": "bromite",
        "name": "Bromite",
        "primary_category": "Privacy/security-focused",
        "categories": ["Privacy/security-focused", "Android-focused"],
        "engine": "Blink",
        "regex": r"Bromite/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.128 Mobile Safari/537.36 Bromite/108.0.5359.128",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Legacy privacy-hardened Android Chromium fork with built-in adblocking and DNS-over-HTTPS. Common among mobile privacy activists and carders.",
        "opsec_vulnerabilities": "Outdated Chromium version string (Bromite development stalled) makes devices running it highly vulnerable to known n-day browser exploits.",
        "deanon_vectors": ["Frozen Chrome 108 user-agent anomaly", "Bromite ad-block filter list syntax", "Hardware canvas fingerprinting on Mali/Adreno"],
        "typical_crime_contexts": ["Mobile carding operations", "Telegram crypto drainers", "Burner device underground communication"]
    },
    {
        "id": "cromite",
        "name": "Cromite",
        "primary_category": "Privacy/security-focused",
        "categories": ["Privacy/security-focused", "Android-focused"],
        "engine": "Blink",
        "regex": r"Cromite/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36 Cromite/126.0.6478.122",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Modern successor to Bromite on Android. Highly popular in mobile underground circles for its anti-fingerprinting and ad-filtering flags.",
        "opsec_vulnerabilities": "Cromite custom anti-fingerprint canvas fuzzing creates a distinct mathematical distribution of random pixel offsets.",
        "deanon_vectors": ["Canvas noise distribution analysis", "WebRTC candidate isolation probing", "Ad-blocking rule telemetry"],
        "typical_crime_contexts": ["Modern Android banking trojan management", "SIM swap escrow operations", "Encrypted underground forum access"]
    },
    {
        "id": "iridium_browser",
        "name": "Iridium Browser",
        "primary_category": "Privacy/security-focused",
        "categories": ["Privacy/security-focused"],
        "engine": "Blink",
        "regex": r"Iridium/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Iridium/2023.11.119",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Open-source privacy browser based on Chromium with hardened defaults. Used in corporate espionage and covert reconnaissance.",
        "opsec_vulnerabilities": "Specific Iridium build release numbers in user-agent and absence of Google component extensions.",
        "deanon_vectors": ["Iridium user-agent token", "Custom TLS cipher suite preference ordering", "Direct DNS query patterns"],
        "typical_crime_contexts": ["Corporate surveillance", "Whistleblower intelligence harvesting", "Covert pen-testing operations"]
    },
    {
        "id": "gnu_icecat",
        "name": "GNU IceCat",
        "primary_category": "Privacy/security-focused",
        "categories": ["Privacy/security-focused", "Linux / open-source browsers"],
        "engine": "Gecko",
        "regex": r"IceCat/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 GNU IceCat/115.3.0",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "GNU Project's free software rebrand of Firefox with LibreJS. Indicates hardline hacktivist ideologues or anti-surveillance militants.",
        "opsec_vulnerabilities": "LibreJS script rejection patterns are visible to web servers (refuses to execute non-free JS), immediately tagging the client.",
        "deanon_vectors": ["LibreJS selective JavaScript execution profile", "GNU IceCat branding string", "Pure free-software font configuration"],
        "typical_crime_contexts": ["Hacktivist group coordination", "Anti-government document dumping", "Encrypted manifesto distribution"]
    },
    {
        "id": "mull_browser",
        "name": "Mull Browser",
        "primary_category": "Privacy/security-focused",
        "categories": ["Privacy/security-focused", "Android-focused"],
        "engine": "Gecko (GeckoView)",
        "regex": r"Mull/(?:\d+)|Android.*rv:1(?:15|28).*Firefox",
        "sample_ua": "Mozilla/5.0 (Android 14; Mobile; rv:128.0) Gecko/128.0 Firefox/128.0 (Mull)",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "F-Droid hardened build of Firefox for Android using arkenfox user.js. Deployed on secure mobile ROMs (GrapheneOS / CalyxOS) by high-level actors.",
        "opsec_vulnerabilities": "Mobile ResistFingerprinting (RFP) spoofing a standard 360x640 screen and UTC timezone while on a mobile carrier network creates an obvious OPSEC contradiction.",
        "deanon_vectors": ["Mobile RFP screen size contradiction", "Carrier cellular latency vs fixed UTC clock", "GeckoView canvas readback noise"],
        "typical_crime_contexts": ["Encrypted cartel messaging coordination", "Ransomware negotiation on burner mobile", "Secure drop management"]
    },
    {
        "id": "vanadium",
        "name": "Vanadium",
        "primary_category": "Privacy/security-focused",
        "categories": ["Privacy/security-focused"],
        "engine": "Blink (Hardened GrapheneOS)",
        "regex": r"Vanadium|Chrome/.*(?=.*GrapheneOS)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Build/UD1A.230803.041; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36 Vanadium",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Default hardened browser of GrapheneOS. Strongest mobile security posture in existence; favored by cybercrime kingpins, elite drug syndicates, and OPSEC elites.",
        "opsec_vulnerabilities": "Disabled JIT compiler and hardened malloc memory allocator can be fingerprinted via micro-benchmark execution timing.",
        "deanon_vectors": ["Hardened memory allocator timing side-channel", "Disabled JIT compilation performance signature", "Strict WebGL disabling flag"],
        "typical_crime_contexts": ["Organized cybercrime leadership", "High-value drug cartel operations", "Zero-day vulnerability trading"]
    },

    # --------------------------------------------------------------------------
    # 3. LINUX / OPEN-SOURCE BROWSERS
    # --------------------------------------------------------------------------
    {
        "id": "chromium",
        "name": "Chromium",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers", "Developer / testing browsers", "Enterprise / specialized"],
        "engine": "Blink",
        "regex": r"Chromium/(?:\d+)(?!.*(Chrome|Edg|OPR|Brave|Vivaldi))",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/126.0.6478.126 Chrome/126.0.6478.126 Safari/537.36",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Default browser on Kali Linux, Parrot OS, and forensic workstations. Frequently indicates attack tools running directly from penetration testing distributions.",
        "opsec_vulnerabilities": "Linux system font packages (e.g. DejaVu Sans, Liberation Mono), X11/Wayland display server quirks, lack of proprietary H.264 codecs.",
        "deanon_vectors": ["Kali/Parrot Linux default font list", "X11 screen coordinate offset", "Missing proprietary media codec fingerprint"],
        "typical_crime_contexts": ["Automated penetration testing attacks", "Kali Linux exploit delivery", "Web application vulnerability scanning"]
    },
    {
        "id": "falkon",
        "name": "Falkon",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "QtWebEngine",
        "regex": r"Falkon/(?:\d+)|QupZilla/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Falkon/24.05.0 Chrome/118.0.5993.159 Safari/537.36",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "KDE Project's QtWebEngine browser. Popular in lightweight Linux VM sandboxes used for malware analysis or bulletproof operations.",
        "opsec_vulnerabilities": "QtWebEngine user-agent structure and distinct Qt OpenGL pipeline rendering.",
        "deanon_vectors": ["QtWebEngine OpenGL signature", "KDE Plasma window manager metrics", "Falkon specific HTTP headers"],
        "typical_crime_contexts": ["Malware triage sandbox browsing", "Disposable Linux VPS browsing", "Proxy chaining operations"]
    },
    {
        "id": "gnome_web",
        "name": "GNOME Web (Epiphany)",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "WebKitGTK",
        "regex": r"Epiphany/(?:\d+)|WebKitGTK",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15 Epiphany/46.0",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Standard GNOME desktop browser on Ubuntu/Debian/Fedora. Indicates a Linux desktop workstation operator.",
        "opsec_vulnerabilities": "WebKitGTK exposes distinct font rendering anti-aliasing (Cairo/Pango) and Linux system file paths via error stacks.",
        "deanon_vectors": ["Cairo/Pango font rasterization hash", "WebKitGTK audio synthesis fingerprint", "GNOME Shell layout constants"],
        "typical_crime_contexts": ["Linux malware staging", "Automated reverse-proxy testing", "Darknet repository administration"]
    },
    {
        "id": "konqueror",
        "name": "Konqueror",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "KHTML / QtWebEngine",
        "regex": r"Konqueror/(?:\d+)|KHTML/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64) KHTML/5.245.0 (like Gecko) Konqueror/5.245.0",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Legendary KDE file manager and web browser. In 2026, presence points to legacy server automation, Unix vintage exploit development, or automated fuzzers.",
        "opsec_vulnerabilities": "KHTML layout engine produces ancient DOM prototypes completely divergent from modern Blink/Gecko.",
        "deanon_vectors": ["KHTML JavaScript prototype tree", "X11 legacy window protocol leaks", "Unix local username disclosure"],
        "typical_crime_contexts": ["Unix vintage vulnerability research", "Legacy file-server exploit staging", "Automated crawler fuzzing"]
    },
    {
        "id": "midori",
        "name": "Midori",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "Gecko / WebKitGTK",
        "regex": r"Midori/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0 Midori/11.2",
        "risk_tier": "MODERATE_EVASION_SIGNAL",
        "crime_behavior": "Lightweight open-source browser now backed by the Astian Foundation. Deployed on low-resource VPS nodes for rapid scraping.",
        "opsec_vulnerabilities": "Midori brand tokens and non-standard Gecko build IDs.",
        "deanon_vectors": ["Astian cloud pingback telemetry", "Midori user-agent header", "Low-resource VPS thread concurrency profile"],
        "typical_crime_contexts": ["Automated credential checking", "Fast flux proxy verification", "Web forum scraping"]
    },
    {
        "id": "nyxt",
        "name": "Nyxt",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "Common Lisp / WebKitGTK",
        "regex": r"Nyxt/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/605.1.15 (KHTML, like Gecko) Nyxt/3.11.0",
        "risk_tier": "DEV_MALWARE_AUTHOR_STAGING",
        "crime_behavior": "Hacker-oriented browser infinitely programmable in Common Lisp. Exclusively used by elite software engineers, cryptographers, and top-tier hackers.",
        "opsec_vulnerabilities": "Extremely rare user base (<0.001%). Any observed connection with Nyxt signature immediately narrows suspect pool to high-capability programmers.",
        "deanon_vectors": ["Common Lisp REPL interaction timing", "WebKitGTK Lisp bridge artifacts", "Statistical rarity isolation"],
        "typical_crime_contexts": ["Custom exploit framework automation", "Cryptographic key extraction", "Bespoke dark web indexing"]
    },
    {
        "id": "qutebrowser",
        "name": "qutebrowser",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "PyQt / QtWebEngine",
        "regex": r"qutebrowser/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.159 Safari/537.36 qutebrowser/3.1.0",
        "risk_tier": "DEV_MALWARE_AUTHOR_STAGING",
        "crime_behavior": "Keyboard-focused Vim-like browser written in Python/PyQt. Widely loved by Arch Linux rice hackers, kernel exploit developers, and botnet maintainers.",
        "opsec_vulnerabilities": "PyQt IPC communication timing, Vim-style navigation cadence (hjkl scrolling generates distinct micro-interval scroll events).",
        "deanon_vectors": ["Vim keybinding scroll timing telemetry", "Python PyQt wrapper artifact", "Arch Linux pacman library dependencies"],
        "typical_crime_contexts": ["Botnet command terminal monitoring", "Darknet forum rapid intelligence triage", "Kernel exploit staging"]
    },
    {
        "id": "dillo",
        "name": "Dillo",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "Dillo Engine (FLTK)",
        "regex": r"Dillo/(?:\d+)",
        "sample_ua": "Dillo/3.0.5",
        "risk_tier": "AUTOMATION_BOTNET",
        "crime_behavior": "Extremely minimal graphical browser without JavaScript support. Utilized by threat actors to safely view malicious HTML without triggering payload traps.",
        "opsec_vulnerabilities": "Zero JavaScript support, Dillo short raw User-Agent header, complete lack of CSS modern flexbox/grid rendering.",
        "deanon_vectors": ["Zero-JS execution behavioral signature", "FLTK GUI window metric probe", "Immediate short-string UA header"],
        "typical_crime_contexts": ["Canary token avoidance during recon", "Safe inspection of booby-trapped sites", "Ultra-fast headless scraping"]
    },
    {
        "id": "links",
        "name": "Links",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "Links Text Engine",
        "regex": r"^Links \((?:\d+)",
        "sample_ua": "Links (2.29; Linux x86_64; GNU/Linux)",
        "risk_tier": "AUTOMATION_BOTNET",
        "crime_behavior": "Text/graphics terminal browser. Run inside SSH terminal sessions from compromised servers and VPS relays to manage underground services.",
        "opsec_vulnerabilities": "Server-side terminal execution leaves no client-side DOM cookies, unique Accept headers (`text/html, text/plain`).",
        "deanon_vectors": ["Compromised server SSH session IP matching", "Accept-Encoding terminal format", "Rapid CLI request bursts"],
        "typical_crime_contexts": ["Compromised VPS interactive control", "Darknet hidden service sanity checks", "CLI-based account takeover"]
    },
    {
        "id": "lynx",
        "name": "Lynx",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "Lynx libwww",
        "regex": r"^Lynx/(?:\d+)",
        "sample_ua": "Lynx/2.9.1 libwww-FM/2.14 SSL-MM/1.4.1 OpenSSL/3.0.13",
        "risk_tier": "AUTOMATION_BOTNET",
        "crime_behavior": "Oldest text-only web browser still maintained. Extensively deployed in automated cron jobs, vulnerability scanners, and backdoor shells.",
        "opsec_vulnerabilities": "OpenSSL library version exposed in user-agent string; completely incapable of executing JavaScript or handling modern TLS SNI extensions.",
        "deanon_vectors": ["OpenSSL version banner in UA string", "Complete inability to execute client-side honeypots", "libwww HTTP header formatting"],
        "typical_crime_contexts": ["Remote web-shell enumeration", "Automated server uptime probing", "Blind SQL injection verification"]
    },
    {
        "id": "w3m",
        "name": "w3m",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "w3m Text Engine",
        "regex": r"^w3m/(?:\d+)",
        "sample_ua": "w3m/0.5.3+git20230121",
        "risk_tier": "AUTOMATION_BOTNET",
        "crime_behavior": "Text-based pager browser capable of inline terminal images. Run by sysadmins and rootkits inside compromised Linux bastions.",
        "opsec_vulnerabilities": "w3m raw User-Agent header, absence of DOM event listeners, Linux terminal escape sequence support.",
        "deanon_vectors": ["Terminal environment variable leaks", "Raw terminal request spacing", "Compromised server source IP correlation"],
        "typical_crime_contexts": ["Rootkit maintenance from SSH", "C2 panel access via reverse tunnel", "Localhost service probing on targets"]
    },
    {
        "id": "netsurf",
        "name": "NetSurf",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "NetSurf Custom Engine",
        "regex": r"NetSurf/(?:\d+)",
        "sample_ua": "NetSurf/3.11 (Linux; x86_64)",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Custom portable browser engine originally built for RISC OS. Run on micro-devices, embedded routers, and IoT botnet controllers.",
        "opsec_vulnerabilities": "Proprietary layout engine with distinct HTML parsing quirks and very limited JavaScript support.",
        "deanon_vectors": ["Embedded router architecture fingerprint", "NetSurf HTML parser non-conformance", "Hardware memory constraint profiling"],
        "typical_crime_contexts": ["Compromised IoT router proxy relay", "Embedded device weaponization", "Lightweight bot monitoring"]
    },
    {
        "id": "dooble",
        "name": "Dooble",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "QtWebEngine",
        "regex": r"Dooble/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36 Dooble/2024.03.01",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Open-source privacy browser designed for encryption and desktop isolation. Observed in cyber security research and isolated operations.",
        "opsec_vulnerabilities": "Specific Dooble build release strings in request headers and customized QtWebEngine font handling.",
        "deanon_vectors": ["Dooble desktop crypto database traces", "QtWebEngine font baseline metric", "Custom cookie jar cipher characteristics"],
        "typical_crime_contexts": ["Secure file sharing coordination", "Covert channel communications", "Air-gapped terminal access"]
    },
    {
        "id": "otter_browser",
        "name": "Otter Browser",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "QtWebEngine / WebKit",
        "regex": r"Otter/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Otter/1.0.03 Chrome/108.0.5359.128 Safari/537.36",
        "risk_tier": "MODERATE_EVASION_SIGNAL",
        "crime_behavior": "Project recreating the classic Opera 12 UI using Qt5. Preferred by nostalgic operators and modular proxy testers.",
        "opsec_vulnerabilities": "Otter user-agent token, custom Qt window geometry.",
        "deanon_vectors": ["Otter token identification", "Qt window aspect ratio", "Custom proxy switching timing delays"],
        "typical_crime_contexts": ["Modular proxy switching testing", "Underground archive access", "Vintage forum administration"]
    },
    {
        "id": "badwolf",
        "name": "BadWolf",
        "primary_category": "Linux / open-source browsers",
        "categories": ["Linux / open-source browsers"],
        "engine": "WebKitGTK",
        "regex": r"Badwolf/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15 Badwolf/1.3.0",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Minimalist privacy-oriented WebKitGTK browser with no state persistence between tabs. Favored by minimalist hackers.",
        "opsec_vulnerabilities": "Absence of all localStorage and sessionStorage APIs across navigations; unique WebKitGTK Linux compile flags.",
        "deanon_vectors": ["Zero-storage ephemeral session state", "WebKitGTK font smoothing on Linux", "Badwolf brand token in UA"],
        "typical_crime_contexts": ["Disposable credential verification", "Burner site access", "Privacy manifesto deployment"]
    },

    # --------------------------------------------------------------------------
    # 4. ANDROID-FOCUSED BROWSERS
    # --------------------------------------------------------------------------
    {
        "id": "firefox_android",
        "name": "Firefox for Android",
        "primary_category": "Android-focused",
        "categories": ["Android-focused", "Major desktop/mobile"],
        "engine": "GeckoView",
        "regex": r"Android.*Firefox/(?:\d+)(?!.*(Focus|Klar|Mull|Fennec))",
        "sample_ua": "Mozilla/5.0 (Android 14; Mobile; rv:127.0) Gecko/127.0 Firefox/127.0",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Mobile Gecko browser with extension support (uBlock Origin, Dark Reader). Commonly installed on suspect mobile devices.",
        "opsec_vulnerabilities": "Android hardware screen dimensions, touch event multi-pointer metrics, GeckoView font baseline on mobile.",
        "deanon_vectors": ["Mobile touch gesture kinetic profiling", "GeckoView font enumeration on Android", "Device orientation sensor leaks"],
        "typical_crime_contexts": ["Mobile carding store purchases", "Telegram darknet group admin", "Mobile phishing QA testing"]
    },
    {
        "id": "brave_android",
        "name": "Brave Browser (Android)",
        "primary_category": "Android-focused",
        "categories": ["Android-focused", "Privacy/security-focused"],
        "engine": "Blink",
        "regex": r"Android.*Chrome/.*Brave|BraveMobile",
        "sample_ua": "Mozilla/5.0 (Linux; Android 14; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36 Brave/126.0.0.0",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Mobile privacy browser popular among cryptocurrency traders and mobile darknet forum users.",
        "opsec_vulnerabilities": "Farbling canvas fingerprint on mobile GPU (Adreno / Immortalis) produces reproducible mathematical noise vectors.",
        "deanon_vectors": ["Mobile GPU farbling seed correlation", "Integrated Brave BAT wallet transaction link", "Device screen DPI ratio"],
        "typical_crime_contexts": ["Crypto drainer transactions", "Mobile marketplace escrow releases", "Forum trading"]
    },
    {
        "id": "chrome_android",
        "name": "Chrome for Android",
        "primary_category": "Android-focused",
        "categories": ["Android-focused", "Major desktop/mobile"],
        "engine": "Blink",
        "regex": r"Android.*Chrome/(?:\d+)(?!.*(Brave|Kiwi|SamsungBrowser|YaBrowser|UCBrowser|AlohaBrowser|Via))",
        "sample_ua": "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Stock Android browser tied to Google Account. If used by an actor to touch malicious infrastructure, provides 100% legal de-anonymization via Google subpeona.",
        "opsec_vulnerabilities": "Google Play Services device check, GAID (Google Advertising ID), persistent Google Account sync cookies, WebRTC WAN IP leaks.",
        "deanon_vectors": ["Google Play Services SafetyNet/Play Integrity tokens", "GAID advertising ID extraction", "Real carrier WAN IP from WebRTC"],
        "typical_crime_contexts": ["Fatal OPSEC leak during live cyber attack", "Accidental clearnet link click", "Victim impersonation failure"]
    },
    {
        "id": "opera_mini",
        "name": "Opera Mini",
        "primary_category": "Android-focused",
        "categories": ["Android-focused", "Major desktop/mobile"],
        "engine": "Presto / Cloud Transcoding",
        "regex": r"Opera Mini/(?:\d+)",
        "sample_ua": "Opera/9.80 (Android; Opera Mini/76.0.2254/191.312; U; en) Presto/2.12.423 Version/12.16",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Server-side proxy compression browser heavily used in developing nations with high data costs. Common in SIM-farm fraud and SMS interception hubs.",
        "opsec_vulnerabilities": "Opera proxy servers append `X-Forwarded-For` with the operator's real cellular IP; renders through old server-side Presto engine.",
        "deanon_vectors": ["X-Forwarded-For cellular carrier IP leak", "Opera Mini compression data-center IP mapping", "Server-side Presto rendering traits"],
        "typical_crime_contexts": ["SIM-box bypass fraud", "SMS verification code bypass", "Third-world money mule operations"]
    },
    {
        "id": "opera_android",
        "name": "Opera for Android",
        "primary_category": "Android-focused",
        "categories": ["Android-focused", "Major desktop/mobile"],
        "engine": "Blink",
        "regex": r"Android.*OPR/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36 OPR/80.1.4244.77443",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Full Chromium-based Opera browser on Android with free VPN toggle. Extensively utilized by amateur mobile fraudsters.",
        "opsec_vulnerabilities": "Free VPN routes through known commercial proxies; mobile WebRTC discloses true Wi-Fi/Cellular IP.",
        "deanon_vectors": ["WebRTC STUN mobile interface leak", "Opera mobile device account token", "Commercial VPN egress tagging"],
        "typical_crime_contexts": ["Credit card testing on mobile", "Gift card fraud", "Fake account creation"]
    },
    {
        "id": "vivaldi_android",
        "name": "Vivaldi for Android",
        "primary_category": "Android-focused",
        "categories": ["Android-focused", "Major desktop/mobile"],
        "engine": "Blink",
        "regex": r"Android.*Vivaldi/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.115 Mobile Safari/537.36 Vivaldi/6.8.3388.75",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Mobile version of Vivaldi with encrypted notes and tab stacking. Used for mobile threat intelligence coordination.",
        "opsec_vulnerabilities": "Vivaldi cloud synchronization metadata and custom mobile UI dimensions.",
        "deanon_vectors": ["Vivaldi sync endpoint connection logs", "Unique mobile tab strip metric", "Device sensor parameters"],
        "typical_crime_contexts": ["Secure note exchange between operatives", "Crypto trade execution", "Darknet forum mobile monitoring"]
    },
    {
        "id": "duckduckgo_android",
        "name": "DuckDuckGo Browser (Android)",
        "primary_category": "Android-focused",
        "categories": ["Android-focused", "Privacy/security-focused"],
        "engine": "Android WebView",
        "regex": r"Android.*DuckDuckGo/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36 DuckDuckGo/5",
        "risk_tier": "MODERATE_EVASION_SIGNAL",
        "crime_behavior": "Android privacy browser with App Tracking Protection. Deployed by mobile operators who want quick burner searches without history.",
        "opsec_vulnerabilities": "Uses the underlying system WebView; vulnerabilities and device identifiers in WebView can still be extracted.",
        "deanon_vectors": ["System WebView version correlation", "App Tracking Protection VPN tunnel IP characteristics", "Hardware screen resolution"],
        "typical_crime_contexts": ["Target reconnaissance", "Mobile doxing", "Fast burner web link verification"]
    },
    {
        "id": "edge_android",
        "name": "Edge for Android",
        "primary_category": "Android-focused",
        "categories": ["Android-focused", "Major desktop/mobile"],
        "engine": "Blink",
        "regex": r"Android.*EdgA/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 14; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36 EdgA/126.0.2592.86",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Microsoft Edge mobile build. Often used on corporate mobile devices (MDM enrolled), signaling high probability of corporate employee involvement or compromised corporate phone.",
        "opsec_vulnerabilities": "Intune MDM device enrollment tokens, Microsoft account synchronization, Bing Copilot AI session telemetry.",
        "deanon_vectors": ["Microsoft Intune corporate device ID", "Active corporate M365 tenant correlation", "Copilot chat session metadata"],
        "typical_crime_contexts": ["Insider corporate sabotage", "Mobile access to corporate secrets", "Spear-phishing delivery"]
    },
    {
        "id": "phoenix_browser",
        "name": "Phoenix Browser",
        "primary_category": "Android-focused",
        "categories": ["Android-focused"],
        "engine": "Blink / Transsion",
        "regex": r"PHX/(?:\d+)|Phoenix/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 12; TECNO CK7n) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.141 Mobile Safari/537.36 PHX/15.2.0",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Default browser on Transsion phones (Tecno, Infinix, itel) dominant in Africa and Latin America. Heavily involved in African cybercrime operations (Yahoo Boys, BEC, romance scams).",
        "opsec_vulnerabilities": "Transsion device identifiers, local Nigerian/Ghanaian telecom carrier APN tokens, distinct PHX user-agent header.",
        "deanon_vectors": ["Tecno/Infinix hardware IMEI/Build signatures", "African cellular carrier IP blocks (MTN, Airtel, Glo)", "PHX browser push notification ID"],
        "typical_crime_contexts": ["Business Email Compromise (BEC)", "Romance fraud syndicates", "Crypto investment pig-butchering"]
    },
    {
        "id": "soul_browser",
        "name": "Soul Browser",
        "primary_category": "Android-focused",
        "categories": ["Android-focused"],
        "engine": "Blink / Android WebView",
        "regex": r"SoulBrowser/(?:\d+)|Soul/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.5845.163 Mobile Safari/537.36 SoulBrowser/1.3.84",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Feature-packed Korean Android browser with video downloaders and stealth mode. Used for unauthorized media ripping and underground file acquisition.",
        "opsec_vulnerabilities": "Unique Soul Browser storage permissions, distinct downloader referrer headers.",
        "deanon_vectors": ["Referrer header anomalies", "Underlying WebView hardware fingerprint", "Korean language fallback preferences"],
        "typical_crime_contexts": ["Media intellectual property theft", "Stolen content dissemination", "Dark web multimedia harvesting"]
    },
    {
        "id": "fennec",
        "name": "Fennec F-Droid",
        "primary_category": "Android-focused",
        "categories": ["Android-focused", "Privacy/security-focused"],
        "engine": "GeckoView",
        "regex": r"Fennec/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Android 14; Mobile; rv:128.0) Gecko/128.0 Firefox/128.0 Fennec/128.0",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Open-source F-Droid build of Firefox for Android with Mozilla proprietary binaries and telemetry completely stripped.",
        "opsec_vulnerabilities": "Absence of Google Play Services components combined with GeckoView rendering creates an easily identifiable mobile profile.",
        "deanon_vectors": ["F-Droid build signature", "Absence of Google SafetyNet attestation", "Custom GeckoView font rasterization"],
        "typical_crime_contexts": ["Secure dark web mobile browsing", "Underground forum posting from burner phone", "Crypto wallet administration"]
    },

    # --------------------------------------------------------------------------
    # 5. APPLE ECOSYSTEM BROWSERS
    # --------------------------------------------------------------------------
    {
        "id": "icab_mobile",
        "name": "iCab Mobile",
        "primary_category": "Apple ecosystem",
        "categories": ["Apple ecosystem"],
        "engine": "WebKit",
        "regex": r"iCabMobile/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 iCabMobile/12.5.3",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Advanced iOS browser featuring user-agent spoofing, cookie filtering, and file download managers. Used by iOS power-users to bypass mobile bot protection.",
        "opsec_vulnerabilities": "Spoofed user-agents fail WebKit feature detection (e.g. spoofing Chrome on iOS still exposes WebKit internal objects like `window.webkit`).",
        "deanon_vectors": ["User-Agent vs WebKit DOM object contradiction", "iOS Metal graphics rendering", "iCab custom URL scheme hooks"],
        "typical_crime_contexts": ["iOS bot protection evasion", "Mobile phishing QA", "Automated mobile account creation"]
    },

    # --------------------------------------------------------------------------
    # 6. HISTORICAL / DISCONTINUED BROWSERS
    # --------------------------------------------------------------------------
    {
        "id": "internet_explorer",
        "name": "Internet Explorer",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers", "Enterprise / specialized"],
        "engine": "Trident",
        "regex": r"MSIE (?:\d+)|Trident/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Decommissioned Microsoft browser. In modern telemetry, indicates either an ancient SCADA/ICS control terminal, legacy corporate ATM, or an unpatched Windows 7/XP target.",
        "opsec_vulnerabilities": "Trident engine has hundreds of critical remote code execution (RCE) flaws; lacks modern CSP, HTTPS-only, and SameSite cookie protections.",
        "deanon_vectors": ["ActiveX component enumeration", "Trident rendering engine quirks", "Windows legacy NTLM authentication leaks"],
        "typical_crime_contexts": ["Industrial Control System (SCADA) targeting", "ATM banking malware execution", "Legacy government network infiltration"]
    },
    {
        "id": "netscape_navigator",
        "name": "Netscape Navigator",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Gecko / Mosaic Fork",
        "regex": r"Navigator/(?:\d+)|Netscape/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Netscape/9.0.0.6",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Historic browser from the 1990s. Found in historical breach databases, vintage exploit archives, or used as a spoofed user-agent by amateur scanners.",
        "opsec_vulnerabilities": "Completely incapable of modern TLS 1.3 or modern JS. If seen connecting over TLS 1.3, it is 100% a fake spoofed User-Agent.",
        "deanon_vectors": ["TLS version vs User-Agent contradiction", "Lack of modern DOM prototypes", "Historical breach archive matching"],
        "typical_crime_contexts": ["Vintage exploit kit testing", "Spoofed scanner honeypot triggering", "Archival cybercrime research"]
    },
    {
        "id": "netscape_communicator",
        "name": "Netscape Communicator",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Netscape Classic",
        "regex": r"Mozilla/4\.(?:[0-8]\d?)(?!.*compatible)",
        "sample_ua": "Mozilla/4.79 [en] (Windows NT 5.0; U)",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Late 1990s suite. Classic indicator of hardcoded ancient exploit scripts, old Perl scrapers, or retro CTF challenge solving.",
        "opsec_vulnerabilities": "Hardcoded HTTP/1.0 headers, complete lack of Host header in vintage implementations.",
        "deanon_vectors": ["HTTP/1.0 protocol anomaly", "Absence of Host / Accept-Encoding headers", "Script bot identification"],
        "typical_crime_contexts": ["Legacy CTF challenge exploitation", "Ancient botnet heartbeat script", "Amateur spoofing decoy"]
    },
    {
        "id": "mosaic",
        "name": "NCSA Mosaic",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Mosaic Original",
        "regex": r"NCSA_Mosaic/(?:\d+)|NCSA Mosaic",
        "sample_ua": "NCSA_Mosaic/2.0 (Windows_NT)",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "The grandfather of graphical web browsers (1993). Modern occurrences are 100% spoofed signatures deployed by script kiddies or automated scanners trying to look exotic.",
        "opsec_vulnerabilities": "Immediate cryptographic contradiction when connected over HTTPS/TLS.",
        "deanon_vectors": ["Instant TLS protocol contradiction", "Honeypot signature trigger", "Network scanner fingerprint matching"],
        "typical_crime_contexts": ["Reconnaissance scanner evasion attempt", "Honeypot triggering", "Academic retro security testing"]
    },
    {
        "id": "opera_presto",
        "name": "Opera Presto",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Presto",
        "regex": r"Presto/(?:\d+)|Version/12\.(?:\d+).*Opera",
        "sample_ua": "Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Classic Opera browser before switching to Chromium (2013). Known for its powerful built-in BitTorrent and mail clients. Used in vintage cyber attacks.",
        "opsec_vulnerabilities": "Presto layout engine has distinct JavaScript syntax error messages and non-standard RegExp support.",
        "deanon_vectors": ["Presto JS error message matching", "BitTorrent client peer ID overlap", "TLS 1.0/1.1 cipher negotiation"],
        "typical_crime_contexts": ["Legacy cybercrime syndicate archival", "BitTorrent initial seed distribution", "Retro exploit recreation"]
    },
    {
        "id": "firefox_os",
        "name": "Firefox OS Browser",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Gecko (B2G)",
        "regex": r"Mobile; rv:(?:\d+).*Gecko/.*Firefox/(?:\d+)|B2G",
        "sample_ua": "Mozilla/5.0 (Mobile; rv:44.0) Gecko/44.0 Firefox/44.0",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Discontinued Boot2Gecko mobile operating system. Found in IoT smart devices, smart TVs, and legacy burner handsets.",
        "opsec_vulnerabilities": "Gecko B2G APIs (e.g. navigator.mozTelephony, navigator.mozBattery), frozen 2016 layout metrics.",
        "deanon_vectors": ["B2G proprietary WebAPI presence", "Outdated mobile Gecko CSS prefix support", "Smart TV embedded hardware match"],
        "typical_crime_contexts": ["Smart TV botnet nodes", "IoT crypto mining", "Abandoned burner phone logs"]
    },
    {
        "id": "flock",
        "name": "Flock",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Gecko / Chromium",
        "regex": r"Flock/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.0.19) Gecko/2010040121 Firefox/3.0.19 Flock/2.6.1",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Discontinued social web browser (2005-2011). Seen in archival criminal logs, old MySpace/Facebook social engineering bot dumps.",
        "opsec_vulnerabilities": "Built-in social network API hooks, deprecated Mozilla Gecko 1.9 rendering quirks.",
        "deanon_vectors": ["Hardcoded social API endpoint pings", "Historical credential database cross-matching", "Gecko 1.9 parser footprint"],
        "typical_crime_contexts": ["Archival social engineering evidence", "Historical phishing campaign analysis", "Zombie botnet remnant"]
    },
    {
        "id": "rockmelt",
        "name": "RockMelt",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Chromium",
        "regex": r"RockMelt/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1 RockMelt/0.9.68.1565",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Early social browser built on Chromium (discontinued in 2013). Appears in historical breach logs from veteran cyber threat actors.",
        "opsec_vulnerabilities": "RockMelt Facebook chat sidebar API integration, ancient Chromium 14 layout metrics.",
        "deanon_vectors": ["Historical breach account matching", "Chromium 14 V8 engine bytecode signatures", "Facebook legacy API token remnants"],
        "typical_crime_contexts": ["Veteran cybercriminal persona linkage", "Historic dark web escrow dispute records", "Ancient carding chat logs"]
    },
    {
        "id": "maxthon",
        "name": "Maxthon Cloud Browser",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Dual Core (Trident + Blink)",
        "regex": r"Maxthon/(?:\d+)|Maxthon",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.228 Safari/537.36 Maxthon/7.1.8.8000",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Dual-engine browser (China). Known for built-in cloud push, blockchain Vbox integration, and resource sniffer tools favored by carders.",
        "opsec_vulnerabilities": "Maxthon cloud account sync broadcasts machine serial numbers to Beijing cloud servers.",
        "deanon_vectors": ["Maxthon passport ID", "Dual-engine switching anomaly (switches between Trident & Blink)", "Resource sniffer DOM hooks"],
        "typical_crime_contexts": ["Carding video streaming fraud", "Media ripping from protected servers", "Chinese underground trading"]
    },
    {
        "id": "comodo_dragon",
        "name": "Comodo Dragon",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Blink",
        "regex": r"Comodo_Dragon/(?:\d+)|Dragon/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.89 Safari/537.36 Dragon/118.0.5993.89",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Security browser by Comodo CA. Novice operators utilize it for its built-in SecureDNS, not realizing Comodo logs all DNS queries.",
        "opsec_vulnerabilities": "Comodo SecureDNS server queries create a centralized government-subpoenaable log of all visited domains.",
        "deanon_vectors": ["Comodo SecureDNS IP server logs", "Comodo certificate validation hooks", "Fixed plugin list"],
        "typical_crime_contexts": ["Novice carding attempts", "Malicious mirror indexing", "Staging server testing"]
    },
    {
        "id": "srware_iron",
        "name": "SRWare Iron",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Blink",
        "regex": r"Iron/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6300.0 Safari/537.36 Iron/124.0.6300.0",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "German privacy Chromium build without Google client tracking. Used by German/European underground actors on clearnet forums.",
        "opsec_vulnerabilities": "Distinctive Iron user-agent token and lack of default Google components.",
        "deanon_vectors": ["Iron user-agent token", "Custom ad-block syntax file traces", "German language locale defaults"],
        "typical_crime_contexts": ["European darknet carding", "Crimenet forum management", "Exploit hosting"]
    },
    {
        "id": "avant_browser",
        "name": "Avant Browser",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Tri-Core (Trident + Gecko + Blink)",
        "regex": r"Avant Browser",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; Avant Browser; rv:11.0) like Gecko",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Tri-engine browser allowing dynamic rendering switching. Historically used by carders to test anti-fraud detection across multiple rendering engines.",
        "opsec_vulnerabilities": "Leaves traces of all three rendering engines in cached storage and system font metrics.",
        "deanon_vectors": ["Multi-engine font measurement divergence", "Avant Browser token in HTTP headers", "Windows registry key leaks"],
        "typical_crime_contexts": ["Anti-fraud system testing", "Carding payment gateway fuzzing", "Exploit kit multi-engine testing"]
    },
    {
        "id": "lunascape",
        "name": "Lunascape",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Tri-Core (Gecko + WebKit + Trident)",
        "regex": r"Lunascape/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0 Lunascape/6.15.2",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Japanese triple-engine browser. Used by exploit authors to check vulnerability triggers across Trident, Gecko, and WebKit simultaneously.",
        "opsec_vulnerabilities": "Triple-engine DLL loading footprints in process memory; unique user-agent token.",
        "deanon_vectors": ["Triple-engine DOM object cross-pollution", "Lunascape UA string", "Japanese OS language environment"],
        "typical_crime_contexts": ["Multi-vector exploit research", "Cross-browser fingerprint evasion testing", "Japanese cyber syndicate ops"]
    },
    {
        "id": "slimbrowser",
        "name": "SlimBrowser",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Gecko",
        "regex": r"SlimBrowser/(?:\d+)|SlimBrowser",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0 SlimBrowser/17.0.1",
        "risk_tier": "MODERATE_EVASION_SIGNAL",
        "crime_behavior": "Lightweight tabbed browser featuring ad-blockers and download managers. Deployed in disposable bot operations.",
        "opsec_vulnerabilities": "Custom SlimBrowser header tags, outdated Gecko baseline.",
        "deanon_vectors": ["SlimBrowser header tag", "Outdated Gecko vulnerability profiling", "Integrated download manager headers"],
        "typical_crime_contexts": ["Automated file scraping", "Low-tier botnet testing", "Disposable account farming"]
    },
    {
        "id": "slimjet",
        "name": "Slimjet",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Blink",
        "regex": r"Slimjet/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.130 Safari/537.36 Slimjet/42.0.4.0",
        "risk_tier": "MODERATE_EVASION_SIGNAL",
        "crime_behavior": "Chromium fork by FlashPeak with built-in ad blocker and proxy switcher. Used by carders for proxy testing.",
        "opsec_vulnerabilities": "Slimjet branding in User-Agent, distinct built-in proxy switching handshake timing.",
        "deanon_vectors": ["Slimjet user-agent token", "Proxy rotation latency jitter", "FlashPeak update pingbacks"],
        "typical_crime_contexts": ["Proxy chaining and rotation fraud", "Carding panel management", "Scam page deployment"]
    },
    {
        "id": "torch_browser",
        "name": "Torch Browser",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Blink",
        "regex": r"Torch/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36 Torch/69.0.0.2990",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Media and BitTorrent focused Chromium browser. Famous in 2014-2018 for torrent piracy and unauthorized distribution of pirated tools.",
        "opsec_vulnerabilities": "Embedded BitTorrent engine broadcasts the client's real public IP address over DHT (Distributed Hash Table) even if web traffic is proxied.",
        "deanon_vectors": ["DHT BitTorrent peer IP leak", "Torch torrent client handshake", "Frozen ancient Chromium 69 engine"],
        "typical_crime_contexts": ["Pirated software and malware distribution", "Torrent swarm tracking", "Stolen media trafficking"]
    },
    {
        "id": "epic_privacy_browser",
        "name": "Epic Privacy Browser",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers", "Privacy/security-focused"],
        "engine": "Blink",
        "regex": r"Epic/(?:\d+)|EpicPrivacyBrowser",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Epic/122.0.0.0",
        "risk_tier": "HIGH_ANONYMITY_EVASION",
        "crime_behavior": "Indian Chromium privacy browser with built-in encrypted proxy. Extensively abused by fraudsters seeking quick proxy masking without installing Tor.",
        "opsec_vulnerabilities": "Epic proxy servers are operated by Aloxii with static data center IP ranges that are easily identified and blocked by anti-fraud systems.",
        "deanon_vectors": ["Aloxii proxy server egress IP cluster", "Canvas fingerprint block detection", "WebRTC disable flag"],
        "typical_crime_contexts": ["Online banking fraud attempts", "Social media account takeover", "Credit card testing"]
    },
    {
        "id": "citrio",
        "name": "Citrio",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Blink",
        "regex": r"Citrio/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36 Citrio/50.0.2661.272",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Chromium fork with built-in torrent and proxy manager. Frequently distributed bundled with adware/PUPs; indicates an adware operator or infected victim.",
        "opsec_vulnerabilities": "Adware beaconing to Catalina Group servers, ancient Chrome 50 codebase.",
        "deanon_vectors": ["Adware C2 telemetry beacon", "Torrent client DHT announce", "Chrome 50 obsolete cipher suite"],
        "typical_crime_contexts": ["Adware botnet affiliate operations", "Malicious software bundling", "Cryptominer distribution"]
    },
    {
        "id": "yandex_elements",
        "name": "Yandex Elements",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Trident / Gecko / Blink Extension",
        "regex": r"YandexBar|YARUBrowser|YaMarket",
        "sample_ua": "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0; YandexBar/8.5) like Gecko",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Legacy toolbar extension bundled with freeware across Russia and the CIS. Present in historical Russian cybercriminal logs.",
        "opsec_vulnerabilities": "YandexBar injected cookies, machine-specific installation GUID.",
        "deanon_vectors": ["YandexBar installation GUID", "Russian search query history leaks", "CIS regional ISP IP mapping"],
        "typical_crime_contexts": ["Russian legacy cybercrime logs", "CIS banking malware victims", "Historical spyware tracking"]
    },
    {
        "id": "camino",
        "name": "Camino",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "Gecko (Cocoa)",
        "regex": r"Camino/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en; rv:1.9.2.29) Gecko/20120906 Camino/2.1.3",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Historical native Cocoa/Gecko browser for macOS (discontinued 2013). Seen in vintage macOS exploit archives and veteran Mac hacker dossiers.",
        "opsec_vulnerabilities": "Gecko 1.9 rendering engine, ancient macOS 10.6 font rasterization.",
        "deanon_vectors": ["Cocoa Gecko engine metrics", "macOS legacy system font hash", "Historical Apple hacker forum records"],
        "typical_crime_contexts": ["Historic Apple platform hacking", "Vintage Mac exploit kits", "Archival persona de-anonymization"]
    },
    {
        "id": "omniweb",
        "name": "OmniWeb",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "WebKit / OmniWeb Classic",
        "regex": r"OmniWeb/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-US) AppleWebKit/533.21.1 (KHTML, like Gecko) OmniWeb/v622.18.0",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Pioneering NeXTSTEP and macOS browser. Classic high-prestige hacker browser in the 2000s; now exclusively a retro-computing artifact.",
        "opsec_vulnerabilities": "NeXTSTEP heritage DOM properties and archaic WebKit build version.",
        "deanon_vectors": ["Archaic WebKit DOM signatures", "NeXTSTEP / Mac OS X 10.6 system parameters", "Historical hacker forum handle matching"],
        "typical_crime_contexts": ["Retro exploit development", "Historical cyber warfare archive review", "High-profile veteran hacker dossier"]
    },
    {
        "id": "shiira",
        "name": "Shiira",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "WebKit",
        "regex": r"Shiira/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en) AppleWebKit/523.12 (KHTML, like Gecko) Version/3.0.4 Safari/523.12 Shiira/2.2",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Japanese open-source WebKit browser for macOS (2004-2009). Found in historical Japanese cyber investigation records.",
        "opsec_vulnerabilities": "Shiira user-agent token and ancient WebKit rendering characteristics.",
        "deanon_vectors": ["Shiira user-agent string", "Japanese macOS system encoding", "Vintage exploit archive linkage"],
        "typical_crime_contexts": ["Historic Japanese cybercrime logs", "Vintage Mac trojan delivery", "Archival evidence cross-correlation"]
    },
    {
        "id": "stainless",
        "name": "Stainless",
        "primary_category": "Historical / discontinued browsers",
        "categories": ["Historical / discontinued browsers"],
        "engine": "WebKit (Multi-Process)",
        "regex": r"Stainless/(?:\d+)",
        "sample_ua": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-us) AppleWebKit/533.19.4 (KHTML, like Gecko) Stainless/0.8",
        "risk_tier": "HISTORICAL_LEGACY_ARCHIVE",
        "crime_behavior": "Early multi-process Mac browser created to test parallel session authentication before Chrome came to OS X. Used for parallel account testing.",
        "opsec_vulnerabilities": "Parallel process PID leakage and ancient WebKit metrics.",
        "deanon_vectors": ["Stainless process architecture signature", "Multi-cookie jar parallel testing anomalies", "macOS vintage build matching"],
        "typical_crime_contexts": ["Early multi-account forum flooding", "Parallel brute force testing", "Historical identity correlation"]
    },

    # --------------------------------------------------------------------------
    # 7. ENTERPRISE / SPECIALIZED BROWSERS
    # --------------------------------------------------------------------------
    {
        "id": "ibm_webexplorer",
        "name": "IBM WebExplorer",
        "primary_category": "Enterprise / specialized",
        "categories": ["Enterprise / specialized", "Historical / discontinued browsers"],
        "engine": "IBM OS/2 Engine",
        "regex": r"IBM WebExplorer|webexplorer",
        "sample_ua": "IBM WebExplorer /v1.2",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "1994 browser for IBM OS/2 Warp. In modern cyberspace, indicates a compromised IBM OS/2 mainframe or critical banking core system being probed or operated.",
        "opsec_vulnerabilities": "Runs exclusively on legacy IBM OS/2 Warp installations; zero cryptographic protection.",
        "deanon_vectors": ["IBM OS/2 Warp mainframe IP range", "Complete lack of modern HTTP headers", "SWIFT/Banking core system network isolation breach"],
        "typical_crime_contexts": ["Legacy banking mainframe breach", "SWIFT financial core manipulation", "Critical infrastructure attack"]
    },
    {
        "id": "chrome_enterprise",
        "name": "Google Chrome Enterprise",
        "primary_category": "Enterprise / specialized",
        "categories": ["Enterprise / specialized"],
        "engine": "Blink",
        "regex": r"Chrome/(?:\d+).*Enterprise|Google-Chrome-Enterprise",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.127 Safari/537.36 Enterprise",
        "risk_tier": "ENTERPRISE_INSIDER_RISK",
        "crime_behavior": "Managed enterprise browser enrolled in Google Cloud Management. Used in insider data theft, corporate sabotage, or ransomware staging from an enterprise workstation.",
        "opsec_vulnerabilities": "Chrome Enterprise Core sends device serial, managed user email, active directory domain, and enrolled extensions directly to enterprise admin console.",
        "deanon_vectors": ["Enterprise enrollment token extraction", "Corporate domain Active Directory username", "Enterprise policy enforcement beacon"],
        "typical_crime_contexts": ["Insider threat data exfiltration", "Corporate espionage", "Ransomware staging on corporate laptop"]
    },
    {
        "id": "firefox_esr",
        "name": "Firefox ESR",
        "primary_category": "Enterprise / specialized",
        "categories": ["Enterprise / specialized"],
        "engine": "Gecko (ESR)",
        "regex": r"rv:(?:115|128)\.0.*Gecko/20100101 Firefox/(?:115|128)\.0",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Firefox Extended Support Release. Primary base engine for Tor Browser and Mullvad Browser. Crucial to distinguish whether it is corporate ESR or Tor Browser.",
        "opsec_vulnerabilities": "If connected without Tor letterboxing, reveals an unhardened enterprise workstation or Debian/RHEL server.",
        "deanon_vectors": ["Absence of letterboxing distinguishes ESR from Tor", "Enterprise font configuration", "Operating system build verification"],
        "typical_crime_contexts": ["Corporate workstation pivot", "Debian Linux server web browsing", "Misconfigured Tor Browser emulation"]
    },
    {
        "id": "kiosk_browser",
        "name": "Kiosk Browser",
        "primary_category": "Enterprise / specialized",
        "categories": ["Enterprise / specialized"],
        "engine": "Blink / WebKit Lockdown",
        "regex": r"Kiosk|KioskBrowser|SiteKiosk",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 SiteKiosk/9.8",
        "risk_tier": "CRITICAL_OPSEC_LEAK",
        "crime_behavior": "Public kiosk or point-of-sale lockdown browser. Observed when threat actors jailbreak a public kiosk (airport, hotel, mall) to perform cyber crimes anonymously.",
        "opsec_vulnerabilities": "Public CCTV camera timestamps match exact browsing seconds; kiosk terminal ID is hardcoded into configuration headers.",
        "deanon_vectors": ["Physical Kiosk ID and GPS location", "Public CCTV security footage timestamp matching", "SiteKiosk management server telemetry"],
        "typical_crime_contexts": ["Public airport/hotel kiosk jailbreak", "Anonymous bomb threat / extortion dispatch", "Credit card skimming at public terminals"]
    },
    {
        "id": "citrix_secure_browser",
        "name": "Citrix Secure Browser",
        "primary_category": "Enterprise / specialized",
        "categories": ["Enterprise / specialized"],
        "engine": "Citrix Virtual WebKit/Blink",
        "regex": r"CitrixReceiver|CitrixSecureBrowser|CtxWeb",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 CitrixSecureBrowser/24.1",
        "risk_tier": "ENTERPRISE_INSIDER_RISK",
        "crime_behavior": "Isolated virtual cloud container browser hosted on corporate Citrix Hypervisors. Abused by threat actors who gained corporate VDI credentials.",
        "opsec_vulnerabilities": "Citrix farm internal server names, client VDI session IDs, NetScaler gateway public IP addresses.",
        "deanon_vectors": ["Citrix NetScaler corporate gateway IP", "VDI User Session ticket", "Active Directory corporate domain leak"],
        "typical_crime_contexts": ["Compromised corporate VDI access", "Financial institution wire tampering", "Insider trading communication"]
    },
    {
        "id": "vmware_browser",
        "name": "VMware Browser (Workspace ONE)",
        "primary_category": "Enterprise / specialized",
        "categories": ["Enterprise / specialized"],
        "engine": "VMware AirWatch WebKit",
        "regex": r"AirWatchBrowser|VMwareBrowser|WorkspaceONE",
        "sample_ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 AirWatchBrowser/23.12",
        "risk_tier": "ENTERPRISE_INSIDER_RISK",
        "crime_behavior": "Enterprise mobile container browser managed by VMware Workspace ONE. Signals a stolen or rogue corporate mobile device.",
        "opsec_vulnerabilities": "AirWatch corporate device enrollment UDID, corporate certificate authority headers, enterprise proxy tunnel.",
        "deanon_vectors": ["AirWatch MDM enrolled device UUID", "Corporate client TLS certificate fingerprint", "Enterprise VPN endpoint attribution"],
        "typical_crime_contexts": ["Stolen enterprise phone exploitation", "Corporate intellectual property theft", "Enterprise cloud portal breach"]
    },
    {
        "id": "blackberry_browser",
        "name": "BlackBerry Browser",
        "primary_category": "Enterprise / specialized",
        "categories": ["Enterprise / specialized", "Historical / discontinued browsers"],
        "engine": "BlackBerry WebKit / Bold Engine",
        "regex": r"BlackBerry|BB10|PlayBook",
        "sample_ua": "Mozilla/5.0 (BB10; Touch) AppleWebKit/537.35+ (KHTML, like Gecko) Version/10.3.3.3216 Mobile Safari/537.35+",
        "risk_tier": "HIGH_CORRELATION_SIGNAL",
        "crime_behavior": "Legendary enterprise encrypted mobile browser. Heavily utilized by vintage financial syndicates, narcotics cartels (custom PGP BlackBerry phones), and legacy operators.",
        "opsec_vulnerabilities": "BlackBerry PIN and BES (BlackBerry Enterprise Server) routing headers disclose server architecture.",
        "deanon_vectors": ["BlackBerry PIN number correlation", "BES enterprise server domain", "BB10 WebKit distinct CSS prefix signature"],
        "typical_crime_contexts": ["Cartel PGP encrypted handset operations", "Historic wire fraud syndicates", "Legacy corporate espionage"]
    },

    # --------------------------------------------------------------------------
    # 8. DEVELOPER / TESTING BROWSERS
    # --------------------------------------------------------------------------
    {
        "id": "chrome_dev",
        "name": "Chrome Dev",
        "primary_category": "Developer / testing browsers",
        "categories": ["Developer / testing browsers"],
        "engine": "Blink",
        "regex": r"Chrome/(?:1[2-9]\d|2\d\d)\..*Dev",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6580.0 Safari/537.36 Dev",
        "risk_tier": "DEV_MALWARE_AUTHOR_STAGING",
        "crime_behavior": "Weekly Chromium developer channel. Used by exploit researchers, malware dev teams, and botnet operators to test newly crafted payloads.",
        "opsec_vulnerabilities": "Weekly version numbers and enabled developer flags (e.g. experimental WebGPU, WebAudio debug extensions).",
        "deanon_vectors": ["Dev build version progression analysis", "Experimental API flag fingerprints", "Chrome Dev feedback telemetry"],
        "typical_crime_contexts": ["Exploit kit payload staging", "Drive-by download weaponization", "Browser zero-day research"]
    },
    {
        "id": "firefox_developer_edition",
        "name": "Firefox Developer Edition",
        "primary_category": "Developer / testing browsers",
        "categories": ["Developer / testing browsers"],
        "engine": "Gecko",
        "regex": r"Firefox/(?:\d+)\.0b\d+|Firefox/.*Developer",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0b9",
        "risk_tier": "DEV_MALWARE_AUTHOR_STAGING",
        "crime_behavior": "Firefox build pre-configured with developer tools, remote debugging, and unsigned extension support. Ideal platform for malware authors writing malicious extensions.",
        "opsec_vulnerabilities": "Remote debugging port listener (port 6000), unsigned add-on execution flags, distinct blue Developer Edition theme constants.",
        "deanon_vectors": ["Remote Gecko debugging socket probe", "Unsigned extension signature extraction", "Developer Edition build ID"],
        "typical_crime_contexts": ["Malicious browser extension development", "C2 admin panel frontend development", "Darknet marketplace UI development"]
    },
    {
        "id": "edge_dev",
        "name": "Microsoft Edge Dev",
        "primary_category": "Developer / testing browsers",
        "categories": ["Developer / testing browsers"],
        "engine": "Blink",
        "regex": r"Edg/(?:\d+)\..*Dev",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.2651.10 Dev",
        "risk_tier": "DEV_MALWARE_AUTHOR_STAGING",
        "crime_behavior": "Weekly Edge developer build. Used to study Microsoft Defender SmartScreen heuristics and bypass Windows antivirus detection.",
        "opsec_vulnerabilities": "Edge Dev specific telemetry, Microsoft feedback diagnostics.",
        "deanon_vectors": ["SmartScreen bypass testing telemetry", "Edge Dev version list", "Corporate Windows Insider ID"],
        "typical_crime_contexts": ["SmartScreen bypass testing", "Windows Defender evasion research", "Ransomware staging"]
    },
    {
        "id": "edge_beta",
        "name": "Microsoft Edge Beta",
        "primary_category": "Developer / testing browsers",
        "categories": ["Developer / testing browsers"],
        "engine": "Blink",
        "regex": r"Edg/(?:\d+)\..*Beta",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.2651.20 Beta",
        "risk_tier": "ELEVATED_OPSEC_LEAK",
        "crime_behavior": "Edge major release preview. Monitored by cyber actors to ensure ongoing access campaigns will persist into future OS patches.",
        "opsec_vulnerabilities": "Beta build channel header disclosure.",
        "deanon_vectors": ["Edge Beta telemetry header", "Client Hints full version sequence", "Windows build pairing"],
        "typical_crime_contexts": ["Persistence verification across Windows updates", "Enterprise malware longevity testing", "Credential stealer QA"]
    },
    {
        "id": "opera_developer",
        "name": "Opera Developer",
        "primary_category": "Developer / testing browsers",
        "categories": ["Developer / testing browsers"],
        "engine": "Blink",
        "regex": r"OPR/(?:\d+)\..*(?:Developer|dev)",
        "sample_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/112.0.5182.0 (Developer)",
        "risk_tier": "DEV_MALWARE_AUTHOR_STAGING",
        "crime_behavior": "Bleeding edge Opera build. Used by developers of proxy-hopping bots and browser-based cryptominers.",
        "opsec_vulnerabilities": "Opera developer build revision tags and debug flags.",
        "deanon_vectors": ["Opera Developer telemetry logs", "Experimental proxy engine flags", "Developer UID tokens"],
        "typical_crime_contexts": ["Cryptominer script testing", "Proxy hopping automation", "Botnet web controller development"]
    },
    {
        "id": "safari_technology_preview",
        "name": "Safari Technology Preview",
        "primary_category": "Developer / testing browsers",
        "categories": ["Developer / testing browsers", "Apple ecosystem"],
        "engine": "WebKit (Bleeding Edge)",
        "regex": r"Safari/(?:\d+).*Technology Preview|Version/(?:\d+).*Safari.*Preview",
        "sample_ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15 Safari/Technology Preview",
        "risk_tier": "DEV_MALWARE_AUTHOR_STAGING",
        "crime_behavior": "Bi-weekly Apple release with cutting-edge WebKit improvements. Explored by iOS/macOS exploit brokers developing WebKit 0-day chains for Pegasus-style spyware.",
        "opsec_vulnerabilities": "Technology Preview build release numbers (e.g. Release 198) map precisely to Apple WebKit repository git commits.",
        "deanon_vectors": ["WebKit commit-level build tracking", "Metal 3 GPU shader compilation benchmark", "Apple developer seed telemetry"],
        "typical_crime_contexts": ["WebKit 0-day exploit weaponization", "Commercial spyware development (Pegasus/Predator style)", "macOS security bypass research"]
    }
]

# Quick lookup map
BROWSER_MAP: Dict[str, Dict[str, Any]] = {b["id"]: b for b in BROWSER_REGISTRY}

CATEGORY_NAMES = [
    "Major desktop/mobile",
    "Privacy/security-focused",
    "Linux / open-source browsers",
    "Android-focused",
    "Apple ecosystem",
    "Historical / discontinued browsers",
    "Enterprise / specialized",
    "Developer / testing browsers"
]

# ==============================================================================
# IDENTIFICATION & FORENSIC CRIME PATTERN ANALYSIS
# ==============================================================================

def identify_browser_from_artifact(user_agent: str, raw_headers: str = "") -> Optional[Dict[str, Any]]:
    """
    Scans User-Agent and HTTP headers against all 80+ browsers in the registry.
    Prioritizes specific developer/testing/fork signatures before falling back to base engines.
    """
    target_str = f"{user_agent} {raw_headers}".strip()
    if not target_str:
        return None

    # Priority 1: Match highly specific variants (Canary, Developer, Pale Moon, Floorp, Tor, Mullvad, etc.)
    sorted_registry = sorted(
        BROWSER_REGISTRY,
        key=lambda b: (
            0 if b["id"] in ["google_chrome", "mozilla_firefox", "apple_safari", "microsoft_edge", "chromium"] else 1
        ),
        reverse=True
    )

    for browser in sorted_registry:
        pattern = browser["regex"]
        try:
            if re.search(pattern, target_str, re.IGNORECASE):
                return browser
        except Exception:
            continue

    return None

def analyze_browser_crime_pattern(
    user_agent: str,
    ip_address: str = "",
    raw_headers: str = "",
    source_context: str = "Dark Web Reconnaissance"
) -> Dict[str, Any]:
    """
    Performs forensic de-anonymization and crime pattern analysis for any intercepted browser artifact.
    """
    matched_browser = identify_browser_from_artifact(user_agent, raw_headers)
    
    # Hash for chain of custody
    evidence_hash = hashlib.sha256((user_agent + ip_address + raw_headers).encode()).hexdigest()

    # Known Tor exit subnets
    KNOWN_TOR_EXIT_SUBNETS = [
        "185.220.100.", "185.220.101.", "185.220.102.", "185.220.103.",
        "198.98.56.", "198.98.57.", "199.249.230.", "171.25.193.",
        "109.70.100.", "51.15.", "162.247.74.", "176.10.99."
    ]
    is_tor_ip = any(ip_address.startswith(p) for p in KNOWN_TOR_EXIT_SUBNETS)
    is_onion_context = "onion" in source_context.lower() or "darknet" in source_context.lower()

    if matched_browser:
        browser_id = matched_browser["id"]
        browser_name = matched_browser["name"]
        primary_category = matched_browser["primary_category"]
        engine = matched_browser["engine"]
        risk_tier = matched_browser["risk_tier"]
        crime_behavior = matched_browser["crime_behavior"]
        opsec_vulnerabilities = matched_browser["opsec_vulnerabilities"]
        deanon_vectors = matched_browser["deanon_vectors"]
        typical_crime_contexts = matched_browser["typical_crime_contexts"]
        confidence = 0.95
    else:
        # Generic automated or unknown client
        is_bot = bool(re.search(r"curl|python|wget|go-http|axios|fetch|aiohttp|scrapy", user_agent, re.IGNORECASE))
        browser_id = "automated_script" if is_bot else "unknown_client"
        browser_name = "Automated Script / Botnet Worker" if is_bot else "Unidentified Client"
        primary_category = "Developer / testing browsers" if is_bot else "Major desktop/mobile"
        engine = "CLI / Script Runtime" if is_bot else "Unknown"
        risk_tier = "AUTOMATION_BOTNET" if is_bot else "MODERATE_EVASION_SIGNAL"
        crime_behavior = (
            "Automated scraping / credential stuffing bot executing raw HTTP requests without full browser rendering."
            if is_bot else "Unclassified client signature with non-standard header composition."
        )
        opsec_vulnerabilities = "Default script User-Agent headers, TLS client hello fingerprint (JA3/JA4) divergence."
        deanon_vectors = ["JA3 TLS fingerprint mapping", "Rate-limit timing analysis", "Egress hosting ASN check"]
        typical_crime_contexts = ["Automated credential stuffing", "DDoS attacks", "Darknet mirror scraping"]
        confidence = 0.88 if is_bot else 0.50

    # Determine OPSEC failure severity
    opsec_leak_detected = False
    opsec_leak_reasons: List[str] = []

    # Check for Clearnet Browser on Darknet / Onion service
    if (is_tor_ip or is_onion_context) and risk_tier in ["CRITICAL_OPSEC_LEAK", "ENTERPRISE_INSIDER_RISK"]:
        opsec_leak_detected = True
        opsec_leak_reasons.append(
            f"CRITICAL OPSEC FAILURE: Threat actor connected to underground/Tor infrastructure using clearnet {browser_name}. "
            f"Leaked Client Hints, hardware models, and canvas parameters render the operator de-anonymizable."
        )

    # Check for Developer / Bleeding Edge testing browser on illicit sites
    if risk_tier == "DEV_MALWARE_AUTHOR_STAGING":
        opsec_leak_reasons.append(
            f"MALWARE AUTHOR WORKSTATION FINGERPRINT: Client is running {browser_name}. "
            f"Indicates vulnerability development, experimental sandbox escape testing, or malware compilation environment."
        )

    # Check for Enterprise Browser on Darknet
    if risk_tier == "ENTERPRISE_INSIDER_RISK":
        opsec_leak_reasons.append(
            f"INSIDER THREAT / CORPORATE COMPROMISE: Client is running enterprise managed {browser_name}. "
            f"Indicates activity originates from within a corporate active directory enterprise network."
        )

    # Check for Mobile Fraud Browser
    if "Android-focused" in primary_category and ("card" in source_context.lower() or "fraud" in source_context.lower() or "sim" in source_context.lower()):
        opsec_leak_reasons.append(
            f"MOBILE FRAUD OPERATIVE: {browser_name} is actively utilized in mobile credential injection and SIM-swapping rings."
        )

    if not opsec_leak_reasons:
        if risk_tier == "HIGH_ANONYMITY_EVASION":
            opsec_leak_reasons.append(f"Hardened anonymity profile ({browser_name}). Threat actor maintained strict operational hygiene.")
        else:
            opsec_leak_reasons.append(f"Standard operational profile ({browser_name}).")

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "evidence_sha256": evidence_hash,
        "browser": {
            "id": browser_id,
            "name": browser_name,
            "primary_category": primary_category,
            "engine": engine,
            "risk_tier": risk_tier,
            "confidence_pct": int(confidence * 100)
        },
        "crime_pattern_profile": {
            "behavioral_summary": crime_behavior,
            "opsec_vulnerabilities": opsec_vulnerabilities,
            "forensic_deanon_vectors": deanon_vectors,
            "typical_crime_contexts": typical_crime_contexts
        },
        "opsec_failure_detected": opsec_leak_detected,
        "investigative_findings": opsec_leak_reasons,
        "network_context": {
            "ip_address": ip_address,
            "is_tor_exit_subnet": is_tor_ip,
            "source_context": source_context
        },
        "recommended_pivot": (
            f"DE-ANONYMIZE OPERATOR: Exploit {browser_name} vulnerabilities ({deanon_vectors[0]}). Subpoena client telemetry or correlate canvas hashes across clearnet forums."
            if opsec_leak_detected else f"Correlate operational diurnal timing, PGP cryptographic keys, and crypto deposit clusters."
        )
    }

def get_browser_crime_taxonomy_catalog() -> Dict[str, Any]:
    """
    Returns the complete organized catalog of all 80+ browsers across the 8 required categories,
    complete with stats, risk distributions, and behavioral crime patterns.
    """
    categories_breakdown: Dict[str, List[Dict[str, Any]]] = {cat: [] for cat in CATEGORY_NAMES}
    risk_tier_counts: Dict[str, int] = {}

    for b in BROWSER_REGISTRY:
        tier = b["risk_tier"]
        risk_tier_counts[tier] = risk_tier_counts.get(tier, 0) + 1
        
        # Add to all relevant category lists
        for cat in b.get("categories", [b["primary_category"]]):
            if cat in categories_breakdown:
                categories_breakdown[cat].append({
                    "id": b["id"],
                    "name": b["name"],
                    "engine": b["engine"],
                    "risk_tier": b["risk_tier"],
                    "sample_ua": b["sample_ua"],
                    "crime_behavior": b["crime_behavior"],
                    "opsec_vulnerabilities": b["opsec_vulnerabilities"],
                    "deanon_vectors": b["deanon_vectors"],
                    "typical_crime_contexts": b["typical_crime_contexts"]
                })

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_browsers_indexed": len(BROWSER_REGISTRY),
        "total_categories": len(CATEGORY_NAMES),
        "categories_list": CATEGORY_NAMES,
        "risk_tier_distribution": risk_tier_counts,
        "catalog_by_category": categories_breakdown,
        "complete_registry": BROWSER_REGISTRY
    }
