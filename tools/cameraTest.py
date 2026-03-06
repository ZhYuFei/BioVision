import cv2
import numpy as np
import time

class CameraParamController:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self.window_name = "Camera Control"
        self.trackbars_created = False
        self.show_info = True
        self.flip_mode = 0  # 0: no flip, 1: horizontal, 2: vertical, 3: 180° rotate
        self.param_values = {}  # Store current parameter values
        self.control_window_name = "Parameter Control"
        
        # Camera parameter configurations based on your camera specs
        self.param_configs = {
            'Brightness': {
                'prop': cv2.CAP_PROP_BRIGHTNESS,
                'min': -64,
                'max': 64,
                'default': 0,
                'step': 1
            },
            'Contrast': {
                'prop': cv2.CAP_PROP_CONTRAST,
                'min': 0,
                'max': 95,
                'default': 2,
                'step': 1
            },
            'Saturation': {
                'prop': cv2.CAP_PROP_SATURATION,
                'min': 0,
                'max': 255,
                'default': 60,
                'step': 1
            },
            'Sharpness': {
                'prop': cv2.CAP_PROP_SHARPNESS,
                'min': 0,
                'max': 7,
                'default': 0,
                'step': 1
            },
            'Gain': {
                'prop': cv2.CAP_PROP_GAIN,
                'min': 0,
                'max': 255,
                'default': 100,
                'step': 1
            },
            'Gamma': {
                'prop': cv2.CAP_PROP_GAMMA,
                'min': 64,
                'max': 300,
                'default': 100,
                'step': 1
            },
            'Hue': {
                'prop': cv2.CAP_PROP_HUE,
                'min': -2000,
                'max': 2000,
                'default': 0,
                'step': 10
            },
            'Exposure': {
                'prop': cv2.CAP_PROP_EXPOSURE,
                'min': -13,
                'max': 0,
                'default': -6,
                'step': 1
            },
            'White Balance': {
                'prop': cv2.CAP_PROP_WB_TEMPERATURE,
                'min': 2800,
                'max': 6500,
                'default': 4600,
                'step': 100
            },
            'Focus': {
                'prop': cv2.CAP_PROP_FOCUS,
                'min': 0,
                'max': 160,
                'default': 100,
                'step': 1
            },
            'Zoom': {  # Added Zoom parameter
                'prop': cv2.CAP_PROP_ZOOM,
                'min': 0,
                'max': 260,
                'default': 0,
                'step': 1
            },
            'Pan': {  # Added Pan parameter
                'prop': cv2.CAP_PROP_PAN,
                'min': -180,
                'max': 180,
                'default': 0,
                'step': 1
            },
            'Tilt': {  # Added Tilt parameter
                'prop': cv2.CAP_PROP_TILT,
                'min': -180,
                'max': 180,
                'default': 0,
                'step': 1
            }
        }
    
    def open_camera(self, width=1280, height=720):
        """Open camera"""
        # Windows: use DirectShow
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        
        if not self.cap.isOpened():
            # Try other backends
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                print(f"Error: Cannot open camera ID {self.camera_id}")
                return False
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Get actual resolution
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Camera opened, resolution: {actual_width}x{actual_height}")
        print(f"Press 'h' to show/hide help info")
        print(f"Press 's' to save current frame")
        print(f"Press 'f' to toggle flip mode")
        print(f"Press 'r' to reset all parameters")
        print(f"Press ESC or 'q' to quit")
        
        return True
    
    def create_control_window(self):
        """Create parameter control window"""
        cv2.namedWindow(self.control_window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.control_window_name, 400, 800)  # Increased height
        
        # Create trackbars for all parameters
        for param_name, config in self.param_configs.items():
            # Calculate trackbar range
            trackbar_min = 0
            trackbar_max = config['max'] - config['min']
            
            # Special handling for parameters that can be negative
            if config['min'] < 0:
                trackbar_max = config['max'] - config['min']
            
            cv2.createTrackbar(
                param_name,
                self.control_window_name,
                config['default'] - config['min'],  # Trackbar start value
                trackbar_max,  # Trackbar range
                lambda x: None
            )
            # Set initial value
            cv2.setTrackbarPos(
                param_name,
                self.control_window_name,
                config['default'] - config['min']
            )
            self.param_values[param_name] = config['default']
        
        # Create auto mode controls
        cv2.createTrackbar(
            'Auto Exposure',
            self.control_window_name,
            1, 1, lambda x: None
        )
        
        cv2.createTrackbar(
            'Auto White Balance',
            self.control_window_name,
            1, 1, lambda x: None
        )
        
        cv2.createTrackbar(
            'Auto Focus',
            self.control_window_name,
            1, 1, lambda x: None
        )
        
        # Create flip mode selector
        flip_modes = ['No Flip', 'Horizontal', 'Vertical', 'Rotate 180°']
        cv2.createTrackbar(
            'Flip Mode',
            self.control_window_name,
            0, 3, lambda x: None
        )
        
        self.trackbars_created = True
        print("Parameter control window created")
    
    def update_parameters_from_trackbars(self):
        """Update camera parameters from trackbars"""
        if not self.trackbars_created or not self.cap:
            return
        
        # Update all parameters
        for param_name, config in self.param_configs.items():
            trackbar_value = cv2.getTrackbarPos(param_name, self.control_window_name)
            actual_value = trackbar_value + config['min']
            
            if actual_value != self.param_values.get(param_name):
                success = self.cap.set(config['prop'], actual_value)
                if success:
                    self.param_values[param_name] = actual_value
                else:
                    # If setting failed, get actual value
                    actual_set_value = self.cap.get(config['prop'])
                    self.param_values[param_name] = actual_set_value
        
        # Update flip mode
        new_flip_mode = cv2.getTrackbarPos('Flip Mode', self.control_window_name)
        if new_flip_mode != self.flip_mode:
            self.flip_mode = new_flip_mode
        
        # Update auto modes
        auto_exp = cv2.getTrackbarPos('Auto Exposure', self.control_window_name)
        auto_wb = cv2.getTrackbarPos('Auto White Balance', self.control_window_name)
        auto_focus = cv2.getTrackbarPos('Auto Focus', self.control_window_name)
        
        # Set auto exposure mode
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, auto_exp)
        
        # Set auto white balance mode
        self.cap.set(cv2.CAP_PROP_AUTO_WB, auto_wb)
        
        # Set auto focus mode
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, auto_focus)
        
        # Enable/disable manual controls based on auto mode
        if auto_exp:
            cv2.setTrackbarMin('Exposure', self.control_window_name, 0)
            cv2.setTrackbarMax('Exposure', self.control_window_name, 0)
        else:
            min_val = self.param_configs['Exposure']['min']
            max_val = self.param_configs['Exposure']['max']
            cv2.setTrackbarMin('Exposure', self.control_window_name, 0)
            cv2.setTrackbarMax('Exposure', self.control_window_name, max_val - min_val)
            current_exp = self.cap.get(cv2.CAP_PROP_EXPOSURE)
            if min_val <= current_exp <= max_val:
                cv2.setTrackbarPos('Exposure', self.control_window_name, int(current_exp - min_val))
        
        if auto_wb:
            cv2.setTrackbarMin('White Balance', self.control_window_name, 0)
            cv2.setTrackbarMax('White Balance', self.control_window_name, 0)
        else:
            min_val = self.param_configs['White Balance']['min']
            max_val = self.param_configs['White Balance']['max']
            step = self.param_configs['White Balance']['step']
            cv2.setTrackbarMin('White Balance', self.control_window_name, 0)
            cv2.setTrackbarMax('White Balance', self.control_window_name, (max_val - min_val) // step)
            current_wb = self.cap.get(cv2.CAP_PROP_WB_TEMPERATURE)
            if min_val <= current_wb <= max_val:
                cv2.setTrackbarPos('White Balance', self.control_window_name, int((current_wb - min_val) // step))
        
        if auto_focus:
            cv2.setTrackbarMin('Focus', self.control_window_name, 0)
            cv2.setTrackbarMax('Focus', self.control_window_name, 0)
        else:
            min_val = self.param_configs['Focus']['min']
            max_val = self.param_configs['Focus']['max']
            cv2.setTrackbarMin('Focus', self.control_window_name, 0)
            cv2.setTrackbarMax('Focus', self.control_window_name, max_val - min_val)
            current_focus = self.cap.get(cv2.CAP_PROP_FOCUS)
            if min_val <= current_focus <= max_val:
                cv2.setTrackbarPos('Focus', self.control_window_name, int(current_focus - min_val))
    
    def process_frame(self, frame):
        """Process frame"""
        if frame is None:
            return None
        
        processed = frame.copy()
        
        # Apply flip/rotation
        if self.flip_mode == 1:
            processed = cv2.flip(processed, 1)  # Horizontal flip
        elif self.flip_mode == 2:
            processed = cv2.flip(processed, 0)  # Vertical flip
        elif self.flip_mode == 3:
            processed = cv2.rotate(processed, cv2.ROTATE_180)  # 180° rotation
        
        return processed
    
    def draw_info_overlay(self, frame):
        """Draw info overlay on image"""
        if not self.show_info:
            return frame
        
        overlay = frame.copy()
        height, width = overlay.shape[:2]
        
        # Create semi-transparent black background
        info_height = 140
        cv2.rectangle(overlay, (0, 0), (width, info_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, overlay)
        
        # Draw text
        y_pos = 20
        line_height = 20
        
        # Title
        cv2.putText(overlay, "Real-time Camera Control", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        y_pos += line_height
        
        # Display key parameters in two columns
        key_params_left = ['Brightness', 'Contrast', 'Exposure', 'Gain', 'White Balance']
        key_params_right = ['Zoom', 'Focus', 'Pan', 'Tilt', 'Sharpness']
        
        # Left column
        y_left = y_pos
        for param in key_params_left:
            if param in self.param_values:
                value = self.param_values[param]
                if param == 'White Balance':
                    text = f"{param}: {value}K"
                else:
                    text = f"{param}: {value}"
                cv2.putText(overlay, text, (10, y_left),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_left += line_height
        
        # Right column
        y_right = y_pos
        for param in key_params_right:
            if param in self.param_values:
                value = self.param_values[param]
                text = f"{param}: {value}"
                cv2.putText(overlay, text, (width // 2, y_right),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_right += line_height
        
        # Display mode info
        auto_exp = cv2.getTrackbarPos('Auto Exposure', self.control_window_name) if self.trackbars_created else 1
        auto_wb = cv2.getTrackbarPos('Auto White Balance', self.control_window_name) if self.trackbars_created else 1
        auto_focus = cv2.getTrackbarPos('Auto Focus', self.control_window_name) if self.trackbars_created else 1
        
        mode_text = f"Modes: Exp:{'A' if auto_exp else 'M'}, WB:{'A' if auto_wb else 'M'}, Focus:{'A' if auto_focus else 'M'}"
        cv2.putText(overlay, mode_text, (10, y_left),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 100), 1)
        
        # Display flip mode
        flip_modes = ['No Flip', 'Horizontal', 'Vertical', 'Rotate 180°']
        flip_text = f"Flip: {flip_modes[self.flip_mode]}"
        cv2.putText(overlay, flip_text, (width // 2, y_right),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 255), 1)
        
        # Display help
        help_y = max(y_left, y_right) + line_height
        help_text = "Press 'h' hide | 's' save | 'f' flip | 'r' reset | 'q' quit"
        cv2.putText(overlay, help_text, (10, help_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 100, 200), 1)
        
        return overlay
    
    def save_current_settings(self):
        """Save current parameter settings"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"camera_settings_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Camera Parameters - Saved: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            for param_name, value in self.param_values.items():
                f.write(f"{param_name}: {value}\n")
            
            f.write(f"\nFlip Mode: {self.flip_mode}\n")
            
            if self.trackbars_created:
                auto_exp = cv2.getTrackbarPos('Auto Exposure', self.control_window_name)
                auto_wb = cv2.getTrackbarPos('Auto White Balance', self.control_window_name)
                auto_focus = cv2.getTrackbarPos('Auto Focus', self.control_window_name)
                
                f.write(f"\nAuto Modes:\n")
                f.write(f"  Auto Exposure: {'ON' if auto_exp else 'OFF'}\n")
                f.write(f"  Auto White Balance: {'ON' if auto_wb else 'OFF'}\n")
                f.write(f"  Auto Focus: {'ON' if auto_focus else 'OFF'}\n")
        
        print(f"Settings saved to: {filename}")
        return filename
    
    def reset_to_defaults(self):
        """Reset all parameters to defaults"""
        if not self.trackbars_created:
            return
        
        # Reset all parameters
        for param_name, config in self.param_configs.items():
            default_pos = config['default'] - config['min']
            cv2.setTrackbarPos(param_name, self.control_window_name, default_pos)
            self.param_values[param_name] = config['default']
            if self.cap:
                self.cap.set(config['prop'], config['default'])
        
        # Reset flip mode
        cv2.setTrackbarPos('Flip Mode', self.control_window_name, 0)
        self.flip_mode = 0
        
        # Reset auto modes
        cv2.setTrackbarPos('Auto Exposure', self.control_window_name, 1)
        cv2.setTrackbarPos('Auto White Balance', self.control_window_name, 1)
        cv2.setTrackbarPos('Auto Focus', self.control_window_name, 1)
        
        print("All parameters reset to defaults")
    
    def run(self):
        """Run main control loop"""
        if not self.open_camera():
            return
        
        # Create main window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 800, 600)
        
        # Create control window
        self.create_control_window()
        
        print("\n=== Starting Real-time Control ===")
        print("Adjust trackbars in the control window to change parameters")
        
        frame_count = 0
        start_time = time.time()
        fps = 0
        
        while True:
            # Read frame
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read frame")
                break
            
            # Update parameters
            self.update_parameters_from_trackbars()
            
            # Process frame
            processed_frame = self.process_frame(frame)
            
            # Calculate FPS
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed_time = time.time() - start_time
                fps = frame_count / elapsed_time
                frame_count = 0
                start_time = time.time()
            
            # Add FPS display
            if self.show_info:
                cv2.putText(processed_frame, f"FPS: {fps:.1f}", 
                           (processed_frame.shape[1] - 100, 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Add info overlay
            display_frame = self.draw_info_overlay(processed_frame)
            
            # Display image
            cv2.imshow(self.window_name, display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27 or key == ord('q'):  # ESC or 'q'
                print("Exiting program")
                break
            elif key == ord('h'):  # Show/hide help
                self.show_info = not self.show_info
                print(f"Help info: {'SHOW' if self.show_info else 'HIDE'}")
            elif key == ord('s'):  # Save current frame
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.png"
                cv2.imwrite(filename, processed_frame)
                print(f"Image saved: {filename}")
            elif key == ord('f'):  # Toggle flip mode
                self.flip_mode = (self.flip_mode + 1) % 4
                if self.trackbars_created:
                    cv2.setTrackbarPos('Flip Mode', self.control_window_name, self.flip_mode)
                flip_modes = ['No Flip', 'Horizontal Flip', 'Vertical Flip', 'Rotate 180°']
                print(f"Flip mode: {flip_modes[self.flip_mode]}")
            elif key == ord('r'):  # Reset parameters
                self.reset_to_defaults()
            elif key == ord('p'):  # Save settings
                self.save_current_settings()
            elif key == ord('c'):  # Switch to control window
                cv2.setWindowProperty(self.control_window_name, cv2.WND_PROP_TOPMOST, 1)
            elif key == ord(' '):  # Spacebar pause/resume
                print("Paused, press any key to continue...")
                cv2.waitKey(0)
        
        # Cleanup
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Program terminated")

# Main program
if __name__ == "__main__":
    print("=== OpenCV Camera Control with Zoom ===")
    print("Starting camera control program...")
    
    # Create and run the camera controller
    controller = CameraParamController(camera_id=0)
    controller.run()
