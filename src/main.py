import cv2
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import config
from trackers import FaceTracker, HandTracker
from osc_sender import VRChatOSCSender, OSCDebugger, ParameterSmoother


class WebcamTracker:
    """Main class for webcam tracking"""

    def __init__(self):
        self.camera = None
        self.face_tracker = FaceTracker()
        self.hand_tracker = HandTracker()
        self.osc_sender = VRChatOSCSender()
        self.debugger = OSCDebugger()
        self.face_smoother = ParameterSmoother(smoothing_factor=0.7)
        self.hand_smoother = ParameterSmoother(smoothing_factor=0.6)

        self.is_running = False
        self.tracking_thread = None
        self.display_thread = None

        # Statistics
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.current_fps = 0

        # Variables for GUI
        self.face_data = {}
        self.hand_data = {}

        print("VRChat webcam tracker initialization complete")

    def initialize_camera(self) -> bool:
        """Initialize camera"""
        try:
            self.camera = cv2.VideoCapture(config.CAMERA_INDEX)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, config.FPS)

            if not self.camera.isOpened():
                print("Error: Cannot open camera")
                return False

            print(
                f"Camera initialization successful: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.FPS}FPS"
            )
            return True

        except Exception as e:
            print(f"Camera initialization error: {e}")
            return False

    def start_tracking(self):
        """Start tracking"""
        if not self.initialize_camera():
            return False

        # OSC connection test
        if not self.osc_sender.test_connection():
            print(
                "Warning: Connection test to VRChat failed. Please check if VRChat is running and OSC is enabled."
            )

        self.is_running = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()

        print("Tracking started")
        return True

    def stop_tracking(self):
        """Stop tracking"""
        self.is_running = False

        if self.tracking_thread:
            self.tracking_thread.join(timeout=2.0)

        if self.camera:
            self.camera.release()
            self.camera = None

        cv2.destroyAllWindows()
        print("Tracking stopped")

    def _tracking_loop(self):
        """Main tracking loop"""
        while self.is_running:
            try:
                if self.camera is None:
                    print("Camera is not initialized")
                    break
                ret, frame = self.camera.read()
                if not ret:
                    print("Cannot read frame from camera")
                    break

                # Flip frame horizontally (mirror image)
                frame = cv2.flip(frame, 1)

                # Face expression tracking
                face_data = self.face_tracker.detect_face_expression(frame)
                smoothed_face_data = self.face_smoother.smooth_parameters(face_data)

                # Hand/arm tracking
                hand_data = self.hand_tracker.detect_hand_pose(frame)
                smoothed_hand_data = self.hand_smoother.smooth_parameters(hand_data)

                # Send data to VRChat
                self.osc_sender.send_combined_data(
                    smoothed_face_data, smoothed_hand_data
                )

                # Output debug information
                self.debugger.log_parameters(smoothed_face_data, smoothed_hand_data)

                # Save data for GUI
                self.face_data = smoothed_face_data
                self.hand_data = smoothed_hand_data

                # Draw landmarks on frame
                self._draw_landmarks(frame)

                # Calculate FPS
                self._update_fps()

                # Display frame
                cv2.putText(
                    frame,
                    f"FPS: {self.current_fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    "Press 'q' to quit",
                    (10, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

                cv2.imshow("VRChat Webcam Tracker", frame)

                # Exit with ESC key or 'q' key
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:
                    break

            except Exception as e:
                print(f"Tracking loop error: {e}")
                break

        self.stop_tracking()

    def _draw_landmarks(self, frame):
        """Draw landmarks on frame"""
        # Display current parameter values on screen
        y_offset = 60
        for param, value in self.face_data.items():
            text = f"{param}: {value:.2f}"
            cv2.putText(
                frame,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            y_offset += 20

        # Also display hand parameters
        for param, value in self.hand_data.items():
            text = f"{param}: {value:.2f}"
            cv2.putText(
                frame,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            y_offset += 20

    def _update_fps(self):
        """Update FPS"""
        self.fps_counter += 1
        current_time = time.time()

        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.last_fps_time)
            self.fps_counter = 0
            self.last_fps_time = current_time


class TrackerGUI:
    """GUI class for tracking application"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VRChat Webcam Tracker")
        self.root.geometry("600x500")

        self.tracker = WebcamTracker()
        self.is_tracking = False

        self.setup_gui()
        self.update_status()

    def setup_gui(self):
        """Setup GUI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Title
        title_label = ttk.Label(
            main_frame, text="VRChat Webcam Tracker", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # OSC settings
        ttk.Label(settings_frame, text="VRChat IP:").grid(row=0, column=0, sticky=tk.W)
        self.ip_var = tk.StringVar(value=config.VRCHAT_OSC_IP)
        ip_entry = ttk.Entry(settings_frame, textvariable=self.ip_var)
        ip_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        ttk.Label(settings_frame, text="Port:").grid(row=1, column=0, sticky=tk.W)
        self.port_var = tk.StringVar(value=str(config.VRCHAT_OSC_PORT))
        port_entry = ttk.Entry(settings_frame, textvariable=self.port_var)
        port_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0))

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.start_button = ttk.Button(
            control_frame, text="Start Tracking", command=self.toggle_tracking
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        test_button = ttk.Button(
            control_frame, text="Test Connection", command=self.test_connection
        )
        test_button.pack(side=tk.LEFT)

        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.status_label = ttk.Label(status_frame, text="Standby")
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        # Parameter display
        params_frame = ttk.LabelFrame(
            main_frame, text="Current Parameters", padding="10"
        )
        params_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(10, 0))

        self.params_text = tk.Text(params_frame, height=15, width=70)
        scrollbar = ttk.Scrollbar(
            params_frame, orient=tk.VERTICAL, command=self.params_text.yview
        )
        self.params_text.configure(yscrollcommand=scrollbar.set)

        self.params_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Set grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(0, weight=1)
        params_frame.rowconfigure(0, weight=1)

    def toggle_tracking(self):
        """Toggle tracking start/stop"""
        if not self.is_tracking:
            # Update settings
            try:
                config.VRCHAT_OSC_IP = self.ip_var.get()
                config.VRCHAT_OSC_PORT = int(self.port_var.get())
                self.tracker.osc_sender = VRChatOSCSender()
            except ValueError:
                messagebox.showerror(
                    "Error", "Please enter a numeric value for the port number"
                )
                return

            if self.tracker.start_tracking():
                self.is_tracking = True
                self.start_button.config(text="Stop Tracking")
                self.status_label.config(text="Tracking...")
            else:
                messagebox.showerror("Error", "Failed to initialize camera")
        else:
            self.tracker.stop_tracking()
            self.is_tracking = False
            self.start_button.config(text="Start Tracking")
            self.status_label.config(text="Stopped")

    def test_connection(self):
        """Test connection to VRChat"""
        try:
            config.VRCHAT_OSC_IP = self.ip_var.get()
            config.VRCHAT_OSC_PORT = int(self.port_var.get())
            osc_sender = VRChatOSCSender()

            if osc_sender.test_connection():
                messagebox.showinfo(
                    "Connection Test", "Connection test to VRChat was successful!"
                )
            else:
                messagebox.showwarning(
                    "Connection Test",
                    "Connection test to VRChat failed.\nPlease check if VRChat is running and OSC is enabled.",
                )
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter a numeric value for the port number"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred during connection test: {e}")

    def update_status(self):
        """Update status and parameter display"""
        if self.is_tracking:
            # Display parameter values
            params_text = "【Face Parameters】\n"
            for param, value in self.tracker.face_data.items():
                params_text += f"  {param}: {value:.3f}\n"

            params_text += "\n【Hand/Arm Parameters】\n"
            for param, value in self.tracker.hand_data.items():
                params_text += f"  {param}: {value:.3f}\n"

            params_text += f"\nFPS: {self.tracker.current_fps:.1f}"

            self.params_text.delete(1.0, tk.END)
            self.params_text.insert(tk.END, params_text)

        # Re-execute after 1 second
        self.root.after(1000, self.update_status)

    def run(self):
        """Start GUI"""
        try:
            self.root.mainloop()
        finally:
            if self.is_tracking:
                self.tracker.stop_tracking()


def main():
    """Main function"""
    print("Starting VRChat webcam tracker...")

    # Start in GUI mode
    gui = TrackerGUI()
    gui.run()


if __name__ == "__main__":
    main()
