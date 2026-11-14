# #!/usr/bin/env python3
# """
# Skin Analysis Tool - Main Entry Point

# Usage:
#     python main.py                          # Launch GUI
#     python main.py --cli image.jpg          # CLI mode
#     python main.py --cli image.jpg --save   # CLI mode with save
#     python main.py --camera                 # Camera capture + analyze
# """

# import argparse
# import sys
# import cv2
# import os

# from skin_analyzer import SkinAnalyzer
# from report_generator import ReportGenerator
# from utils import resize_image


# def run_cli(image_path: str, save: bool = False, output_dir: str = "output"):
#     """Run analysis in CLI mode."""
#     print(f"\n{'=' * 60}")
#     print(f"  SKIN ANALYSIS TOOL - CLI MODE")
#     print(f"{'=' * 60}\n")

#     # Load image
#     if not os.path.exists(image_path):
#         print(f"[ERROR] Image not found: {image_path}")
#         sys.exit(1)

#     image = cv2.imread(image_path)
#     if image is None:
#         print(f"[ERROR] Failed to load image: {image_path}")
#         sys.exit(1)

#     image = resize_image(image, 800, 800)
#     print(f"[INFO] Image loaded: {image_path}")
#     print(f"[INFO] Image size: {image.shape[1]}x{image.shape[0]}")

#     # Initialize analyzer
#     analyzer = SkinAnalyzer(use_mediapipe=True)

#     # Run analysis
#     results = analyzer.analyze(image, detailed=True)

#     if results.get("status") == "error":
#         print(f"\n[ERROR] {results.get('error', 'Unknown error')}")
#         sys.exit(1)

#     # Generate report
#     report_gen = ReportGenerator()
#     report_text = report_gen.generate_text_report(results)
#     print(report_text)

#     # Save results if requested
#     if save:
#         os.makedirs(output_dir, exist_ok=True)

#         # Save report
#         report_gen.save_report(
#             report_text,
#             os.path.join(output_dir, "skin_analysis_report.txt")
#         )

#         # Create visualizations
#         visualizations = analyzer.create_visualization(image, results)

#         for name, vis_img in visualizations.items():
#             filepath = os.path.join(output_dir, f"skin_{name}.png")
#             cv2.imwrite(filepath, vis_img)
#             print(f"[SAVED] {filepath}")

#         # Visual report
#         vis_report = report_gen.create_visual_report(
#             image, visualizations, results
#         )
#         cv2.imwrite(
#             os.path.join(output_dir, "visual_report.png"), vis_report
#         )
#         print(f"\n[INFO] All results saved to: {output_dir}/")


# def run_camera_analysis():
#     """Capture from camera and analyze."""
#     print("\n[INFO] Opening camera...")
#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         print("[ERROR] Cannot access camera")
#         sys.exit(1)

#     print("[INFO] Press SPACE to capture, ESC to exit")

#     captured = None
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         display = cv2.flip(frame, 1)
#         h, w = display.shape[:2]

#         # Draw guide
#         cx, cy = w // 2, h // 2
#         cv2.ellipse(display, (cx, cy), (150, 200), 0, 0, 360, (0, 255, 0), 2)
#         cv2.putText(
#             display, "Align face | SPACE: Capture | ESC: Exit",
#             (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
#         )

#         cv2.imshow("Skin Analysis - Camera", display)

#         key = cv2.waitKey(1) & 0xFF
#         if key == 27:
#             break
#         elif key == 32:
#             captured = cv2.flip(frame, 1)
#             break

#     cap.release()
#     cv2.destroyAllWindows()

#     if captured is not None:
#         print("[INFO] Image captured! Starting analysis...")

#         # Save captured image
#         cv2.imwrite("captured_face.jpg", captured)

#         # Run analysis
#         run_cli("captured_face.jpg", save=True, output_dir="camera_output")
#     else:
#         print("[INFO] No image captured.")


# def run_realtime():
#     """Run real-time skin analysis on camera feed (simplified)."""
#     print("\n[INFO] Starting real-time analysis...")
#     print("[INFO] Press 'q' to quit, 's' to snapshot & full analyze")

#     analyzer = SkinAnalyzer(use_mediapipe=True)

#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         print("[ERROR] Cannot access camera")
#         return

#     from skin_detector import SkinDetector
#     from face_detector import FaceDetector

#     skin_det = SkinDetector()
#     face_det = FaceDetector(use_mediapipe=True)

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame = cv2.flip(frame, 1)
#         display = frame.copy()

#         # Quick face detection
#         face = face_det.detect_face(frame)
#         if face is not None:
#             x, y, w, h = face
#             cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)

#             # Quick skin detection
#             face_mask = face_det.get_face_mask(frame)
#             if face_mask is not None:
#                 _, skin_mask = skin_det.extract_skin(frame, face_mask)
#                 skin_pct = skin_det.get_skin_percentage(skin_mask, face_mask)

#                 cv2.putText(
#                     display, f"Skin: {skin_pct:.0f}%",
#                     (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
#                     0.5, (0, 255, 0), 1
#                 )

#         cv2.putText(
#             display, "q: Quit | s: Snapshot & Full Analysis",
#             (10, frame.shape[0] - 15),
#             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
#         )

#         cv2.imshow("Real-Time Skin Analysis", display)

#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('q'):
#             break
#         elif key == ord('s'):
#             cv2.imwrite("snapshot.jpg", frame)
#             print("\n[INFO] Snapshot saved! Running full analysis...")
#             cap.release()
#             cv2.destroyAllWindows()
#             run_cli("snapshot.jpg", save=True, output_dir="snapshot_output")
#             return

#     cap.release()
#     cv2.destroyAllWindows()


# def main():
#     parser = argparse.ArgumentParser(
#         description="AI Skin Analysis Tool",
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         epilog="""
# Examples:
#   python main.py                         Launch GUI application
#   python main.py --cli face.jpg          Analyze image (CLI)
#   python main.py --cli face.jpg --save   Analyze and save results
#   python main.py --camera                Camera capture + analyze
#   python main.py --realtime              Real-time camera analysis
#         """
#     )

#     parser.add_argument(
#         "--cli", type=str, metavar="IMAGE",
#         help="Run in CLI mode with specified image"
#     )
#     parser.add_argument(
#         "--save", action="store_true",
#         help="Save analysis results (CLI mode)"
#     )
#     parser.add_argument(
#         "--output", type=str, default="output",
#         help="Output directory for saved results"
#     )
#     parser.add_argument(
#         "--camera", action="store_true",
#         help="Capture from camera and analyze"
#     )
#     parser.add_argument(
#         "--realtime", action="store_true",
#         help="Real-time camera analysis"
#     )
#     parser.add_argument(
#         "--no-mediapipe", action="store_true",
#         help="Disable MediaPipe (use Haar Cascade)"
#     )

#     args = parser.parse_args()

#     if args.no_mediapipe:
#         import config
#         config.USE_MEDIAPIPE = False

#     if args.cli:
#         run_cli(args.cli, save=args.save, output_dir=args.output)
#     elif args.camera:
#         run_camera_analysis()
#     elif args.realtime:
#         run_realtime()
#     else:
#         # Launch GUI
#         from gui_app import SkinAnalysisApp
#         app = SkinAnalysisApp()
#         app.run()


# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3
"""
Skin Insights — AI-Powered Skin Analysis Tool
"""

import argparse
import sys
import cv2
import os

from skin_analyzer import SkinAnalyzer
from report_generator import ReportGenerator
from utils import resize_image


def run_cli(image_path, save=False, output_dir="output"):
    print(f"\n{'═' * 50}")
    print(f"  SKIN INSIGHTS — AI Skin Analysis")
    print(f"{'═' * 50}\n")

    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        sys.exit(1)

    image = cv2.imread(image_path)
    if image is None:
        print(f"[ERROR] Failed to load: {image_path}")
        sys.exit(1)

    image = resize_image(image, 800, 800)
    analyzer = SkinAnalyzer(use_mediapipe=False)
    results = analyzer.analyze(image, detailed=True)

    if results.get("status") == "error":
        print(f"\n[ERROR] {results.get('error')}")
        sys.exit(1)

    report_gen = ReportGenerator()
    print(report_gen.generate_text_report(results))

    # Print personalized concerns
    concerns = results.get("recommendations", {}).get("concerns", [])
    if concerns:
        print("\n🎯 YOUR TOP CONCERNS:")
        for c in concerns:
            print(f"  {c['icon']} {c['name']} — {c['severity']} — {c['details']}")

    # Print routine
    routine = results.get("routine", {})
    if routine:
        print("\n🌅 MORNING ROUTINE:")
        for step in routine.get("morning_routine", []):
            print(f"  {step['icon']} Step {step['step']}: {step['product']} → {step['ingredient']}")

        print("\n🌙 NIGHT ROUTINE:")
        for step in routine.get("night_routine", []):
            print(f"  {step['icon']} Step {step['step']}: {step['product']} → {step['ingredient']}")

    if save:
        os.makedirs(output_dir, exist_ok=True)
        report_gen.save_report(
            report_gen.generate_text_report(results),
            os.path.join(output_dir, "report.txt")
        )
        vis = analyzer.create_visualization(image, results)
        for name, img in vis.items():
            cv2.imwrite(os.path.join(output_dir, f"{name}.png"), img)
        print(f"\n[SAVED] Results saved to {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Skin Insights — AI Skin Analysis")
    parser.add_argument("--cli", type=str, help="Analyze image (CLI mode)")
    parser.add_argument("--save", action="store_true", help="Save results")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    args = parser.parse_args()

    if args.cli:
        run_cli(args.cli, save=args.save, output_dir=args.output)
    else:
        from gui_app import SkinAnalysisApp
        app = SkinAnalysisApp()
        app.run()


if __name__ == "__main__":
    main()