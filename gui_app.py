
# """
# Skin Insights — AI-Powered Skin Analysis Tool
# Complete GUI Application (Minimalist Design)
# """

# import cv2
# import numpy as np
# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox, scrolledtext
# from PIL import Image, ImageTk
# import threading
# import os
# from typing import Optional, Dict

# from skin_analyzer import SkinAnalyzer
# from report_generator import ReportGenerator
# from utils import resize_image
# import config

# # ──────────────── Color Palette ────────────────
# COLORS = {
#     "bg_primary": "#FFFFFF",
#     "bg_secondary": "#F5F5F5",
#     "bg_card": "#FAFAFA",
#     "bg_dark": "#1A1A1A",
#     "accent": "#E85D3A",
#     "accent_hover": "#D14E2E",
#     "text_primary": "#1A1A1A",
#     "text_secondary": "#555555",
#     "text_light": "#999999",
#     "border": "#E0E0E0",
#     "border_light": "#F0F0F0",
#     "green": "#2ECC71",
#     "green_dark": "#27AE60",
#     "yellow": "#F39C12",
#     "red": "#E74C3C",
#     "blue": "#3498DB",
#     "purple": "#8E44AD",
#     "score_excellent": "#2ECC71",
#     "score_good": "#27AE60",
#     "score_average": "#F39C12",
#     "score_poor": "#E74C3C",
#     "bar_bg": "#EEEEEE",
#     "white": "#FFFFFF",
# }


# class SkinAnalysisApp:
#     """Professional Skin Analysis GUI — Minimalist Design."""

#     def __init__(self):
#         # ── Window Setup ──
#         self.root = tk.Tk()
#         self.root.title("Skin Insights - AI Skin Analysis")
#         self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
#         self.root.configure(bg=COLORS["bg_primary"])
#         self.root.minsize(900, 600)
#         self.root.resizable(True, True)

#         # ── State ──
#         self.image: Optional[np.ndarray] = None
#         self.results: Optional[Dict] = None
#         self.visualizations: Optional[Dict] = None
#         self.is_analyzing = False

#         # ── Initialize analyzer ──
#         self.analyzer = SkinAnalyzer(use_mediapipe=config.USE_MEDIAPIPE)
#         self.report_gen = ReportGenerator()

#         # ── Build UI ──
#         self._build_navigation()
#         self._build_main_area()
#         self._show_upload_screen()

#         # ── Keyboard shortcuts ──
#         self.root.bind("<Control-o>", lambda e: self._load_image())
#         self.root.bind("<Control-s>", lambda e: self._save_results())

#     # ════════════════════════════════════════════════════════════
#     #  NAVIGATION BAR
#     # ════════════════════════════════════════════════════════════

#     def _build_navigation(self):
#         """Build top navigation bar."""
#         self.nav = tk.Frame(
#             self.root, bg=COLORS["white"], height=60,
#             highlightthickness=1, highlightbackground=COLORS["border"]
#         )
#         self.nav.pack(fill=tk.X, side=tk.TOP)
#         self.nav.pack_propagate(False)

#         # ── Left: Logo & Title ──
#         left_frame = tk.Frame(self.nav, bg=COLORS["white"])
#         left_frame.pack(side=tk.LEFT, padx=20)

#         tk.Label(
#             left_frame, text="Skin Insights",
#             font=("Segoe UI", 17, "bold"),
#             fg=COLORS["text_primary"], bg=COLORS["white"]
#         ).pack(side=tk.LEFT)

#         tk.Label(
#             left_frame, text="  |  AI-Powered Analysis",
#             font=("Segoe UI", 10),
#             fg=COLORS["text_light"], bg=COLORS["white"]
#         ).pack(side=tk.LEFT, padx=(5, 0))

#         # ── Right: Action Buttons ──
#         right_frame = tk.Frame(self.nav, bg=COLORS["white"])
#         right_frame.pack(side=tk.RIGHT, padx=20)

#         self.btn_save = self._make_nav_button(
#             right_frame, "Save Report", self._save_results,
#             bg=COLORS["green_dark"], state=tk.DISABLED
#         )
#         self.btn_save.pack(side=tk.RIGHT, padx=5)

#         self.btn_analyze = self._make_nav_button(
#             right_frame, "Analyze Skin", self._start_analysis,
#             bg=COLORS["accent"], state=tk.DISABLED
#         )
#         self.btn_analyze.pack(side=tk.RIGHT, padx=5)

#         self.btn_camera = self._make_nav_button(
#             right_frame, "Camera", self._capture_from_camera,
#             bg=COLORS["blue"]
#         )
#         self.btn_camera.pack(side=tk.RIGHT, padx=5)

#         self.btn_upload = self._make_nav_button(
#             right_frame, "Upload Photo", self._load_image,
#             bg=COLORS["text_primary"]
#         )
#         self.btn_upload.pack(side=tk.RIGHT, padx=5)

#     def _make_nav_button(self, parent, text, command, bg, state=tk.NORMAL):
#         """Create a styled navigation button."""
#         btn = tk.Button(
#             parent, text=text, command=command,
#             font=("Segoe UI", 10, "bold"),
#             fg="white", bg=bg,
#             activebackground=bg, activeforeground="white",
#             bd=0, padx=16, pady=6,
#             cursor="hand2", state=state, relief=tk.FLAT
#         )
#         return btn

#     # ════════════════════════════════════════════════════════════
#     #  MAIN CONTENT AREA
#     # ════════════════════════════════════════════════════════════

#     def _build_main_area(self):
#         """Build main content container."""
#         self.main_frame = tk.Frame(self.root, bg=COLORS["bg_secondary"])
#         self.main_frame.pack(fill=tk.BOTH, expand=True)

#     def _clear_main(self):
#         """Clear all widgets from main area."""
#         for widget in self.main_frame.winfo_children():
#             widget.destroy()

#     # ════════════════════════════════════════════════════════════
#     #  SCREEN 1: UPLOAD SCREEN
#     # ════════════════════════════════════════════════════════════

#     def _show_upload_screen(self):
#         """Show the initial upload/welcome screen."""
#         self._clear_main()

#         # Center container
#         center = tk.Frame(self.main_frame, bg=COLORS["bg_secondary"])
#         center.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

#         # Icon
#         tk.Label(
#             center, text="SKIN INSIGHTS",
#             font=("Segoe UI", 28, "bold"),
#             fg=COLORS["accent"], bg=COLORS["bg_secondary"]
#         ).pack(pady=(0, 5))

#         # Tagline
#         tk.Label(
#             center, text="Upload a selfie to get your personalized skin analysis",
#             font=("Segoe UI", 14),
#             fg=COLORS["text_primary"], bg=COLORS["bg_secondary"]
#         ).pack(pady=(0, 5))

#         tk.Label(
#             center,
#             text="For best results: front-facing photo, good lighting, no makeup, no filters",
#             font=("Segoe UI", 10),
#             fg=COLORS["text_light"], bg=COLORS["bg_secondary"]
#         ).pack(pady=(0, 25))

#         # Buttons
#         btn_row = tk.Frame(center, bg=COLORS["bg_secondary"])
#         btn_row.pack(pady=10)

#         upload_btn = tk.Button(
#             btn_row, text="Upload Photo",
#             command=self._load_image,
#             font=("Segoe UI", 13, "bold"),
#             fg="white", bg=COLORS["accent"],
#             activebackground=COLORS["accent_hover"],
#             activeforeground="white",
#             bd=0, padx=40, pady=14, cursor="hand2", relief=tk.FLAT
#         )
#         upload_btn.pack(side=tk.LEFT, padx=10)

#         camera_btn = tk.Button(
#             btn_row, text="Use Camera",
#             command=self._capture_from_camera,
#             font=("Segoe UI", 13, "bold"),
#             fg=COLORS["text_primary"], bg=COLORS["white"],
#             activebackground=COLORS["bg_secondary"],
#             bd=2, padx=40, pady=12, cursor="hand2", relief=tk.SOLID
#         )
#         camera_btn.pack(side=tk.LEFT, padx=10)

#         # Features list
#         features_frame = tk.Frame(center, bg=COLORS["bg_secondary"])
#         features_frame.pack(pady=(30, 0))

#         features = [
#             "Acne & Blemish Detection",
#             "Skin Type Analysis",
#             "Personalized Routine",
#             "Ingredient Recommendations",
#         ]

#         for feat in features:
#             tk.Label(
#                 features_frame,
#                 text=f"  [+]  {feat}",
#                 font=("Segoe UI", 10),
#                 fg=COLORS["text_secondary"],
#                 bg=COLORS["bg_secondary"], anchor=tk.W
#             ).pack(anchor=tk.W, pady=2)

#     # ════════════════════════════════════════════════════════════
#     #  SCREEN 2: PREVIEW SCREEN
#     # ════════════════════════════════════════════════════════════

#     def _show_preview_screen(self):
#         """Show image preview before analysis."""
#         self._clear_main()

#         center = tk.Frame(self.main_frame, bg=COLORS["bg_secondary"])
#         center.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

#         # Image
#         if self.image is not None:
#             display = resize_image(self.image, 350, 350)
#             rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
#             pil_img = Image.fromarray(rgb)
#             tk_img = ImageTk.PhotoImage(pil_img)

#             img_label = tk.Label(
#                 center, image=tk_img, bg=COLORS["bg_secondary"],
#                 bd=3, relief=tk.GROOVE
#             )
#             img_label.image = tk_img
#             img_label.pack(pady=(0, 15))

#         # Status text
#         tk.Label(
#             center, text="Photo uploaded successfully!",
#             font=("Segoe UI", 15, "bold"),
#             fg=COLORS["text_primary"], bg=COLORS["bg_secondary"]
#         ).pack(pady=(5, 5))

#         tk.Label(
#             center, text="Click below to start your skin analysis",
#             font=("Segoe UI", 11),
#             fg=COLORS["text_light"], bg=COLORS["bg_secondary"]
#         ).pack(pady=(0, 15))

#         # Buttons
#         btn_row = tk.Frame(center, bg=COLORS["bg_secondary"])
#         btn_row.pack(pady=5)

#         analyze_btn = tk.Button(
#             btn_row, text="Analyze My Skin",
#             command=self._start_analysis,
#             font=("Segoe UI", 14, "bold"),
#             fg="white", bg=COLORS["accent"],
#             activebackground=COLORS["accent_hover"],
#             bd=0, padx=45, pady=14, cursor="hand2", relief=tk.FLAT
#         )
#         analyze_btn.pack(side=tk.LEFT, padx=8)

#         change_btn = tk.Button(
#             btn_row, text="Change Photo",
#             command=self._load_image,
#             font=("Segoe UI", 11),
#             fg=COLORS["text_secondary"], bg=COLORS["white"],
#             bd=1, padx=20, pady=12, cursor="hand2", relief=tk.SOLID
#         )
#         change_btn.pack(side=tk.LEFT, padx=8)

#     # ════════════════════════════════════════════════════════════
#     #  SCREEN 3: LOADING SCREEN
#     # ════════════════════════════════════════════════════════════

#     def _show_loading_screen(self):
#         """Show loading/analyzing screen."""
#         self._clear_main()

#         center = tk.Frame(self.main_frame, bg=COLORS["bg_secondary"])
#         center.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

#         tk.Label(
#             center, text="Analyzing Your Skin...",
#             font=("Segoe UI", 20, "bold"),
#             fg=COLORS["text_primary"], bg=COLORS["bg_secondary"]
#         ).pack(pady=(0, 10))

#         self.loading_status = tk.Label(
#             center, text="Detecting face and skin regions...",
#             font=("Segoe UI", 11),
#             fg=COLORS["text_light"], bg=COLORS["bg_secondary"]
#         )
#         self.loading_status.pack(pady=(0, 20))

#         # Progress bar
#         style = ttk.Style()
#         style.configure(
#             "Custom.Horizontal.TProgressbar",
#             troughcolor=COLORS["bar_bg"],
#             background=COLORS["accent"],
#             thickness=8
#         )

#         self.progress = ttk.Progressbar(
#             center, mode="indeterminate", length=350,
#             style="Custom.Horizontal.TProgressbar"
#         )
#         self.progress.pack(pady=10)
#         self.progress.start(12)

#         tk.Label(
#             center, text="This usually takes 10-20 seconds",
#             font=("Segoe UI", 9),
#             fg=COLORS["text_light"], bg=COLORS["bg_secondary"]
#         ).pack(pady=(10, 0))

#     # ════════════════════════════════════════════════════════════
#     #  SCREEN 4: RESULTS SCREEN (MAIN)
#     # ════════════════════════════════════════════════════════════

#     def _show_results_screen(self):
#         """Show full analysis results — Minimalist scrollable layout."""
#         self._clear_main()

#         r = self.results
#         if r is None:
#             return

#         # ── Scrollable Canvas Setup ──
#         canvas = tk.Canvas(
#             self.main_frame, bg=COLORS["bg_secondary"],
#             highlightthickness=0, bd=0
#         )
#         scrollbar = ttk.Scrollbar(
#             self.main_frame, orient=tk.VERTICAL, command=canvas.yview
#         )
#         self.scroll_content = tk.Frame(canvas, bg=COLORS["bg_secondary"])

#         self.scroll_content.bind(
#             "<Configure>",
#             lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
#         )

#         canvas_window = canvas.create_window(
#             (0, 0), window=self.scroll_content, anchor="nw",
#             width=config.WINDOW_WIDTH - 30
#         )

#         # Resize inner frame when canvas resizes
#         def on_canvas_resize(event):
#             canvas.itemconfig(canvas_window, width=event.width)
#         canvas.bind("<Configure>", on_canvas_resize)

#         canvas.configure(yscrollcommand=scrollbar.set)

#         # Mouse wheel scrolling
#         def on_mousewheel(event):
#             canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

#         canvas.bind_all("<MouseWheel>", on_mousewheel)

#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#         parent = self.scroll_content

#         # ═════════════════════════════════════════
#         # SECTION 1: HERO — Photo + Score + Info
#         # ═════════════════════════════════════════
#         self._build_hero_section(parent, r)

#         # ═════════════════════════════════════════
#         # SECTION 2: SCORE BREAKDOWN
#         # ═════════════════════════════════════════
#         self._build_score_section(parent, r)

#         # ═════════════════════════════════════════
#         # SECTION 3: YOUR CONCERNS
#         # ═════════════════════════════════════════
#         self._build_concerns_section(parent, r)

#         # ═════════════════════════════════════════
#         # SECTION 4: PERSONALIZED TIPS
#         # ═════════════════════════════════════════
#         self._build_tips_section(parent, r)

#         # ═════════════════════════════════════════
#         # SECTION 5: RECOMMENDED INGREDIENTS
#         # ═════════════════════════════════════════
#         self._build_ingredients_section(parent, r)

#         # ═════════════════════════════════════════
#         # SECTION 6: MORNING ROUTINE
#         # ═════════════════════════════════════════
#         self._build_routine_section(parent, r, "morning")

#         # ═════════════════════════════════════════
#         # SECTION 7: NIGHT ROUTINE
#         # ═════════════════════════════════════════
#         self._build_routine_section(parent, r, "night")

#         # ═════════════════════════════════════════
#         # SECTION 8: WEEKLY TREATMENTS
#         # ═════════════════════════════════════════
#         self._build_weekly_section(parent, r)

#         # ═════════════════════════════════════════
#         # SECTION 9: LIFESTYLE TIPS
#         # ═════════════════════════════════════════
#         self._build_lifestyle_section(parent, r)

#         # ═════════════════════════════════════════
#         # SECTION 10: DISCLAIMER
#         # ═════════════════════════════════════════
#         self._build_disclaimer(parent)

#         # Bottom spacer
#         tk.Frame(parent, height=60, bg=COLORS["bg_secondary"]).pack()

#     # ════════════════════════════════════════════════════════════
#     #  SECTION BUILDERS
#     # ════════════════════════════════════════════════════════════

#     def _build_hero_section(self, parent, r):
#         """Build hero section with photo, score, and quick stats."""
#         hero_card = tk.Frame(parent, bg=COLORS["white"], bd=0)
#         hero_card.pack(fill=tk.X, padx=20, pady=(20, 10))

#         hero_inner = tk.Frame(hero_card, bg=COLORS["white"])
#         hero_inner.pack(fill=tk.X, padx=30, pady=25)

#         # ── Left: Photo ──
#         photo_frame = tk.Frame(hero_inner, bg=COLORS["white"])
#         photo_frame.pack(side=tk.LEFT, padx=(0, 25))

#         if self.image is not None:
#             display = resize_image(self.image, 250, 250)
#             rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
#             pil_img = Image.fromarray(rgb)
#             tk_img = ImageTk.PhotoImage(pil_img)

#             img_label = tk.Label(
#                 photo_frame, image=tk_img, bg=COLORS["white"],
#                 bd=2, relief=tk.GROOVE
#             )
#             img_label.image = tk_img
#             img_label.pack()

#         # ── Right: Score + Info ──
#         info_frame = tk.Frame(hero_inner, bg=COLORS["white"])
#         info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#         # Title
#         tk.Label(
#             info_frame, text="Your Skin Health Score",
#             font=("Segoe UI", 11),
#             fg=COLORS["text_secondary"], bg=COLORS["white"]
#         ).pack(anchor=tk.W)

#         # Score
#         score = r.get("overall_score", 0)
#         score_color = self._get_score_color(score)

#         score_row = tk.Frame(info_frame, bg=COLORS["white"])
#         score_row.pack(anchor=tk.W, pady=(5, 0))

#         tk.Label(
#             score_row, text=f"{score:.0f}",
#             font=("Segoe UI", 48, "bold"),
#             fg=score_color, bg=COLORS["white"]
#         ).pack(side=tk.LEFT)

#         tk.Label(
#             score_row, text=" / 100",
#             font=("Segoe UI", 16),
#             fg=COLORS["text_light"], bg=COLORS["white"]
#         ).pack(side=tk.LEFT, pady=(18, 0))

#         # Grade
#         tk.Label(
#             info_frame, text=r.get("overall_grade", ""),
#             font=("Segoe UI", 13, "bold"),
#             fg=score_color, bg=COLORS["white"]
#         ).pack(anchor=tk.W, pady=(0, 12))

#         # Quick stats cards
#         stats_row = tk.Frame(info_frame, bg=COLORS["white"])
#         stats_row.pack(anchor=tk.W, pady=(5, 0))

#         skin_type = r.get("skin_type", {}).get("type", "N/A")
#         skin_tone = r.get("skin_tone", {}).get("category", "N/A")
#         skin_age = r.get("skin_age", {}).get("age_range", "N/A")
#         undertone = r.get("skin_tone", {}).get("undertone", {}).get("type", "N/A")

#         stats = [
#             ("Skin Type", skin_type),
#             ("Skin Tone", skin_tone),
#             ("Undertone", undertone.capitalize()),
#             ("Skin Age", skin_age),
#         ]

#         for label_text, value_text in stats:
#             stat_card = tk.Frame(
#                 stats_row, bg=COLORS["bg_secondary"],
#                 padx=14, pady=8
#             )
#             stat_card.pack(side=tk.LEFT, padx=(0, 8))

#             tk.Label(
#                 stat_card, text=label_text,
#                 font=("Segoe UI", 8),
#                 fg=COLORS["text_light"], bg=COLORS["bg_secondary"]
#             ).pack()

#             tk.Label(
#                 stat_card, text=value_text,
#                 font=("Segoe UI", 11, "bold"),
#                 fg=COLORS["text_primary"], bg=COLORS["bg_secondary"]
#             ).pack()

#         # Skin age status
#         age_status = r.get("skin_age", {}).get("status", "")
#         if age_status:
#             tk.Label(
#                 info_frame, text=age_status,
#                 font=("Segoe UI", 10, "italic"),
#                 fg=COLORS["text_light"], bg=COLORS["white"]
#             ).pack(anchor=tk.W, pady=(10, 0))

#     def _build_score_section(self, parent, r):
#         """Build score breakdown section with proper labeled bars."""
#         self._section_title(parent, "Score Breakdown")

#         card = tk.Frame(parent, bg=COLORS["white"])
#         card.pack(fill=tk.X, padx=20, pady=(0, 10))

#         inner = tk.Frame(card, bg=COLORS["white"])
#         inner.pack(fill=tk.X, padx=25, pady=20)

#         # ── Column Headers ──
#         header = tk.Frame(inner, bg=COLORS["white"], height=25)
#         header.pack(fill=tk.X, pady=(0, 5))
#         header.pack_propagate(False)

#         h_label = tk.Frame(header, bg=COLORS["white"], width=170, height=25)
#         h_label.pack(side=tk.LEFT)
#         h_label.pack_propagate(False)
#         tk.Label(
#             h_label, text="CATEGORY",
#             font=("Segoe UI", 8, "bold"),
#             fg=COLORS["text_light"], bg=COLORS["white"]
#         ).place(x=0, rely=0.5, anchor=tk.W)

#         tk.Label(
#             header, text="",
#             bg=COLORS["white"]
#         ).pack(side=tk.LEFT, fill=tk.X, expand=True)

#         h_score = tk.Frame(header, bg=COLORS["white"], width=50, height=25)
#         h_score.pack(side=tk.LEFT)
#         h_score.pack_propagate(False)
#         tk.Label(
#             h_score, text="SCORE",
#             font=("Segoe UI", 8, "bold"),
#             fg=COLORS["text_light"], bg=COLORS["white"]
#         ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

#         h_status = tk.Frame(header, bg=COLORS["white"], width=100, height=25)
#         h_status.pack(side=tk.LEFT)
#         h_status.pack_propagate(False)
#         tk.Label(
#             h_status, text="STATUS",
#             font=("Segoe UI", 8, "bold"),
#             fg=COLORS["text_light"], bg=COLORS["white"]
#         ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

#         # Divider line
#         tk.Frame(inner, bg=COLORS["border"], height=1).pack(fill=tk.X, pady=(0, 8))

#         # ── Score Bars ──
#         score_items = [
#             ("Acne & Blemishes",
#              r.get("blemishes", {}).get("score", 75),
#              r.get("blemishes", {}).get("severity", "N/A")),
#             ("Pigmentation",
#              r.get("pigmentation", {}).get("score", 75),
#              r.get("pigmentation", {}).get("severity", "N/A")),
#             ("Wrinkles",
#              r.get("wrinkles", {}).get("overall_score", 75),
#              r.get("wrinkles", {}).get("severity", "N/A")),
#             ("Texture",
#              r.get("texture", {}).get("score", 75),
#              r.get("texture", {}).get("grade", "N/A")),
#             ("Pores",
#              r.get("pores", {}).get("score", 75),
#              r.get("pores", {}).get("severity", "N/A")),
#             ("Dark Circles",
#              r.get("dark_circles", {}).get("score", 75),
#              r.get("dark_circles", {}).get("severity", "N/A")),
#             ("Skin Evenness",
#              r.get("skin_tone", {}).get("evenness_score", 75),
#              "Even" if r.get("skin_tone", {}).get("evenness_score", 75) >= 70 else "Uneven"),
#         ]

#         for name, sc, severity in score_items:
#             self._build_score_bar(inner, name, sc, severity)

#     def _build_score_bar(self, parent, name, score, severity):
#         """Build a single score bar row with label, bar, score, status."""
#         row = tk.Frame(parent, bg=COLORS["white"], height=42)
#         row.pack(fill=tk.X, pady=4)
#         row.pack_propagate(False)

#         bar_color = self._get_score_color(score)

#         # ── 1. LABEL (left side) ──
#         label_box = tk.Frame(row, bg=COLORS["white"], width=170, height=42)
#         label_box.pack(side=tk.LEFT)
#         label_box.pack_propagate(False)

#         tk.Label(
#             label_box, text=name,
#             font=("Segoe UI", 11),
#             fg=COLORS["text_primary"], bg=COLORS["white"],
#             anchor=tk.W
#         ).place(x=0, rely=0.5, anchor=tk.W)

#         # ── 2. PROGRESS BAR (middle) ──
#         bar_frame = tk.Frame(row, bg=COLORS["white"], height=42)
#         bar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12)

#         bar_canvas = tk.Canvas(
#             bar_frame, bg=COLORS["bar_bg"], height=18,
#             highlightthickness=0, bd=0
#         )
#         bar_canvas.pack(fill=tk.X, pady=12)

#         def draw_bar(event=None):
#             bar_canvas.delete("all")
#             w = bar_canvas.winfo_width()
#             if w <= 1:
#                 w = 300
#             fill_w = max(4, int((score / 100) * w))

#             # Background
#             bar_canvas.create_rectangle(
#                 0, 0, w, 18,
#                 fill=COLORS["bar_bg"], outline=""
#             )

#             # Filled portion
#             bar_canvas.create_rectangle(
#                 0, 0, fill_w, 18,
#                 fill=bar_color, outline=""
#             )

#         bar_canvas.bind("<Configure>", draw_bar)

#         # ── 3. SCORE NUMBER (right) ──
#         score_box = tk.Frame(row, bg=COLORS["white"], width=50, height=42)
#         score_box.pack(side=tk.LEFT)
#         score_box.pack_propagate(False)

#         tk.Label(
#             score_box, text=f"{score:.0f}",
#             font=("Segoe UI", 12, "bold"),
#             fg=bar_color, bg=COLORS["white"]
#         ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

#         # ── 4. STATUS LABEL (far right) ──
#         status_box = tk.Frame(row, bg=COLORS["white"], width=100, height=42)
#         status_box.pack(side=tk.LEFT)
#         status_box.pack_propagate(False)

#         sev_text = str(severity).capitalize()
#         sev_color = self._get_severity_color(sev_text)

#         tk.Label(
#             status_box, text=sev_text,
#             font=("Segoe UI", 9, "bold"),
#             fg=sev_color, bg=COLORS["white"]
#         ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

#     def _build_concerns_section(self, parent, r):
#         """Build skin concerns section."""
#         concerns = r.get("recommendations", {}).get("concerns", [])
#         if not concerns:
#             return

#         # Skip if only "Great Skin" placeholder
#         if len(concerns) == 1 and "Great" in concerns[0].get("name", ""):
#             self._section_title(parent, "Your Skin Assessment")
#             card = tk.Frame(parent, bg=COLORS["white"])
#             card.pack(fill=tk.X, padx=20, pady=(0, 10))
#             tk.Label(
#                 card, text="Your skin looks great! No major concerns detected.",
#                 font=("Segoe UI", 13, "bold"),
#                 fg=COLORS["green"], bg=COLORS["white"],
#                 pady=25
#             ).pack()
#             return

#         self._section_title(parent, "Your Top Skin Concerns")

#         for concern in concerns[:5]:
#             card = tk.Frame(
#                 parent, bg=COLORS["white"],
#                 highlightthickness=1, highlightbackground=COLORS["border_light"]
#             )
#             card.pack(fill=tk.X, padx=20, pady=3)

#             inner = tk.Frame(card, bg=COLORS["white"])
#             inner.pack(fill=tk.X, padx=18, pady=12)

#             # Header row: name + severity badge
#             top_row = tk.Frame(inner, bg=COLORS["white"])
#             top_row.pack(fill=tk.X)

#             # Concern icon (text-based)
#             icon_map = {
#                 "Acne": "[!]",
#                 "Pigmentation": "[.]",
#                 "Fine Lines": "[~]",
#                 "Enlarged": "[o]",
#                 "Dark Circles": "(o)",
#                 "Uneven": "[#]",
#                 "Oiliness": "[~]",
#                 "Dryness": "[_]",
#                 "Great": "[*]",
#             }
#             icon = "[>]"
#             for key, val in icon_map.items():
#                 if key in concern.get("name", ""):
#                     icon = val
#                     break

#             tk.Label(
#                 top_row,
#                 text=f"{icon}  {concern['name']}",
#                 font=("Segoe UI", 12, "bold"),
#                 fg=COLORS["text_primary"], bg=COLORS["white"]
#             ).pack(side=tk.LEFT)

#             sev = concern.get("severity", "mild")
#             sev_color = self._get_severity_color(sev)

#             badge = tk.Label(
#                 top_row, text=f"  {sev.upper()}  ",
#                 font=("Segoe UI", 8, "bold"),
#                 fg="white", bg=sev_color
#             )
#             badge.pack(side=tk.RIGHT, padx=5)

#             # Details
#             details = concern.get("details", "")
#             if details:
#                 tk.Label(
#                     inner, text=details,
#                     font=("Segoe UI", 10),
#                     fg=COLORS["text_secondary"], bg=COLORS["white"],
#                     wraplength=700, justify=tk.LEFT, anchor=tk.W
#                 ).pack(anchor=tk.W, pady=(6, 0))

#     def _build_tips_section(self, parent, r):
#         """Build personalized tips section."""
#         tips = r.get("recommendations", {}).get("specific_tips", [])
#         if not tips:
#             return

#         self._section_title(parent, "Personalized Tips For You")

#         for tip in tips:
#             card = tk.Frame(
#                 parent, bg=COLORS["white"],
#                 highlightthickness=1, highlightbackground=COLORS["border_light"]
#             )
#             card.pack(fill=tk.X, padx=20, pady=3)

#             inner = tk.Frame(card, bg=COLORS["white"])
#             inner.pack(fill=tk.X, padx=18, pady=12)

#             # Urgency indicator
#             urgency = tip.get("urgency", "low")
#             urg_map = {"high": "[!!]", "medium": "[!]", "low": "[i]"}
#             urg_colors = {
#                 "high": COLORS["red"],
#                 "medium": COLORS["yellow"],
#                 "low": COLORS["green"]
#             }

#             title_row = tk.Frame(inner, bg=COLORS["white"])
#             title_row.pack(fill=tk.X)

#             tk.Label(
#                 title_row,
#                 text=f"{urg_map.get(urgency, '[i]')}  {tip['title']}",
#                 font=("Segoe UI", 11, "bold"),
#                 fg=COLORS["text_primary"], bg=COLORS["white"]
#             ).pack(side=tk.LEFT)

#             tk.Label(
#                 title_row,
#                 text=urgency.upper(),
#                 font=("Segoe UI", 8, "bold"),
#                 fg=urg_colors.get(urgency, COLORS["text_light"]),
#                 bg=COLORS["white"]
#             ).pack(side=tk.RIGHT)

#             tk.Label(
#                 inner, text=tip["tip"],
#                 font=("Segoe UI", 10),
#                 fg=COLORS["text_secondary"], bg=COLORS["white"],
#                 wraplength=700, justify=tk.LEFT, anchor=tk.W
#             ).pack(anchor=tk.W, pady=(6, 0))

#     def _build_ingredients_section(self, parent, r):
#         """Build recommended ingredients section."""
#         ingredients = r.get("recommendations", {}).get("recommended_ingredients", [])
#         if not ingredients:
#             return

#         self._section_title(parent, "Recommended Active Ingredients")

#         card = tk.Frame(parent, bg=COLORS["white"])
#         card.pack(fill=tk.X, padx=20, pady=(0, 10))

#         inner = tk.Frame(card, bg=COLORS["white"])
#         inner.pack(fill=tk.X, padx=20, pady=15)

#         for i, ing in enumerate(ingredients[:8]):
#             ing_frame = tk.Frame(inner, bg=COLORS["bg_secondary"])
#             ing_frame.pack(fill=tk.X, pady=4)

#             ing_inner = tk.Frame(ing_frame, bg=COLORS["bg_secondary"])
#             ing_inner.pack(fill=tk.X, padx=14, pady=10)

#             # Row 1: Name + Concentration
#             name_row = tk.Frame(ing_inner, bg=COLORS["bg_secondary"])
#             name_row.pack(fill=tk.X)

#             tk.Label(
#                 name_row,
#                 text=f"[{i+1}]  {ing.get('name', '')}",
#                 font=("Segoe UI", 11, "bold"),
#                 fg=COLORS["text_primary"], bg=COLORS["bg_secondary"]
#             ).pack(side=tk.LEFT)

#             tk.Label(
#                 name_row,
#                 text=ing.get("concentration", ""),
#                 font=("Segoe UI", 9, "bold"),
#                 fg=COLORS["accent"], bg=COLORS["bg_secondary"]
#             ).pack(side=tk.RIGHT)

#             # Row 2: Benefits
#             tk.Label(
#                 ing_inner,
#                 text=ing.get("benefits", ""),
#                 font=("Segoe UI", 10),
#                 fg=COLORS["text_secondary"], bg=COLORS["bg_secondary"],
#                 wraplength=650, justify=tk.LEFT, anchor=tk.W
#             ).pack(anchor=tk.W, pady=(3, 0))

#             # Row 3: Reason
#             tk.Label(
#                 ing_inner,
#                 text=ing.get("reason", ""),
#                 font=("Segoe UI", 9, "italic"),
#                 fg=COLORS["text_light"], bg=COLORS["bg_secondary"],
#                 anchor=tk.W
#             ).pack(anchor=tk.W, pady=(2, 0))

#     def _build_routine_section(self, parent, r, time_of_day):
#         """Build AM or PM routine section."""
#         routine = r.get("routine", {})
#         if not routine:
#             return

#         if time_of_day == "morning":
#             title = "Your Morning Routine (AM)"
#             steps = routine.get("morning_routine", [])
#         else:
#             title = "Your Night Routine (PM)"
#             steps = routine.get("night_routine", [])

#         if not steps:
#             return

#         self._section_title(parent, title)

#         card = tk.Frame(parent, bg=COLORS["white"])
#         card.pack(fill=tk.X, padx=20, pady=(0, 10))

#         inner = tk.Frame(card, bg=COLORS["white"])
#         inner.pack(fill=tk.X, padx=25, pady=20)

#         for step in steps:
#             step_frame = tk.Frame(inner, bg=COLORS["white"])
#             step_frame.pack(fill=tk.X, pady=6)

#             # Step number circle
#             step_num = step.get("step", "?")
#             num_label = tk.Label(
#                 step_frame,
#                 text=f"  {step_num}  ",
#                 font=("Segoe UI", 11, "bold"),
#                 fg="white", bg=COLORS["accent"]
#             )
#             num_label.pack(side=tk.LEFT, padx=(0, 12))

#             # Step details
#             details_frame = tk.Frame(step_frame, bg=COLORS["white"])
#             details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

#             tk.Label(
#                 details_frame,
#                 text=step.get("product", ""),
#                 font=("Segoe UI", 11, "bold"),
#                 fg=COLORS["text_primary"], bg=COLORS["white"],
#                 anchor=tk.W
#             ).pack(anchor=tk.W)

#             tk.Label(
#                 details_frame,
#                 text=step.get("ingredient", ""),
#                 font=("Segoe UI", 10),
#                 fg=COLORS["accent"], bg=COLORS["white"],
#                 anchor=tk.W
#             ).pack(anchor=tk.W)

#             how_to = step.get("how_to", "")
#             if how_to:
#                 tk.Label(
#                     details_frame,
#                     text=how_to,
#                     font=("Segoe UI", 9),
#                     fg=COLORS["text_light"], bg=COLORS["white"],
#                     wraplength=600, justify=tk.LEFT, anchor=tk.W
#                 ).pack(anchor=tk.W, pady=(2, 0))

#             # Separator
#             tk.Frame(
#                 inner, bg=COLORS["border_light"], height=1
#             ).pack(fill=tk.X, pady=4)

#         # Routine notes
#         notes = r.get("routine", {}).get("notes", [])
#         if notes:
#             notes_frame = tk.Frame(inner, bg=COLORS["bg_secondary"])
#             notes_frame.pack(fill=tk.X, pady=(8, 0))
#             notes_inner = tk.Frame(notes_frame, bg=COLORS["bg_secondary"])
#             notes_inner.pack(fill=tk.X, padx=12, pady=8)

#             for note in notes:
#                 clean_note = self._clean_text(note)
#                 tk.Label(
#                     notes_inner, text=f"  {clean_note}",
#                     font=("Segoe UI", 9),
#                     fg=COLORS["text_secondary"],
#                     bg=COLORS["bg_secondary"], anchor=tk.W,
#                     wraplength=600, justify=tk.LEFT
#                 ).pack(anchor=tk.W, pady=1)

#     def _build_weekly_section(self, parent, r):
#         """Build weekly treatments section."""
#         weekly = r.get("routine", {}).get("weekly_treatments", [])
#         if not weekly:
#             return

#         self._section_title(parent, "Weekly Treatments")

#         card = tk.Frame(parent, bg=COLORS["white"])
#         card.pack(fill=tk.X, padx=20, pady=(0, 10))

#         inner = tk.Frame(card, bg=COLORS["white"])
#         inner.pack(fill=tk.X, padx=25, pady=20)

#         for treatment in weekly:
#             t_frame = tk.Frame(inner, bg=COLORS["bg_secondary"])
#             t_frame.pack(fill=tk.X, pady=4)

#             t_inner = tk.Frame(t_frame, bg=COLORS["bg_secondary"])
#             t_inner.pack(fill=tk.X, padx=14, pady=10)

#             top_row = tk.Frame(t_inner, bg=COLORS["bg_secondary"])
#             top_row.pack(fill=tk.X)

#             tk.Label(
#                 top_row,
#                 text=treatment.get("treatment", ""),
#                 font=("Segoe UI", 11, "bold"),
#                 fg=COLORS["text_primary"], bg=COLORS["bg_secondary"]
#             ).pack(side=tk.LEFT)

#             tk.Label(
#                 top_row,
#                 text=treatment.get("frequency", ""),
#                 font=("Segoe UI", 9, "bold"),
#                 fg=COLORS["accent"], bg=COLORS["bg_secondary"]
#             ).pack(side=tk.RIGHT)

#             tk.Label(
#                 t_inner,
#                 text=f"Product: {treatment.get('ingredient', '')}",
#                 font=("Segoe UI", 10),
#                 fg=COLORS["text_secondary"], bg=COLORS["bg_secondary"],
#                 anchor=tk.W
#             ).pack(anchor=tk.W, pady=(3, 0))

#             tk.Label(
#                 t_inner,
#                 text=treatment.get("benefit", ""),
#                 font=("Segoe UI", 9),
#                 fg=COLORS["text_light"], bg=COLORS["bg_secondary"],
#                 anchor=tk.W
#             ).pack(anchor=tk.W, pady=(2, 0))

#     def _build_lifestyle_section(self, parent, r):
#         """Build lifestyle recommendations section."""
#         lifestyle = r.get("recommendations", {}).get("lifestyle_tips", [])
#         if not lifestyle:
#             return

#         self._section_title(parent, "Lifestyle Recommendations")

#         card = tk.Frame(parent, bg=COLORS["white"])
#         card.pack(fill=tk.X, padx=20, pady=(0, 10))

#         inner = tk.Frame(card, bg=COLORS["white"])
#         inner.pack(fill=tk.X, padx=25, pady=20)

#         for tip in lifestyle:
#             clean_tip = self._clean_text(tip)
#             tk.Label(
#                 inner,
#                 text=f"  ->  {clean_tip}",
#                 font=("Segoe UI", 11),
#                 fg=COLORS["text_primary"], bg=COLORS["white"],
#                 anchor=tk.W, wraplength=700, justify=tk.LEFT
#             ).pack(anchor=tk.W, pady=4)

#     def _build_disclaimer(self, parent):
#         """Build disclaimer footer."""
#         disc_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
#         disc_frame.pack(fill=tk.X, padx=20, pady=(20, 5))

#         tk.Label(
#             disc_frame,
#             text="DISCLAIMER: This analysis is for informational and educational "
#                  "purposes only. It is not a substitute for professional medical "
#                  "advice. Please consult a qualified dermatologist for proper "
#                  "skin assessment and treatment.",
#             font=("Segoe UI", 9),
#             fg=COLORS["text_light"], bg=COLORS["bg_secondary"],
#             wraplength=800, justify=tk.CENTER
#         ).pack(pady=12)

#     # ════════════════════════════════════════════════════════════
#     #  HELPER METHODS
#     # ════════════════════════════════════════════════════════════

#     def _section_title(self, parent, text):
#         """Create a section title."""
#         tk.Label(
#             parent, text=text,
#             font=("Segoe UI", 15, "bold"),
#             fg=COLORS["text_primary"], bg=COLORS["bg_secondary"],
#             anchor=tk.W
#         ).pack(fill=tk.X, padx=25, pady=(20, 8))

#     def _get_score_color(self, score):
#         """Get color based on score value."""
#         if score >= 80:
#             return COLORS["score_excellent"]
#         elif score >= 70:
#             return COLORS["score_good"]
#         elif score >= 50:
#             return COLORS["score_average"]
#         else:
#             return COLORS["score_poor"]

#     def _get_severity_color(self, severity_text):
#         """Get color based on severity text."""
#         severity_lower = severity_text.lower()

#         # Good statuses (green)
#         if severity_lower in [
#             "clear", "minimal", "none", "fine",
#             "excellent", "even", "good"
#         ]:
#             return COLORS["score_excellent"]

#         # Okay statuses (green-ish)
#         if severity_lower in ["mild", "normal"]:
#             return COLORS["score_good"]

#         # Warning statuses (yellow/orange)
#         if severity_lower in [
#             "moderate", "average", "visible",
#             "below average", "uneven"
#         ]:
#             return COLORS["score_average"]

#         # Bad statuses (red)
#         if severity_lower in [
#             "severe", "significant", "poor",
#             "enlarged", "heavy"
#         ]:
#             return COLORS["score_poor"]

#         # Default
#         return COLORS["text_light"]

#     def _clean_text(self, text):
#         """Remove emoji characters for safe display."""
#         clean = ""
#         for char in text:
#             try:
#                 char.encode("cp1252")
#                 clean += char
#             except (UnicodeEncodeError, UnicodeDecodeError):
#                 # Replace emoji with text equivalent
#                 replacements = {
#                     "\U0001f4a7": "[~]",    # water
#                     "\U0001f4a4": "[z]",    # sleep
#                     "\U0001f3c3": "[>]",    # running
#                     "\U00002600": "[sun]",  # sun
#                     "\U00002728": "[*]",    # sparkles
#                     "\U0001f6ad": "[no]",   # no smoking
#                     "\U0001f9d8": "[om]",   # meditation
#                     "\U0001f9ea": "[lab]",  # test tube
#                     "\U0001f95b": "[milk]", # glass
#                     "\U0001f957": "[food]", # salad
#                 }
#                 clean += replacements.get(char, "")
#         return clean.strip()

#     # ════════════════════════════════════════════════════════════
#     #  IMAGE / CAMERA ACTIONS
#     # ════════════════════════════════════════════════════════════

#     def _load_image(self):
#         """Load image from file dialog."""
#         filetypes = [
#             ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
#             ("All files", "*.*"),
#         ]
#         filepath = filedialog.askopenfilename(filetypes=filetypes)
#         if not filepath:
#             return

#         image = cv2.imread(filepath)
#         if image is None:
#             messagebox.showerror("Error", "Failed to load image file.")
#             return

#         self.image = resize_image(image, 800, 800)
#         self.results = None
#         self.visualizations = None

#         self.btn_analyze.config(state=tk.NORMAL)
#         self.btn_save.config(state=tk.DISABLED)

#         self._show_preview_screen()

#     def _capture_from_camera(self):
#         """Capture image from webcam."""
#         cap = cv2.VideoCapture(0)
#         if not cap.isOpened():
#             messagebox.showerror("Error", "Cannot access camera.")
#             return

#         messagebox.showinfo(
#             "Camera",
#             "Camera will open.\n\n"
#             "SPACE = Capture photo\n"
#             "ESC = Cancel"
#         )

#         captured = None
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             display = cv2.flip(frame, 1)
#             h, w = display.shape[:2]
#             cx, cy = w // 2, h // 2

#             # Guide oval
#             cv2.ellipse(display, (cx, cy), (150, 200), 0, 0, 360, (0, 255, 0), 2)

#             # Instructions
#             cv2.putText(
#                 display, "Position face in oval",
#                 (cx - 110, cy - 220),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
#             )
#             cv2.putText(
#                 display, "SPACE: Capture  |  ESC: Cancel",
#                 (10, h - 15),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
#             )

#             cv2.imshow("Camera - Skin Analysis", display)

#             key = cv2.waitKey(1) & 0xFF
#             if key == 27:  # ESC
#                 break
#             elif key == 32:  # SPACE
#                 captured = cv2.flip(frame, 1)
#                 break

#         cap.release()
#         cv2.destroyAllWindows()

#         if captured is not None:
#             self.image = resize_image(captured, 800, 800)
#             self.results = None
#             self.visualizations = None

#             self.btn_analyze.config(state=tk.NORMAL)
#             self.btn_save.config(state=tk.DISABLED)

#             self._show_preview_screen()

#     # ════════════════════════════════════════════════════════════
#     #  ANALYSIS EXECUTION
#     # ════════════════════════════════════════════════════════════

#     def _start_analysis(self):
#         """Start skin analysis in background thread."""
#         if self.image is None:
#             messagebox.showwarning("Warning", "Please upload a photo first.")
#             return

#         if self.is_analyzing:
#             return

#         self.is_analyzing = True
#         self.btn_analyze.config(state=tk.DISABLED)

#         self._show_loading_screen()

#         thread = threading.Thread(target=self._run_analysis, daemon=True)
#         thread.start()

#     def _run_analysis(self):
#         """Run analysis in background thread."""
#         try:
#             self.results = self.analyzer.analyze(self.image, detailed=True)
#             self.visualizations = self.analyzer.create_visualization(
#                 self.image, self.results
#             )
#             self.root.after(0, self._on_analysis_complete)
#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             self.root.after(0, lambda: self._on_analysis_error(str(e)))

#     def _on_analysis_complete(self):
#         """Called when analysis finishes successfully."""
#         self.is_analyzing = False

#         if hasattr(self, "progress"):
#             self.progress.stop()

#         self.btn_analyze.config(state=tk.NORMAL)
#         self.btn_save.config(state=tk.NORMAL)

#         if self.results.get("status") == "error":
#             messagebox.showerror(
#                 "Analysis Error",
#                 self.results.get("error", "Unknown error occurred.")
#             )
#             self._show_upload_screen()
#             return

#         self._show_results_screen()

#     def _on_analysis_error(self, error_msg):
#         """Called when analysis encounters an error."""
#         self.is_analyzing = False

#         if hasattr(self, "progress"):
#             self.progress.stop()

#         self.btn_analyze.config(state=tk.NORMAL)

#         messagebox.showerror(
#             "Error",
#             f"Analysis failed:\n\n{error_msg}"
#         )
#         self._show_upload_screen()

#     # ════════════════════════════════════════════════════════════
#     #  SAVE RESULTS
#     # ════════════════════════════════════════════════════════════

#     def _save_results(self):
#         """Save analysis results to disk."""
#         if not self.results:
#             messagebox.showwarning("Warning", "No results to save.")
#             return

#         save_dir = filedialog.askdirectory(title="Select Folder to Save Results")
#         if not save_dir:
#             return

#         try:
#             # Save text report (UTF-8)
#             report_text = self.report_gen.generate_text_report(self.results)
#             report_path = os.path.join(save_dir, "skin_analysis_report.txt")
#             with open(report_path, "w", encoding="utf-8") as f:
#                 f.write(report_text)

#             # Save visualization images
#             if self.visualizations:
#                 for name, img in self.visualizations.items():
#                     img_path = os.path.join(save_dir, f"skin_{name}.png")
#                     cv2.imwrite(img_path, img)

#             # Save original image
#             if self.image is not None:
#                 cv2.imwrite(
#                     os.path.join(save_dir, "original_photo.png"),
#                     self.image
#                 )

#             messagebox.showinfo(
#                 "Saved Successfully",
#                 f"All results saved to:\n{save_dir}"
#             )

#         except Exception as e:
#             messagebox.showerror(
#                 "Save Error",
#                 f"Failed to save:\n{str(e)}"
#             )

#     # ════════════════════════════════════════════════════════════
#     #  RUN APPLICATION
#     # ════════════════════════════════════════════════════════════

#     def run(self):
#         """Start the application main loop."""
#         self.root.mainloop()


# # ════════════════════════════════════════════════════════════
# #  ENTRY POINT
# # ════════════════════════════════════════════════════════════

# def main():
#     """Launch the Skin Analysis GUI application."""
#     app = SkinAnalysisApp()
#     app.run()


# if __name__ == "__main__":
#     main()


"""
Skin Insights — AI-Powered Skin Analysis Tool
Modern Interactive GUI with Card Grid Layouts
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os
from typing import Optional, Dict

from skin_analyzer import SkinAnalyzer
from report_generator import ReportGenerator
from utils import resize_image
import config

# ──────────────── Color Palette ────────────────
C = {
    "bg": "#F0F2F5",
    "card": "#FFFFFF",
    "card_hover": "#FAFBFC",
    "accent": "#E85D3A",
    "accent_dark": "#C94D2E",
    "accent_light": "#FFF0EC",
    "text": "#1A1A2E",
    "text2": "#4A4A5A",
    "text3": "#8A8A9A",
    "border": "#E4E7EB",
    "border_light": "#F0F0F5",
    "green": "#10B981",
    "green_bg": "#ECFDF5",
    "green_dark": "#059669",
    "yellow": "#F59E0B",
    "yellow_bg": "#FFFBEB",
    "red": "#EF4444",
    "red_bg": "#FEF2F2",
    "blue": "#3B82F6",
    "blue_bg": "#EFF6FF",
    "purple": "#8B5CF6",
    "purple_bg": "#F5F3FF",
    "orange": "#F97316",
    "orange_bg": "#FFF7ED",
    "indigo": "#4F46E5",
    "indigo_bg": "#EEF2FF",
    "bar_bg": "#E5E7EB",
    "white": "#FFFFFF",
    "am_accent": "#F97316",
    "am_bg": "#FFF7ED",
    "am_light": "#FFEDD5",
    "pm_accent": "#4F46E5",
    "pm_bg": "#EEF2FF",
    "pm_light": "#E0E7FF",
}


class SkinAnalysisApp:
    """Modern Interactive Skin Analysis GUI."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Skin Insights - AI Skin Analysis")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg=C["bg"])
        self.root.minsize(1000, 700)
        self.root.resizable(True, True)

        self.image: Optional[np.ndarray] = None
        self.results: Optional[Dict] = None
        self.visualizations: Optional[Dict] = None
        self.is_analyzing = False

        self.analyzer = SkinAnalyzer(use_mediapipe=config.USE_MEDIAPIPE)
        self.report_gen = ReportGenerator()

        self._build_navigation()
        self._build_main_area()
        self._show_upload_screen()

        self.root.bind("<Control-o>", lambda e: self._load_image())
        self.root.bind("<Control-s>", lambda e: self._save_results())

    # ═══════════════════════════════════════════════
    #  NAVIGATION BAR
    # ═══════════════════════════════════════════════

    def _build_navigation(self):
        nav = tk.Frame(self.root, bg=C["white"], height=56)
        nav.pack(fill=tk.X, side=tk.TOP)
        nav.pack_propagate(False)

        # Shadow line under nav
        tk.Frame(self.root, bg=C["border"], height=1).pack(fill=tk.X)

        left = tk.Frame(nav, bg=C["white"])
        left.pack(side=tk.LEFT, padx=24)

        tk.Label(left, text="Skin Insights",
                 font=("Segoe UI", 16, "bold"),
                 fg=C["accent"], bg=C["white"]).pack(side=tk.LEFT)

        tk.Label(left, text="AI Analysis",
                 font=("Segoe UI", 9),
                 fg=C["text3"], bg=C["white"]).pack(side=tk.LEFT, padx=(8, 0), pady=(4, 0))

        right = tk.Frame(nav, bg=C["white"])
        right.pack(side=tk.RIGHT, padx=24)

        self.btn_save = self._pill_button(right, "Save Report",
                                          self._save_results, C["green_dark"],
                                          state=tk.DISABLED)
        self.btn_save.pack(side=tk.RIGHT, padx=4)

        self.btn_analyze = self._pill_button(right, "Analyze",
                                             self._start_analysis, C["accent"],
                                             state=tk.DISABLED)
        self.btn_analyze.pack(side=tk.RIGHT, padx=4)

        self.btn_camera = self._pill_button(right, "Camera",
                                            self._capture_from_camera, C["blue"])
        self.btn_camera.pack(side=tk.RIGHT, padx=4)

        self.btn_upload = self._pill_button(right, "Upload",
                                            self._load_image, C["text"])
        self.btn_upload.pack(side=tk.RIGHT, padx=4)

    def _pill_button(self, parent, text, cmd, bg, state=tk.NORMAL):
        btn = tk.Button(parent, text=text, command=cmd,
                        font=("Segoe UI", 9, "bold"),
                        fg="white", bg=bg,
                        activebackground=bg, activeforeground="white",
                        bd=0, padx=18, pady=5, cursor="hand2",
                        state=state, relief=tk.FLAT)
        # Hover effect
        def on_enter(e): btn.config(bg=self._darken(bg))
        def on_leave(e): btn.config(bg=bg)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _darken(self, hex_color, factor=0.85):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ═══════════════════════════════════════════════
    #  MAIN AREA
    # ═══════════════════════════════════════════════

    def _build_main_area(self):
        self.main_frame = tk.Frame(self.root, bg=C["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def _clear_main(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    # ═══════════════════════════════════════════════
    #  UPLOAD SCREEN
    # ═══════════════════════════════════════════════

    def _show_upload_screen(self):
        self._clear_main()
        center = tk.Frame(self.main_frame, bg=C["bg"])
        center.place(relx=0.5, rely=0.42, anchor=tk.CENTER)

        # Big upload area card
        upload_card = tk.Frame(center, bg=C["white"], padx=60, pady=50)
        upload_card.pack()

        tk.Label(upload_card, text="SKIN INSIGHTS",
                 font=("Segoe UI", 26, "bold"),
                 fg=C["accent"], bg=C["white"]).pack(pady=(0, 4))

        tk.Label(upload_card,
                 text="Get your personalized skin analysis in seconds",
                 font=("Segoe UI", 12),
                 fg=C["text2"], bg=C["white"]).pack(pady=(0, 4))

        tk.Label(upload_card,
                 text="Front-facing photo  |  Good lighting  |  No makeup  |  No filters",
                 font=("Segoe UI", 9),
                 fg=C["text3"], bg=C["white"]).pack(pady=(0, 30))

        btn_row = tk.Frame(upload_card, bg=C["white"])
        btn_row.pack()

        tk.Button(btn_row, text="Upload Photo", command=self._load_image,
                  font=("Segoe UI", 13, "bold"), fg="white", bg=C["accent"],
                  activebackground=C["accent_dark"], bd=0,
                  padx=36, pady=13, cursor="hand2",
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=8)

        tk.Button(btn_row, text="Use Camera", command=self._capture_from_camera,
                  font=("Segoe UI", 13, "bold"), fg=C["text"],
                  bg=C["white"], activebackground=C["bg"],
                  highlightthickness=2, highlightbackground=C["border"],
                  bd=0, padx=36, pady=12, cursor="hand2",
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=8)

        # Feature chips
        chips = tk.Frame(upload_card, bg=C["white"])
        chips.pack(pady=(28, 0))

        chip_data = [
            ("Acne Detection", C["red_bg"], C["red"]),
            ("Skin Type", C["blue_bg"], C["blue"]),
            ("Personalized Routine", C["green_bg"], C["green"]),
            ("Ingredients", C["purple_bg"], C["purple"]),
            ("Skin Age", C["orange_bg"], C["orange"]),
        ]
        for text, bg, fg in chip_data:
            chip = tk.Label(chips, text=f"  {text}  ",
                           font=("Segoe UI", 9, "bold"),
                           fg=fg, bg=bg)
            chip.pack(side=tk.LEFT, padx=4, pady=2)

    # ═══════════════════════════════════════════════
    #  PREVIEW SCREEN
    # ═══════════════════════════════════════════════

    def _show_preview_screen(self):
        self._clear_main()
        center = tk.Frame(self.main_frame, bg=C["bg"])
        center.place(relx=0.5, rely=0.43, anchor=tk.CENTER)

        card = tk.Frame(center, bg=C["white"], padx=40, pady=35)
        card.pack()

        if self.image is not None:
            display = resize_image(self.image, 320, 320)
            rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            tk_img = ImageTk.PhotoImage(pil_img)
            lbl = tk.Label(card, image=tk_img, bg=C["white"], bd=2, relief=tk.GROOVE)
            lbl.image = tk_img
            lbl.pack(pady=(0, 18))

        tk.Label(card, text="Ready to analyze!",
                 font=("Segoe UI", 16, "bold"),
                 fg=C["text"], bg=C["white"]).pack(pady=(0, 5))

        tk.Label(card, text="Click below to start your skin analysis",
                 font=("Segoe UI", 10), fg=C["text3"],
                 bg=C["white"]).pack(pady=(0, 18))

        btn_row = tk.Frame(card, bg=C["white"])
        btn_row.pack()

        tk.Button(btn_row, text="Analyze My Skin",
                  command=self._start_analysis,
                  font=("Segoe UI", 13, "bold"), fg="white", bg=C["accent"],
                  bd=0, padx=40, pady=13, cursor="hand2",
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=6)

        tk.Button(btn_row, text="Change Photo",
                  command=self._load_image,
                  font=("Segoe UI", 10), fg=C["text2"], bg=C["bg"],
                  bd=0, padx=20, pady=11, cursor="hand2",
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=6)

    # ═══════════════════════════════════════════════
    #  LOADING SCREEN
    # ═══════════════════════════════════════════════

    def _show_loading_screen(self):
        self._clear_main()
        center = tk.Frame(self.main_frame, bg=C["bg"])
        center.place(relx=0.5, rely=0.42, anchor=tk.CENTER)

        card = tk.Frame(center, bg=C["white"], padx=60, pady=45)
        card.pack()

        tk.Label(card, text="Analyzing Your Skin...",
                 font=("Segoe UI", 20, "bold"),
                 fg=C["text"], bg=C["white"]).pack(pady=(0, 8))

        tk.Label(card, text="Detecting concerns and building your routine",
                 font=("Segoe UI", 10), fg=C["text3"],
                 bg=C["white"]).pack(pady=(0, 22))

        self.progress = ttk.Progressbar(card, mode="indeterminate", length=320)
        self.progress.pack(pady=(0, 12))
        self.progress.start(12)

        tk.Label(card, text="Usually takes 10-20 seconds",
                 font=("Segoe UI", 9), fg=C["text3"],
                 bg=C["white"]).pack()

    # ═══════════════════════════════════════════════
    #  RESULTS SCREEN
    # ═══════════════════════════════════════════════

    def _show_results_screen(self):
        self._clear_main()
        r = self.results
        if not r:
            return

        # Scrollable setup
        canvas = tk.Canvas(self.main_frame, bg=C["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=C["bg"])

        self.scroll_frame.bind("<Configure>",
                               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        cw = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw",
                                  width=config.WINDOW_WIDTH - 30)

        def on_resize(e):
            canvas.itemconfig(cw, width=e.width)
        canvas.bind("<Configure>", on_resize)
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_scroll(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_scroll)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        p = self.scroll_frame  # parent shorthand

        # ── SECTION 1: Hero ──
        self._hero(p, r)

        # ── SECTION 2: Score Breakdown ──
        self._scores(p, r)

        # ── SECTION 3: Concerns Grid ──
        self._concerns_grid(p, r)

        # ── SECTION 4: Personalized Tips Grid ──
        self._tips_grid(p, r)

        # ── SECTION 5: Ingredients Grid ──
        self._ingredients_grid(p, r)

        # ── SECTION 6: AM/PM Routine Side by Side ──
        self._routine_table(p, r)

        # ── SECTION 7: Weekly Treatments ──
        self._weekly_grid(p, r)

        # ── SECTION 8: Lifestyle ──
        self._lifestyle(p, r)

        # ── SECTION 9: Disclaimer ──
        self._disclaimer(p)

        tk.Frame(p, height=60, bg=C["bg"]).pack()

    # ═══════════════════════════════════════════════
    #  HERO SECTION
    # ═══════════════════════════════════════════════

    def _hero(self, parent, r):
        card = tk.Frame(parent, bg=C["white"])
        card.pack(fill=tk.X, padx=24, pady=(20, 12))

        inner = tk.Frame(card, bg=C["white"])
        inner.pack(fill=tk.X, padx=28, pady=24)

        # Photo
        left = tk.Frame(inner, bg=C["white"])
        left.pack(side=tk.LEFT, padx=(0, 28))

        if self.image is not None:
            disp = resize_image(self.image, 220, 220)
            rgb = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb)
            tki = ImageTk.PhotoImage(pil)
            lbl = tk.Label(left, image=tki, bg=C["white"], bd=2, relief=tk.GROOVE)
            lbl.image = tki
            lbl.pack()

        # Score + Info
        right = tk.Frame(inner, bg=C["white"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Your Skin Health Score",
                 font=("Segoe UI", 10), fg=C["text3"],
                 bg=C["white"]).pack(anchor=tk.W)

        score = r.get("overall_score", 0)
        sc = self._score_color(score)

        row = tk.Frame(right, bg=C["white"])
        row.pack(anchor=tk.W, pady=(2, 0))
        tk.Label(row, text=f"{score:.0f}", font=("Segoe UI", 46, "bold"),
                 fg=sc, bg=C["white"]).pack(side=tk.LEFT)
        tk.Label(row, text="/100", font=("Segoe UI", 15),
                 fg=C["text3"], bg=C["white"]).pack(side=tk.LEFT, pady=(16, 0))

        tk.Label(right, text=r.get("overall_grade", ""),
                 font=("Segoe UI", 12, "bold"), fg=sc,
                 bg=C["white"]).pack(anchor=tk.W, pady=(0, 10))

        # Stat chips row
        chips = tk.Frame(right, bg=C["white"])
        chips.pack(anchor=tk.W, pady=(4, 0))

        stat_data = [
            ("Skin Type", r.get("skin_type", {}).get("type", "N/A"),
             C["blue_bg"], C["blue"]),
            ("Tone", r.get("skin_tone", {}).get("category", "N/A"),
             C["orange_bg"], C["orange"]),
            ("Undertone", r.get("skin_tone", {}).get("undertone", {}).get("type", "N/A").capitalize(),
             C["purple_bg"], C["purple"]),
            ("Skin Age", r.get("skin_age", {}).get("age_range", "N/A"),
             C["green_bg"], C["green_dark"]),
        ]

        for label, value, bg, fg in stat_data:
            chip = tk.Frame(chips, bg=bg, padx=12, pady=6)
            chip.pack(side=tk.LEFT, padx=(0, 6))
            tk.Label(chip, text=label, font=("Segoe UI", 7, "bold"),
                     fg=fg, bg=bg).pack()
            tk.Label(chip, text=value, font=("Segoe UI", 11, "bold"),
                     fg=C["text"], bg=bg).pack()

        age_status = r.get("skin_age", {}).get("status", "")
        if age_status:
            tk.Label(right, text=age_status, font=("Segoe UI", 9, "italic"),
                     fg=C["text3"], bg=C["white"]).pack(anchor=tk.W, pady=(10, 0))

    # ═══════════════════════════════════════════════
    #  SCORE BREAKDOWN
    # ═══════════════════════════════════════════════

    def _scores(self, parent, r):
        self._title(parent, "Score Breakdown")

        card = tk.Frame(parent, bg=C["white"])
        card.pack(fill=tk.X, padx=24, pady=(0, 12))
        inner = tk.Frame(card, bg=C["white"])
        inner.pack(fill=tk.X, padx=24, pady=18)

        # Headers
        hdr = tk.Frame(inner, bg=C["white"], height=22)
        hdr.pack(fill=tk.X, pady=(0, 4))
        hdr.pack_propagate(False)

        for text, w, side in [("CATEGORY", 160, tk.LEFT), ("STATUS", 90, tk.RIGHT),
                               ("SCORE", 45, tk.RIGHT)]:
            f = tk.Frame(hdr, bg=C["white"], width=w, height=22)
            f.pack(side=side)
            f.pack_propagate(False)
            anchor = tk.W if side == tk.LEFT else tk.CENTER
            tk.Label(f, text=text, font=("Segoe UI", 7, "bold"),
                     fg=C["text3"], bg=C["white"]).place(
                x=0 if side == tk.LEFT else None,
                relx=None if side == tk.LEFT else 0.5,
                rely=0.5, anchor=anchor if side == tk.LEFT else tk.CENTER)

        tk.Frame(inner, bg=C["border"], height=1).pack(fill=tk.X, pady=(0, 6))

        items = [
            ("Acne & Blemishes", r.get("blemishes", {}).get("score", 75),
             r.get("blemishes", {}).get("severity", "N/A")),
            ("Pigmentation", r.get("pigmentation", {}).get("score", 75),
             r.get("pigmentation", {}).get("severity", "N/A")),
            ("Wrinkles", r.get("wrinkles", {}).get("overall_score", 75),
             r.get("wrinkles", {}).get("severity", "N/A")),
            ("Texture", r.get("texture", {}).get("score", 75),
             r.get("texture", {}).get("grade", "N/A")),
            ("Pores", r.get("pores", {}).get("score", 75),
             r.get("pores", {}).get("severity", "N/A")),
            ("Dark Circles", r.get("dark_circles", {}).get("score", 75),
             r.get("dark_circles", {}).get("severity", "N/A")),
            ("Evenness", r.get("skin_tone", {}).get("evenness_score", 75),
             "Even" if r.get("skin_tone", {}).get("evenness_score", 75) >= 70 else "Uneven"),
        ]

        for name, sc, sev in items:
            self._score_bar(inner, name, sc, sev)

    def _score_bar(self, parent, name, score, severity):
        row = tk.Frame(parent, bg=C["white"], height=38)
        row.pack(fill=tk.X, pady=3)
        row.pack_propagate(False)

        color = self._score_color(score)

        # Label
        lf = tk.Frame(row, bg=C["white"], width=160, height=38)
        lf.pack(side=tk.LEFT)
        lf.pack_propagate(False)
        tk.Label(lf, text=name, font=("Segoe UI", 10),
                 fg=C["text"], bg=C["white"]).place(x=0, rely=0.5, anchor=tk.W)

        # Status badge (RIGHT side)
        sf = tk.Frame(row, bg=C["white"], width=90, height=38)
        sf.pack(side=tk.RIGHT)
        sf.pack_propagate(False)

        sev_text = str(severity).capitalize()
        sev_bg = self._severity_bg(sev_text)
        sev_fg = self._severity_color(sev_text)

        badge = tk.Label(sf, text=f" {sev_text} ", font=("Segoe UI", 8, "bold"),
                        fg=sev_fg, bg=sev_bg)
        badge.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Score number (RIGHT of bar)
        nf = tk.Frame(row, bg=C["white"], width=45, height=38)
        nf.pack(side=tk.RIGHT)
        nf.pack_propagate(False)
        tk.Label(nf, text=f"{score:.0f}", font=("Segoe UI", 11, "bold"),
                 fg=color, bg=C["white"]).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Bar
        bf = tk.Frame(row, bg=C["white"], height=38)
        bf.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 8))

        bar = tk.Canvas(bf, bg=C["bar_bg"], height=12, highlightthickness=0, bd=0)
        bar.pack(fill=tk.X, pady=13)

        def draw(e=None):
            bar.delete("all")
            w = max(bar.winfo_width(), 100)
            fw = max(3, int((score / 100) * w))
            bar.create_rectangle(0, 0, w, 12, fill=C["bar_bg"], outline="")
            bar.create_rectangle(0, 0, fw, 12, fill=color, outline="")
        bar.bind("<Configure>", draw)

    # ═══════════════════════════════════════════════
    #  CONCERNS — 2-COLUMN GRID CARDS
    # ═══════════════════════════════════════════════

    def _concerns_grid(self, parent, r):
        concerns = r.get("recommendations", {}).get("concerns", [])
        if not concerns:
            return
        if len(concerns) == 1 and "Great" in concerns[0].get("name", ""):
            self._title(parent, "Skin Assessment")
            card = tk.Frame(parent, bg=C["white"])
            card.pack(fill=tk.X, padx=24, pady=(0, 12))
            tk.Label(card, text="Your skin looks great! No major concerns.",
                     font=("Segoe UI", 13, "bold"), fg=C["green"],
                     bg=C["white"], pady=28).pack()
            return

        self._title(parent, "Your Skin Concerns")

        grid = tk.Frame(parent, bg=C["bg"])
        grid.pack(fill=tk.X, padx=24, pady=(0, 12))

        # Configure 2 equal columns
        grid.columnconfigure(0, weight=1, uniform="concern")
        grid.columnconfigure(1, weight=1, uniform="concern")

        icon_colors = {
            "Acne": (C["red"], C["red_bg"]),
            "Pigmentation": (C["orange"], C["orange_bg"]),
            "Fine Lines": (C["purple"], C["purple_bg"]),
            "Enlarged": (C["blue"], C["blue_bg"]),
            "Dark Circles": (C["indigo"], C["indigo_bg"]),
            "Uneven": (C["yellow"], C["yellow_bg"]),
            "Oiliness": (C["blue"], C["blue_bg"]),
            "Dryness": (C["orange"], C["orange_bg"]),
        }

        icon_symbols = {
            "Acne": "!!", "Pigmentation": "..", "Fine Lines": "~~",
            "Enlarged": "oo", "Dark Circles": "()", "Uneven": "##",
            "Oiliness": "~~", "Dryness": "__",
        }

        for i, concern in enumerate(concerns[:6]):
            row_idx = i // 2
            col_idx = i % 2

            # Get colors for this concern type
            fg_c, bg_c = C["accent"], C["accent_light"]
            icon_sym = ">>"
            for key in icon_colors:
                if key in concern.get("name", ""):
                    fg_c, bg_c = icon_colors[key]
                    icon_sym = icon_symbols.get(key, ">>")
                    break

            # Card
            card = tk.Frame(grid, bg=C["white"], padx=0, pady=0)
            card.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="nsew")

            card_inner = tk.Frame(card, bg=C["white"])
            card_inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

            # Top: Icon circle + Name + Badge
            top = tk.Frame(card_inner, bg=C["white"])
            top.pack(fill=tk.X)

            # Icon
            icon_lbl = tk.Label(top, text=f" {icon_sym} ",
                               font=("Consolas", 10, "bold"),
                               fg=fg_c, bg=bg_c)
            icon_lbl.pack(side=tk.LEFT, padx=(0, 10))

            # Name
            tk.Label(top, text=concern["name"],
                     font=("Segoe UI", 11, "bold"),
                     fg=C["text"], bg=C["white"]).pack(side=tk.LEFT)

            # Severity badge
            sev = concern.get("severity", "mild")
            sev_fg = self._severity_color(sev)
            sev_bg = self._severity_bg(sev)
            tk.Label(top, text=f" {sev.upper()} ",
                     font=("Segoe UI", 7, "bold"),
                     fg=sev_fg, bg=sev_bg).pack(side=tk.RIGHT)

            # Details
            details = concern.get("details", "")
            if details:
                tk.Label(card_inner, text=details,
                         font=("Segoe UI", 9), fg=C["text2"],
                         bg=C["white"], wraplength=350,
                         justify=tk.LEFT, anchor=tk.W).pack(
                    anchor=tk.W, pady=(8, 0))

            # Left accent bar
            accent_bar = tk.Frame(card, bg=fg_c, width=4)
            accent_bar.place(x=0, y=0, relheight=1)

    # ═══════════════════════════════════════════════
    #  TIPS — HORIZONTAL SCROLLABLE CARDS
    # ═══════════════════════════════════════════════

    def _tips_grid(self, parent, r):
        tips = r.get("recommendations", {}).get("specific_tips", [])
        if not tips:
            return

        self._title(parent, "Personalized Care Plan")

        grid = tk.Frame(parent, bg=C["bg"])
        grid.pack(fill=tk.X, padx=24, pady=(0, 12))
        grid.columnconfigure(0, weight=1, uniform="tip")
        grid.columnconfigure(1, weight=1, uniform="tip")

        urg_styles = {
            "high": {"fg": C["red"], "bg": C["red_bg"], "icon": "!!",
                     "label": "HIGH PRIORITY"},
            "medium": {"fg": C["yellow"], "bg": C["yellow_bg"], "icon": "!",
                       "label": "MEDIUM"},
            "low": {"fg": C["green"], "bg": C["green_bg"], "icon": "i",
                    "label": "GOOD TO KNOW"},
        }

        for i, tip in enumerate(tips[:6]):
            urgency = tip.get("urgency", "low")
            style = urg_styles.get(urgency, urg_styles["low"])

            row_idx = i // 2
            col_idx = i % 2

            card = tk.Frame(grid, bg=C["white"])
            card.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="nsew")

            inner = tk.Frame(card, bg=C["white"])
            inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

            # Top bar with urgency
            top = tk.Frame(inner, bg=C["white"])
            top.pack(fill=tk.X, pady=(0, 6))

            tk.Label(top, text=f" {style['icon']} ",
                     font=("Consolas", 9, "bold"),
                     fg=style["fg"], bg=style["bg"]).pack(side=tk.LEFT, padx=(0, 8))

            tk.Label(top, text=style["label"],
                     font=("Segoe UI", 7, "bold"),
                     fg=style["fg"], bg=C["white"]).pack(side=tk.LEFT)

            # Title
            tk.Label(inner, text=tip["title"],
                     font=("Segoe UI", 11, "bold"),
                     fg=C["text"], bg=C["white"],
                     anchor=tk.W).pack(anchor=tk.W, pady=(0, 4))

            # Tip text
            tk.Label(inner, text=tip["tip"],
                     font=("Segoe UI", 9), fg=C["text2"],
                     bg=C["white"], wraplength=360,
                     justify=tk.LEFT, anchor=tk.W).pack(anchor=tk.W)

            # Top accent
            tk.Frame(card, bg=style["fg"], height=3).place(x=0, y=0, relwidth=1)

    # ═══════════════════════════════════════════════
    #  INGREDIENTS — 3-COLUMN CARDS
    # ═══════════════════════════════════════════════

    def _ingredients_grid(self, parent, r):
        ingredients = r.get("recommendations", {}).get("recommended_ingredients", [])
        if not ingredients:
            return

        self._title(parent, "Recommended Active Ingredients")

        grid = tk.Frame(parent, bg=C["bg"])
        grid.pack(fill=tk.X, padx=24, pady=(0, 12))
        grid.columnconfigure(0, weight=1, uniform="ing")
        grid.columnconfigure(1, weight=1, uniform="ing")
        grid.columnconfigure(2, weight=1, uniform="ing")

        colors = [C["green"], C["blue"], C["purple"], C["orange"],
                  C["indigo"], C["red"], C["accent"], C["green_dark"]]

        for i, ing in enumerate(ingredients[:6]):
            col_color = colors[i % len(colors)]

            card = tk.Frame(grid, bg=C["white"])
            card.grid(row=i // 3, column=i % 3, padx=4, pady=4, sticky="nsew")

            inner = tk.Frame(card, bg=C["white"])
            inner.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

            # Number badge
            top = tk.Frame(inner, bg=C["white"])
            top.pack(fill=tk.X, pady=(0, 8))

            tk.Label(top, text=f" {i + 1} ",
                     font=("Segoe UI", 9, "bold"),
                     fg="white", bg=col_color).pack(side=tk.LEFT, padx=(0, 8))

            tk.Label(top, text=ing.get("concentration", ""),
                     font=("Segoe UI", 8, "bold"),
                     fg=col_color, bg=C["white"]).pack(side=tk.RIGHT)

            # Name
            tk.Label(inner, text=ing.get("name", ""),
                     font=("Segoe UI", 10, "bold"),
                     fg=C["text"], bg=C["white"],
                     anchor=tk.W, wraplength=220).pack(anchor=tk.W)

            # Benefits
            tk.Label(inner, text=ing.get("benefits", ""),
                     font=("Segoe UI", 9), fg=C["text2"],
                     bg=C["white"], wraplength=220,
                     justify=tk.LEFT, anchor=tk.W).pack(
                anchor=tk.W, pady=(4, 0))

            # Reason
            reason = ing.get("reason", "")
            if reason:
                tk.Label(inner, text=reason,
                         font=("Segoe UI", 8, "italic"),
                         fg=C["text3"], bg=C["white"],
                         wraplength=220, justify=tk.LEFT,
                         anchor=tk.W).pack(anchor=tk.W, pady=(4, 0))

            # Top color bar
            tk.Frame(card, bg=col_color, height=3).place(x=0, y=0, relwidth=1)

    # ═══════════════════════════════════════════════
    #  ROUTINE — SIDE BY SIDE TABLE
    # ═══════════════════════════════════════════════

    def _routine_table(self, parent, r):
        routine = r.get("routine", {})
        am = routine.get("morning_routine", [])
        pm = routine.get("night_routine", [])
        if not am and not pm:
            return

        self._title(parent, "Your Daily Skincare Routine")

        card = tk.Frame(parent, bg=C["white"])
        card.pack(fill=tk.X, padx=24, pady=(0, 12))

        inner = tk.Frame(card, bg=C["white"])
        inner.pack(fill=tk.X, padx=16, pady=16)

        # Two columns
        inner.columnconfigure(0, weight=1, uniform="routine")
        inner.columnconfigure(1, weight=0, minsize=2)
        inner.columnconfigure(2, weight=1, uniform="routine")

        # ── AM Header ──
        am_hdr = tk.Frame(inner, bg=C["am_light"])
        am_hdr.grid(row=0, column=0, sticky="ew", padx=(0, 1), pady=(0, 2))
        tk.Label(am_hdr, text="MORNING  (AM)",
                 font=("Segoe UI", 12, "bold"),
                 fg=C["am_accent"], bg=C["am_light"],
                 pady=10).pack()
        tk.Label(am_hdr, text="Apply in order every morning",
                 font=("Segoe UI", 8), fg=C["am_accent"],
                 bg=C["am_light"]).pack(pady=(0, 8))

        # ── Divider column ──
        tk.Frame(inner, bg=C["border"], width=2).grid(
            row=0, column=1, rowspan=max(len(am), len(pm)) + 1,
            sticky="ns", padx=2)

        # ── PM Header ──
        pm_hdr = tk.Frame(inner, bg=C["pm_light"])
        pm_hdr.grid(row=0, column=2, sticky="ew", padx=(1, 0), pady=(0, 2))
        tk.Label(pm_hdr, text="NIGHT  (PM)",
                 font=("Segoe UI", 12, "bold"),
                 fg=C["pm_accent"], bg=C["pm_light"],
                 pady=10).pack()
        tk.Label(pm_hdr, text="Apply in order every night",
                 font=("Segoe UI", 8), fg=C["pm_accent"],
                 bg=C["pm_light"]).pack(pady=(0, 8))

        # ── Steps side by side ──
        max_steps = max(len(am), len(pm))

        for i in range(max_steps):
            # AM cell
            am_cell = tk.Frame(inner, bg=C["white"],
                               highlightthickness=1,
                               highlightbackground=C["border_light"])
            am_cell.grid(row=i + 1, column=0, sticky="nsew",
                        padx=(0, 1), pady=2)

            if i < len(am):
                self._routine_cell(am_cell, am[i], "am")
            else:
                tk.Label(am_cell, text="", bg=C["white"], height=2).pack()

            # PM cell
            pm_cell = tk.Frame(inner, bg=C["white"],
                               highlightthickness=1,
                               highlightbackground=C["border_light"])
            pm_cell.grid(row=i + 1, column=2, sticky="nsew",
                        padx=(1, 0), pady=2)

            if i < len(pm):
                self._routine_cell(pm_cell, pm[i], "pm")
            else:
                tk.Label(pm_cell, text="", bg=C["white"], height=2).pack()

        # ── Notes row ──
        notes = routine.get("notes", [])
        if notes:
            notes_row = tk.Frame(inner, bg=C["bg"])
            notes_row.grid(row=max_steps + 1, column=0, columnspan=3,
                          sticky="ew", pady=(10, 0))
            notes_inner = tk.Frame(notes_row, bg=C["bg"])
            notes_inner.pack(fill=tk.X, padx=12, pady=10)

            tk.Label(notes_inner, text="IMPORTANT NOTES",
                     font=("Segoe UI", 8, "bold"),
                     fg=C["text3"], bg=C["bg"]).pack(anchor=tk.W, pady=(0, 4))

            notes_grid = tk.Frame(notes_inner, bg=C["bg"])
            notes_grid.pack(fill=tk.X)
            notes_grid.columnconfigure(0, weight=1)
            notes_grid.columnconfigure(1, weight=1)

            for idx, note in enumerate(notes):
                clean = self._clean(note)
                tk.Label(notes_grid, text=f"  ->  {clean}",
                         font=("Segoe UI", 8), fg=C["text2"],
                         bg=C["bg"], anchor=tk.W, wraplength=340,
                         justify=tk.LEFT).grid(
                    row=idx // 2, column=idx % 2,
                    sticky="w", padx=4, pady=2)

    def _routine_cell(self, parent, step, tod):
        """Build one routine step cell."""
        if tod == "am":
            accent, light = C["am_accent"], C["am_bg"]
        else:
            accent, light = C["pm_accent"], C["pm_bg"]

        inner = tk.Frame(parent, bg=C["white"])
        inner.pack(fill=tk.X, padx=10, pady=8)

        # Top: step badge + product
        top = tk.Frame(inner, bg=C["white"])
        top.pack(fill=tk.X)

        tk.Label(top, text=f" {step.get('step', '?')} ",
                 font=("Segoe UI", 8, "bold"),
                 fg="white", bg=accent).pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(top, text=step.get("product", ""),
                 font=("Segoe UI", 10, "bold"),
                 fg=C["text"], bg=C["white"]).pack(side=tk.LEFT)

        # Ingredient
        ing = step.get("ingredient", "")
        if ing:
            tk.Label(inner, text=ing,
                     font=("Segoe UI", 9, "bold"),
                     fg=accent, bg=C["white"],
                     anchor=tk.W).pack(anchor=tk.W, pady=(3, 0))

        # How to
        how = step.get("how_to", "")
        if how:
            tk.Label(inner, text=how,
                     font=("Segoe UI", 8), fg=C["text3"],
                     bg=C["white"], wraplength=300,
                     justify=tk.LEFT, anchor=tk.W).pack(
                anchor=tk.W, pady=(2, 0))

    # ═══════════════════════════════════════════════
    #  WEEKLY — HORIZONTAL CARDS
    # ═══════════════════════════════════════════════

    def _weekly_grid(self, parent, r):
        weekly = r.get("routine", {}).get("weekly_treatments", [])
        if not weekly:
            return

        self._title(parent, "Weekly Treatments")

        grid = tk.Frame(parent, bg=C["bg"])
        grid.pack(fill=tk.X, padx=24, pady=(0, 12))

        for i, w in enumerate(weekly):
            grid.columnconfigure(i, weight=1, uniform="weekly")

        colors = [C["purple"], C["blue"], C["green"], C["orange"]]

        for i, treatment in enumerate(weekly):
            col = colors[i % len(colors)]

            card = tk.Frame(grid, bg=C["white"])
            card.grid(row=0, column=i, padx=4, pady=4, sticky="nsew")

            inner = tk.Frame(card, bg=C["white"])
            inner.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

            tk.Label(inner, text=treatment.get("treatment", ""),
                     font=("Segoe UI", 11, "bold"),
                     fg=C["text"], bg=C["white"],
                     anchor=tk.W).pack(anchor=tk.W)

            tk.Label(inner, text=treatment.get("frequency", ""),
                     font=("Segoe UI", 9, "bold"),
                     fg=col, bg=C["white"],
                     anchor=tk.W).pack(anchor=tk.W, pady=(2, 0))

            tk.Label(inner, text=treatment.get("ingredient", ""),
                     font=("Segoe UI", 9), fg=C["text2"],
                     bg=C["white"], wraplength=180,
                     anchor=tk.W, justify=tk.LEFT).pack(
                anchor=tk.W, pady=(4, 0))

            tk.Label(inner, text=treatment.get("benefit", ""),
                     font=("Segoe UI", 8), fg=C["text3"],
                     bg=C["white"], wraplength=180,
                     anchor=tk.W, justify=tk.LEFT).pack(
                anchor=tk.W, pady=(3, 0))

            tk.Frame(card, bg=col, height=3).place(x=0, y=0, relwidth=1)

    # ═══════════════════════════════════════════════
    #  LIFESTYLE
    # ═══════════════════════════════════════════════

    def _lifestyle(self, parent, r):
        tips = r.get("recommendations", {}).get("lifestyle_tips", [])
        if not tips:
            return

        self._title(parent, "Lifestyle Tips")

        card = tk.Frame(parent, bg=C["white"])
        card.pack(fill=tk.X, padx=24, pady=(0, 12))

        inner = tk.Frame(card, bg=C["white"])
        inner.pack(fill=tk.X, padx=24, pady=16)

        inner.columnconfigure(0, weight=1, uniform="life")
        inner.columnconfigure(1, weight=1, uniform="life")

        colors_cycle = [C["green"], C["blue"], C["purple"],
                       C["orange"], C["indigo"]]

        for i, tip in enumerate(tips):
            clean = self._clean(tip)
            col = colors_cycle[i % len(colors_cycle)]

            cell = tk.Frame(inner, bg=C["bg"], padx=12, pady=8)
            cell.grid(row=i // 2, column=i % 2,
                     padx=3, pady=3, sticky="nsew")

            # Color dot + text
            row_f = tk.Frame(cell, bg=C["bg"])
            row_f.pack(fill=tk.X)

            tk.Label(row_f, text=" * ",
                     font=("Segoe UI", 10, "bold"),
                     fg=col, bg=C["bg"]).pack(side=tk.LEFT)

            tk.Label(row_f, text=clean,
                     font=("Segoe UI", 10), fg=C["text"],
                     bg=C["bg"], anchor=tk.W,
                     wraplength=320, justify=tk.LEFT).pack(
                side=tk.LEFT, fill=tk.X, expand=True)

    # ═══════════════════════════════════════════════
    #  DISCLAIMER
    # ═══════════════════════════════════════════════

    def _disclaimer(self, parent):
        f = tk.Frame(parent, bg=C["bg"])
        f.pack(fill=tk.X, padx=24, pady=(16, 4))
        tk.Label(f, text="DISCLAIMER: This analysis is for informational purposes only. "
                         "Not a substitute for professional medical advice. "
                         "Consult a dermatologist for proper assessment.",
                 font=("Segoe UI", 8), fg=C["text3"],
                 bg=C["bg"], wraplength=800, justify=tk.CENTER).pack(pady=8)

    # ═══════════════════════════════════════════════
    #  HELPERS
    # ═══════════════════════════════════════════════

    def _title(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 14, "bold"),
                 fg=C["text"], bg=C["bg"],
                 anchor=tk.W).pack(fill=tk.X, padx=28, pady=(18, 6))

    def _score_color(self, s):
        if s >= 80: return C["green"]
        if s >= 70: return C["green_dark"]
        if s >= 50: return C["yellow"]
        return C["red"]

    def _severity_color(self, t):
        t = t.lower()
        if t in ["clear", "minimal", "none", "fine", "excellent", "even", "good"]:
            return C["green"]
        if t in ["mild", "normal"]:
            return C["green_dark"]
        if t in ["moderate", "average", "visible", "below average", "uneven"]:
            return C["yellow"]
        if t in ["severe", "significant", "poor", "enlarged"]:
            return C["red"]
        return C["text3"]

    def _severity_bg(self, t):
        t = t.lower()
        if t in ["clear", "minimal", "none", "fine", "excellent", "even", "good"]:
            return C["green_bg"]
        if t in ["mild", "normal"]:
            return C["green_bg"]
        if t in ["moderate", "average", "visible", "below average", "uneven"]:
            return C["yellow_bg"]
        if t in ["severe", "significant", "poor", "enlarged"]:
            return C["red_bg"]
        return C["bg"]

    def _clean(self, text):
        clean = ""
        for ch in text:
            try:
                ch.encode("cp1252")
                clean += ch
            except:
                pass
        return clean.strip()

    # ═══════════════════════════════════════════════
    #  IMAGE / CAMERA
    # ═══════════════════════════════════════════════

    def _load_image(self):
        fp = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp")])
        if not fp:
            return
        img = cv2.imread(fp)
        if img is None:
            messagebox.showerror("Error", "Failed to load image.")
            return
        self.image = resize_image(img, 800, 800)
        self.results = None
        self.visualizations = None
        self.btn_analyze.config(state=tk.NORMAL)
        self.btn_save.config(state=tk.DISABLED)
        self._show_preview_screen()

    def _capture_from_camera(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot access camera.")
            return
        messagebox.showinfo("Camera", "SPACE = Capture\nESC = Cancel")
        captured = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            disp = cv2.flip(frame, 1)
            h, w = disp.shape[:2]
            cx, cy = w // 2, h // 2
            cv2.ellipse(disp, (cx, cy), (150, 200), 0, 0, 360, (0, 255, 0), 2)
            cv2.putText(disp, "SPACE: Capture | ESC: Cancel",
                        (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 1)
            cv2.imshow("Camera", disp)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            elif key == 32:
                captured = cv2.flip(frame, 1)
                break
        cap.release()
        cv2.destroyAllWindows()
        if captured is not None:
            self.image = resize_image(captured, 800, 800)
            self.results = None
            self.btn_analyze.config(state=tk.NORMAL)
            self.btn_save.config(state=tk.DISABLED)
            self._show_preview_screen()

    # ═══════════════════════════════════════════════
    #  ANALYSIS
    # ═══════════════════════════════════════════════

    def _start_analysis(self):
        if self.image is None or self.is_analyzing:
            return
        self.is_analyzing = True
        self.btn_analyze.config(state=tk.DISABLED)
        self._show_loading_screen()
        threading.Thread(target=self._run_analysis, daemon=True).start()

    def _run_analysis(self):
        try:
            self.results = self.analyzer.analyze(self.image, detailed=True)
            self.visualizations = self.analyzer.create_visualization(
                self.image, self.results)
            self.root.after(0, self._on_done)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: self._on_err(str(e)))

    def _on_done(self):
        self.is_analyzing = False
        if hasattr(self, "progress"):
            self.progress.stop()
        self.btn_analyze.config(state=tk.NORMAL)
        self.btn_save.config(state=tk.NORMAL)
        if self.results.get("status") == "error":
            messagebox.showerror("Error", self.results.get("error", "Unknown"))
            self._show_upload_screen()
            return
        self._show_results_screen()

    def _on_err(self, msg):
        self.is_analyzing = False
        if hasattr(self, "progress"):
            self.progress.stop()
        self.btn_analyze.config(state=tk.NORMAL)
        messagebox.showerror("Error", f"Analysis failed:\n{msg}")
        self._show_upload_screen()

    # ═══════════════════════════════════════════════
    #  SAVE
    # ═══════════════════════════════════════════════

    def _save_results(self):
        if not self.results:
            return
        d = filedialog.askdirectory(title="Save To")
        if not d:
            return
        try:
            txt = self.report_gen.generate_text_report(self.results)
            with open(os.path.join(d, "skin_report.txt"), "w", encoding="utf-8") as f:
                f.write(txt)
            if self.visualizations:
                for name, img in self.visualizations.items():
                    cv2.imwrite(os.path.join(d, f"skin_{name}.png"), img)
            if self.image is not None:
                cv2.imwrite(os.path.join(d, "original.png"), self.image)
            messagebox.showinfo("Saved", f"Results saved to:\n{d}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ═══════════════════════════════════════════════
    #  RUN
    # ═══════════════════════════════════════════════

    def run(self):
        self.root.mainloop()


def main():
    app = SkinAnalysisApp()
    app.run()


if __name__ == "__main__":
    main()