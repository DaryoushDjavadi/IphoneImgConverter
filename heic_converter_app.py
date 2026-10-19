"""
iPhone HEIC → JPEG Konverter
Portables Windows-Programm ohne Installation.
"""

from __future__ import annotations

import json
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from converter_core import collect_heic_files, convert_many


APP_NAME = "iPhone Foto-Konverter"
APP_VERSION = "1.0.0"
SETTINGS_FILE = "einstellungen.json"


def app_dir() -> Path:
    """Ordner neben der EXE (PyInstaller) bzw. neben dem Skript."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def settings_path() -> Path:
    return app_dir() / SETTINGS_FILE


def load_settings() -> dict:
    defaults = {
        "output_dir": "",
        "delete_original": False,
        "quality": 95,
    }
    path = settings_path()
    if not path.exists():
        return defaults
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        defaults.update({k: data[k] for k in defaults if k in data})
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return defaults


def save_settings(settings: dict) -> None:
    path = settings_path()
    path.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


class SettingsWindow(tk.Toplevel):
    def __init__(self, master: "App") -> None:
        super().__init__(master)
        self.master_app = master
        self.title("Einstellungen")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        pad = {"padx": 14, "pady": 8}
        frame = ttk.Frame(self, padding=16)
        frame.grid(sticky="nsew")

        ttk.Label(
            frame,
            text="Ausgabe-Ordner für die JPEG-Bilder",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", **pad)

        ttk.Label(
            frame,
            text=(
                "Leer lassen = JPEGs landen im gleichen Ordner "
                "wie die HEIC-Dateien."
            ),
            wraplength=420,
        ).grid(row=1, column=0, columnspan=3, sticky="w", padx=14, pady=(0, 8))

        self.output_var = tk.StringVar(value=master.settings.get("output_dir", ""))
        entry = ttk.Entry(frame, textvariable=self.output_var, width=48)
        entry.grid(row=2, column=0, columnspan=2, sticky="ew", padx=(14, 6), pady=4)

        ttk.Button(frame, text="Ordner wählen…", command=self._pick_folder).grid(
            row=2, column=2, padx=(0, 14), pady=4
        )
        ttk.Button(frame, text="Leeren", command=lambda: self.output_var.set("")).grid(
            row=3, column=2, padx=(0, 14), pady=4, sticky="e"
        )

        ttk.Label(frame, text="JPEG-Qualität (1–100):").grid(
            row=4, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        self.quality_var = tk.IntVar(value=int(master.settings.get("quality", 95)))
        quality = ttk.Spinbox(
            frame,
            from_=50,
            to=100,
            textvariable=self.quality_var,
            width=6,
        )
        quality.grid(row=4, column=1, sticky="w", pady=(12, 4))

        btn_row = ttk.Frame(frame)
        btn_row.grid(row=5, column=0, columnspan=3, sticky="e", padx=14, pady=(16, 4))
        ttk.Button(btn_row, text="Abbrechen", command=self.destroy).pack(
            side="right", padx=(8, 0)
        )
        ttk.Button(btn_row, text="Speichern", command=self._save).pack(side="right")

        self.bind("<Escape>", lambda _e: self.destroy())
        self.update_idletasks()
        self._center_on_parent()

    def _center_on_parent(self) -> None:
        self.update_idletasks()
        px = self.master.winfo_rootx()
        py = self.master.winfo_rooty()
        pw = self.master.winfo_width()
        ph = self.master.winfo_height()
        w = self.winfo_width()
        h = self.winfo_height()
        self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")

    def _pick_folder(self) -> None:
        chosen = filedialog.askdirectory(
            parent=self,
            title="Ausgabe-Ordner wählen",
            initialdir=self.output_var.get() or str(Path.home()),
        )
        if chosen:
            self.output_var.set(chosen)

    def _save(self) -> None:
        quality = int(self.quality_var.get())
        if quality < 50 or quality > 100:
            messagebox.showwarning(
                "Qualität",
                "Bitte eine Qualität zwischen 50 und 100 wählen.",
                parent=self,
            )
            return
        self.master_app.settings["output_dir"] = self.output_var.get().strip()
        self.master_app.settings["quality"] = quality
        save_settings(self.master_app.settings)
        self.master_app.refresh_output_hint()
        self.destroy()


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME}  v{APP_VERSION}")
        self.minsize(560, 480)
        self.geometry("640x520")

        self.settings = load_settings()
        self.files: list[Path] = []
        self._busy = False

        self._build_style()
        self._build_ui()
        self.refresh_output_hint()

        # Drag & Drop, falls tkinterdnd2 verfügbar (optional)
        self._try_enable_dnd()

    def _build_style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Hint.TLabel", foreground="#444444")
        style.configure("Big.TButton", font=("Segoe UI", 11, "bold"), padding=10)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text=APP_NAME, style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            root,
            text=(
                "Wandelt iPhone-Fotos (HEIC) in normale JPEG-Bilder um – "
                "die jeder Windows-PC öffnen kann."
            ),
            style="Hint.TLabel",
            wraplength=580,
        ).pack(anchor="w", pady=(4, 14))

        btn_row = ttk.Frame(root)
        btn_row.pack(fill="x")
        ttk.Button(
            btn_row, text="Fotos auswählen…", command=self.add_files
        ).pack(side="left")
        ttk.Button(
            btn_row, text="Ordner auswählen…", command=self.add_folder
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            btn_row, text="Liste leeren", command=self.clear_files
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            btn_row, text="Einstellungen…", command=self.open_settings
        ).pack(side="right")

        list_frame = ttk.LabelFrame(root, text="Ausgewählte HEIC-Dateien", padding=8)
        list_frame.pack(fill="both", expand=True, pady=(14, 8))

        self.listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            activestyle="dotbox",
            font=("Consolas", 9),
        )
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.listbox.yview
        )
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.count_label = ttk.Label(root, text="0 Dateien ausgewählt")
        self.count_label.pack(anchor="w")

        self.output_hint = ttk.Label(root, style="Hint.TLabel", wraplength=580)
        self.output_hint.pack(anchor="w", pady=(2, 8))

        self.delete_var = tk.BooleanVar(
            value=bool(self.settings.get("delete_original", False))
        )
        ttk.Checkbutton(
            root,
            text="Original-HEIC nach erfolgreicher Konvertierung löschen",
            variable=self.delete_var,
            command=self._persist_delete_flag,
        ).pack(anchor="w", pady=(0, 10))

        self.progress = ttk.Progressbar(root, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 6))

        self.status_var = tk.StringVar(value="Bereit.")
        ttk.Label(root, textvariable=self.status_var).pack(anchor="w", pady=(0, 10))

        self.convert_btn = ttk.Button(
            root,
            text="Jetzt in JPEG umwandeln",
            style="Big.TButton",
            command=self.start_convert,
        )
        self.convert_btn.pack(fill="x")

    def _try_enable_dnd(self) -> None:
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore

            # Nur Hinweis: ohne TkinterDnD-Root funktioniert DnD oft nicht.
            # Wir registrieren trotzdem, falls die Umgebung es erlaubt.
            self.listbox.drop_target_register(DND_FILES)
            self.listbox.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

    def _on_drop(self, event) -> None:  # noqa: ANN001
        raw = event.data
        # Windows liefert Pfade oft in {…}
        parts: list[str] = []
        current = ""
        in_brace = False
        for ch in raw:
            if ch == "{":
                in_brace = True
                current = ""
            elif ch == "}":
                in_brace = False
                parts.append(current)
                current = ""
            elif ch == " " and not in_brace:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += ch
        if current:
            parts.append(current)
        self._add_paths([Path(p) for p in parts if p])

    def refresh_output_hint(self) -> None:
        out = (self.settings.get("output_dir") or "").strip()
        if out:
            text = f"Ausgabe-Ordner: {out}"
        else:
            text = (
                "Ausgabe-Ordner: gleicher Ordner wie die HEIC-Dateien "
                "(änderbar unter Einstellungen)."
            )
        self.output_hint.configure(text=text)

    def _persist_delete_flag(self) -> None:
        self.settings["delete_original"] = bool(self.delete_var.get())
        save_settings(self.settings)

    def open_settings(self) -> None:
        if self._busy:
            return
        SettingsWindow(self)

    def add_files(self) -> None:
        if self._busy:
            return
        paths = filedialog.askopenfilenames(
            parent=self,
            title="HEIC-Fotos auswählen",
            filetypes=[
                ("iPhone-Fotos (HEIC/HEIF)", "*.heic *.HEIC *.heif *.HEIF"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if paths:
            self._add_paths([Path(p) for p in paths])

    def add_folder(self) -> None:
        if self._busy:
            return
        folder = filedialog.askdirectory(
            parent=self,
            title="Ordner mit HEIC-Fotos wählen",
        )
        if folder:
            self._add_paths([Path(folder)])

    def _add_paths(self, paths: list[Path]) -> None:
        new_files = collect_heic_files(paths)
        if not new_files:
            messagebox.showinfo(
                "Keine HEIC-Dateien",
                "In der Auswahl wurden keine HEIC/HEIF-Dateien gefunden.",
                parent=self,
            )
            return
        existing = {p.resolve() for p in self.files}
        added = 0
        for f in new_files:
            if f.resolve() not in existing:
                self.files.append(f)
                existing.add(f.resolve())
                added += 1
        self._refresh_list()
        self.status_var.set(f"{added} Datei(en) hinzugefügt.")

    def clear_files(self) -> None:
        if self._busy:
            return
        self.files.clear()
        self._refresh_list()
        self.status_var.set("Liste geleert.")

    def _refresh_list(self) -> None:
        self.listbox.delete(0, tk.END)
        for f in self.files:
            self.listbox.insert(tk.END, str(f))
        n = len(self.files)
        self.count_label.configure(
            text=f"{n} Datei{'en' if n != 1 else ''} ausgewählt"
        )

    def start_convert(self) -> None:
        if self._busy:
            return
        if not self.files:
            messagebox.showinfo(
                "Keine Dateien",
                "Bitte zuerst HEIC-Fotos oder einen Ordner auswählen.",
                parent=self,
            )
            return

        delete = bool(self.delete_var.get())
        if delete:
            ok = messagebox.askyesno(
                "Originale löschen?",
                (
                    "Die Original-HEIC-Dateien werden nach erfolgreicher "
                    "Umwandlung gelöscht.\n\n"
                    "Bist du sicher? Das lässt sich nicht rückgängig machen."
                ),
                parent=self,
                icon="warning",
            )
            if not ok:
                return

        out_raw = (self.settings.get("output_dir") or "").strip()
        output_dir = Path(out_raw) if out_raw else None
        if output_dir is not None:
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                messagebox.showerror(
                    "Ausgabe-Ordner",
                    f"Der Ausgabe-Ordner kann nicht erstellt werden:\n{exc}",
                    parent=self,
                )
                return

        self._busy = True
        self.convert_btn.configure(state="disabled")
        self.progress.configure(maximum=len(self.files), value=0)
        self.status_var.set("Konvertierung läuft…")
        self.settings["delete_original"] = delete
        save_settings(self.settings)

        sources = list(self.files)
        quality = int(self.settings.get("quality", 95))

        def worker() -> None:
            def on_progress(index: int, total: int, result) -> None:  # noqa: ANN001
                self.after(
                    0,
                    lambda: self._update_progress(index, total, result),
                )

            results = convert_many(
                sources,
                output_dir,
                quality=quality,
                delete_original=delete,
                on_progress=on_progress,
            )
            self.after(0, lambda: self._finish(results))

        threading.Thread(target=worker, daemon=True).start()

    def _update_progress(self, index: int, total: int, result) -> None:  # noqa: ANN001
        self.progress.configure(value=index)
        name = result.source.name
        if result.success:
            self.status_var.set(f"{index}/{total}: {name} → OK")
        else:
            self.status_var.set(f"{index}/{total}: {name} → Fehler")

    def _finish(self, results) -> None:  # noqa: ANN001
        self._busy = False
        self.convert_btn.configure(state="normal")

        ok = [r for r in results if r.success]
        fail = [r for r in results if not r.success]

        # Erfolgreich konvertierte aus der Liste entfernen
        ok_sources = {r.source.resolve() for r in ok}
        self.files = [f for f in self.files if f.resolve() not in ok_sources]
        self._refresh_list()

        msg_lines = [
            f"Fertig: {len(ok)} von {len(results)} erfolgreich umgewandelt."
        ]
        if fail:
            msg_lines.append(f"\nFehlgeschlagen: {len(fail)}")
            for r in fail[:8]:
                msg_lines.append(f"• {r.source.name}: {r.error}")
            if len(fail) > 8:
                msg_lines.append(f"… und {len(fail) - 8} weitere")

        self.status_var.set(msg_lines[0])
        if fail:
            messagebox.showwarning("Ergebnis", "\n".join(msg_lines), parent=self)
        else:
            messagebox.showinfo("Ergebnis", "\n".join(msg_lines), parent=self)


def main() -> None:
    # Unter Windows: etwas schärfere Darstellung
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
