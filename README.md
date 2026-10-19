# iPhone Foto-Konverter

Hallo Jannis 👋

Dieses kleine Programm macht aus **iPhone-Fotos** normale **JPEG-Bilder**, die jeder Windows-PC ohne Extra-Software öffnen kann.

---

## Wozu brauchst du das?

Dein iPhone speichert Fotos oft als **HEIC**-Dateien (Dateiendung `.heic` oder `.HEIC`).

Das ist praktisch fürs Handy (kleinere Dateien, gute Qualität), aber unter Windows klappt das oft **nicht** oder nur umständlich:

- Windows-Fotoanzeige zeigt manchmal nur ein leeres Bild oder gar nichts
- WhatsApp, ältere Programme oder Online-Portale wollen oft **JPEG** (`.jpg`)
- Freunde oder die Arbeit können die Datei möglicherweise nicht öffnen

**Dieses Programm wandelt HEIC einfach in JPEG um.** Danach sind die Fotos „ganz normal“ und überall lesbar.

---

## Was du brauchst

Nur **eine Datei**:

`iPhone-Foto-Konverter.exe`

- **Keine Installation**
- Nichts in den „Programmen“ eintragen
- Einfach doppelklicken – fertig

Du kannst die EXE z. B. auf den Desktop legen oder auf einen USB-Stick kopieren und überall mitnehmen.

> Falls du die EXE noch nicht hast: Jemand mit Python kann sie einmal mit `build_windows.bat` bauen (siehe unten „Für den, der die EXE baut“). Danach brauchst **du** kein Python mehr.

---

## So benutzt du es (Schritt für Schritt)

1. **Doppelklick** auf `iPhone-Foto-Konverter.exe`
2. Klicke auf **„Fotos auswählen…“**  
   – oder auf **„Ordner auswählen…“**, wenn du einen ganzen Ordner voll HEIC-Fotos hast
3. Die Dateien erscheinen in der Liste
4. Optional:
   - Haken setzen bei **„Original-HEIC nach erfolgreicher Konvertierung löschen“**, wenn du die alten Dateien nicht mehr brauchst  
     *(Achtung: Weg ist weg. Nur anhaken, wenn du sicher bist.)*
5. Klicke auf **„Jetzt in JPEG umwandeln“**
6. Fertig – die neuen `.jpg`-Dateien liegen da, wo du es eingestellt hast

---

## Einstellungen: Wohin sollen die JPEGs?

Oben rechts → **„Einstellungen…“**

- **Ausgabe-Ordner wählen**  
  z. B. `C:\Users\Jannis\Bilder\Aus iPhone`  
  Dann landen **alle** umgewandelten Fotos in diesem Ordner.
- **Feld leer lassen**  
  Dann kommt jedes JPEG **neben** die jeweilige HEIC-Datei (gleicher Ordner).

Die Einstellung wird gespeichert (Datei `einstellungen.json` neben der EXE) und gilt beim nächsten Start wieder.

---

## Die Checkbox „Original löschen“

| Haken | Was passiert |
|--------|----------------|
| **Aus** (empfohlen am Anfang) | HEIC bleibt, JPEG kommt dazu. Du hast beides. |
| **An** | Nach erfolgreicher Umwandlung wird die HEIC gelöscht. Spart Speicherplatz. |

Tipp: Beim ersten Mal **ohne** Haken testen. Wenn die JPEGs gut aussehen, kannst du die HEICs später selbst löschen – oder den Haken setzen.

---

## Typischer Ablauf (Beispiel)

1. iPhone mit dem PC verbinden (oder Fotos per AirDrop/Cloud/USB kopieren)
2. HEIC-Dateien in einen Ordner legen, z. B. `Downloads\iPhone Fotos`
3. Programm starten → Ordner auswählen → umwandeln
4. Fertig: JPEG-Bilder, die Windows, WhatsApp & Co. verstehen

---

## Häufige Fragen

**Kann ich das Programm deinstallieren?**  
Es gibt nichts zu deinstallieren. Einfach die EXE (und ggf. `einstellungen.json`) löschen.

**Werden meine Fotos schlechter?**  
JPEG ist etwas „verlustbehaftet“, aber mit der Standard-Qualität (95) sieht man den Unterschied für den Alltag praktisch nicht. Für WhatsApp, Ausdruck und Familienalbum absolut ausreichend.

**Was ist mit Live Photos / Videos?**  
Das Programm macht nur **Fotos** (HEIC/HEIF → JPEG). Videos (`.mov` usw.) lässt es in Ruhe.

**Es passiert nichts / Windows warnt vor der EXE?**  
Windows kennt den Hersteller nicht und zeigt manchmal „Windows hat den PC geschützt“. Dann auf **Weitere Informationen** → **Trotzdem ausführen** klicken – sofern du die Datei von einer vertrauenswürdigen Person hast.

**Fehler bei einer Datei?**  
Die anderen Dateien werden trotzdem fertig. Am Ende siehst du eine Meldung, welche Datei(en) Probleme hatten.

---

## Kurz: Der Nutzen in einem Satz

> Aus iPhone-Fotos (HEIC) machst du mit einem Klick normale JPEG-Bilder – ohne Installation, ohne IT-Studium.

Viel Erfolg – und bei Fragen einfach melden.

---

## Für den, der die EXE baut (nicht nötig für den Alltag)

Auf einem Windows-PC mit installiertem [Python](https://www.python.org/downloads/) (Haken bei „Add to PATH“):

1. Diesen Ordner öffnen
2. Doppelklick auf `build_windows.bat`
3. Fertige Datei liegt unter `dist\iPhone-Foto-Konverter.exe`
4. Diese eine EXE an Jannis weitergeben

Technische Dateien im Projekt:

| Datei | Bedeutung |
|--------|-----------|
| `heic_converter_app.py` | Das Programm (Fenster) |
| `converter_core.py` | Die eigentliche Umwandlung |
| `requirements.txt` | Benötigte Python-Pakete |
| `build_windows.bat` | Baut die portable EXE |
