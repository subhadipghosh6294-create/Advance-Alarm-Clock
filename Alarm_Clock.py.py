
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import time
import threading
import pygame
import json
import os
from pathlib import Path


class AlarmClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Alarm Clock")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
    
        pygame.mixer.init()
        
        
        self.alarms = []
        self.current_playing_alarm = None
        self.alarm_sounds = {
            'Default Beep': None,
            'Classic Alarm': None,
            'Gentle Wake': None,
            'Custom Sound': None
        }
        self.settings_file = 'alarm_settings.json'
        
     
        self.load_settings()
        
       
       
        self.setup_gui()
        
        
        
        self.update_clock()
        
      
      
        self.check_alarms_thread = threading.Thread(target=self.monitor_alarms, daemon=True)
        self.check_alarms_thread.start()
    
    def setup_gui(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=10)
        
        title_label = tk.Label(title_frame, text="Advanced Alarm Clock", 
                              font=('Arial', 24, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack()
        
        # Current time display
        self.time_frame = tk.Frame(self.root, bg='#34495e', relief='raised', bd=2)
        self.time_frame.pack(pady=10, padx=20, fill='x')
        
        self.time_label = tk.Label(self.time_frame, text="", 
                                  font=('Arial', 18, 'bold'), 
                                  fg='#e74c3c', bg='#34495e')
        self.time_label.pack(pady=10)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Add/Edit Alarm
        left_frame = tk.LabelFrame(main_frame, text="Set New Alarm", 
                                  font=('Arial', 12, 'bold'),
                                  fg='#ecf0f1', bg='#34495e')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Time input
        time_frame = tk.Frame(left_frame, bg='#34495e')
        time_frame.pack(pady=10)
        
        tk.Label(time_frame, text="Time:", 
                font=('Arial', 10, 'bold'), 
                fg='#ecf0f1', bg='#34495e').grid(row=0, column=0, sticky='w')
        
        # Hour
        self.hour_var = tk.StringVar()
        hour_combo = ttk.Combobox(time_frame, textvariable=self.hour_var, 
                                 values=[f"{i:02d}" for i in range(24)], 
                                 width=3, state='readonly')
        hour_combo.grid(row=0, column=1, padx=5)
        hour_combo.set("07")
        
        tk.Label(time_frame, text=":", 
                font=('Arial', 12, 'bold'), 
                fg='#ecf0f1', bg='#34495e').grid(row=0, column=2)
        
        # Minute
        self.minute_var = tk.StringVar()
        minute_combo = ttk.Combobox(time_frame, textvariable=self.minute_var,
                                   values=[f"{i:02d}" for i in range(60)],
                                   width=3, state='readonly')
        minute_combo.grid(row=0, column=3, padx=5)
        minute_combo.set("00")
        
        # Label input
        label_frame = tk.Frame(left_frame, bg='#34495e')
        label_frame.pack(pady=10, fill='x', padx=10)
        
        tk.Label(label_frame, text="Label:", 
                font=('Arial', 10, 'bold'), 
                fg='#ecf0f1', bg='#34495e').pack(anchor='w')
        
        self.label_var = tk.StringVar()
        self.label_entry = tk.Entry(label_frame, textvariable=self.label_var, 
                                   font=('Arial', 10), width=30)
        self.label_entry.pack(fill='x', pady=5)
        self.label_entry.insert(0, "Wake up!")
        
        # Sound selection
        sound_frame = tk.Frame(left_frame, bg='#34495e')
        sound_frame.pack(pady=10, fill='x', padx=10)
        
        tk.Label(sound_frame, text="Alarm Sound:", 
                font=('Arial', 10, 'bold'), 
                fg='#ecf0f1', bg='#34495e').pack(anchor='w')
        
        self.sound_var = tk.StringVar()
        self.sound_combo = ttk.Combobox(sound_frame, textvariable=self.sound_var,
                                       values=list(self.alarm_sounds.keys()),
                                       state='readonly', width=20)
        self.sound_combo.pack(side='left', pady=5)
        self.sound_combo.set("Default Beep")
        
        # Browse button for custom sound
        browse_btn = tk.Button(sound_frame, text="Browse", 
                              command=self.browse_sound_file,
                              bg='#3498db', fg='white', font=('Arial', 9))
        browse_btn.pack(side='left', padx=5)
        
        # Volume control
        volume_frame = tk.Frame(left_frame, bg='#34495e')
        volume_frame.pack(pady=10, fill='x', padx=10)
        
        tk.Label(volume_frame, text="Volume:", 
                font=('Arial', 10, 'bold'), 
                fg='#ecf0f1', bg='#34495e').pack(anchor='w')
        
        self.volume_var = tk.DoubleVar()
        self.volume_scale = tk.Scale(volume_frame, from_=0.0, to=1.0, 
                                    resolution=0.1, orient='horizontal',
                                    variable=self.volume_var, 
                                    bg='#34495e', fg='#ecf0f1',
                                    highlightbackground='#34495e')
        self.volume_scale.pack(fill='x', pady=5)
        self.volume_scale.set(0.7)
        
        # Snooze settings
        snooze_frame = tk.Frame(left_frame, bg='#34495e')
        snooze_frame.pack(pady=10, fill='x', padx=10)
        
        self.snooze_enabled = tk.BooleanVar()
        snooze_check = tk.Checkbutton(snooze_frame, text="Enable Snooze", 
                                     variable=self.snooze_enabled,
                                     bg='#34495e', fg='#ecf0f1', 
                                     selectcolor='#2c3e50',
                                     font=('Arial', 10, 'bold'))
        snooze_check.pack(anchor='w')
        
        tk.Label(snooze_frame, text="Snooze Duration (minutes):", 
                font=('Arial', 9), 
                fg='#ecf0f1', bg='#34495e').pack(anchor='w')
        
        self.snooze_duration = tk.IntVar()
        snooze_spin = tk.Spinbox(snooze_frame, from_=1, to=30, 
                                textvariable=self.snooze_duration,
                                width=5, font=('Arial', 9))
        snooze_spin.pack(anchor='w', pady=2)
        self.snooze_duration.set(5)
        
        # Repeat settings
        repeat_frame = tk.Frame(left_frame, bg='#34495e')
        repeat_frame.pack(pady=10, fill='x', padx=10)
        
        tk.Label(repeat_frame, text="Repeat:", 
                font=('Arial', 10, 'bold'), 
                fg='#ecf0f1', bg='#34495e').pack(anchor='w')
        
        self.repeat_var = tk.StringVar()
        repeat_combo = ttk.Combobox(repeat_frame, textvariable=self.repeat_var,
                                   values=["Once", "Daily", "Weekdays", "Weekends"],
                                   state='readonly', width=15)
        repeat_combo.pack(anchor='w', pady=2)
        repeat_combo.set("Once")
        
        # Add alarm button
        add_btn = tk.Button(left_frame, text="Add Alarm", 
                           command=self.add_alarm,
                           bg='#27ae60', fg='white', 
                           font=('Arial', 12, 'bold'),
                           relief='raised', bd=2)
        add_btn.pack(pady=20)
        
        # Right panel - Active Alarms
        right_frame = tk.LabelFrame(main_frame, text="Active Alarms", 
                                   font=('Arial', 12, 'bold'),
                                   fg='#ecf0f1', bg='#34495e')
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Alarms listbox with scrollbar
        list_frame = tk.Frame(right_frame, bg='#34495e')
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.alarms_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                        font=('Arial', 10), bg='#ecf0f1',
                                        selectmode='single')
        self.alarms_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.alarms_listbox.yview)
        
        # Control buttons
        control_frame = tk.Frame(right_frame, bg='#34495e')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        edit_btn = tk.Button(control_frame, text="Edit", 
                            command=self.edit_alarm,
                            bg='#f39c12', fg='white', 
                            font=('Arial', 10, 'bold'))
        edit_btn.pack(side='left', padx=5)
        
        delete_btn = tk.Button(control_frame, text="Delete", 
                              command=self.delete_alarm,
                              bg='#e74c3c', fg='white', 
                              font=('Arial', 10, 'bold'))
        delete_btn.pack(side='left', padx=5)
        
        toggle_btn = tk.Button(control_frame, text="Enable/Disable", 
                              command=self.toggle_alarm,
                              bg='#9b59b6', fg='white', 
                              font=('Arial', 10, 'bold'))
        toggle_btn.pack(side='left', padx=5)
        
        # Test sound button
        test_btn = tk.Button(control_frame, text="Test Sound", 
                            command=self.test_sound,
                            bg='#16a085', fg='white', 
                            font=('Arial', 10, 'bold'))
        test_btn.pack(side='right', padx=5)
    
    def update_clock(self):
        """Update the current time display"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        self.time_label.config(text=f"{current_date}\n{current_time}")
        self.root.after(1000, self.update_clock)
    
    def browse_sound_file(self):
        """Browse for custom sound file"""
        file_path = filedialog.askopenfilename(
            title="Select Alarm Sound",
            filetypes=[("Audio files", "*.mp3 *.wav *.ogg"), ("All files", "*.*")]
        )
        if file_path:
            self.alarm_sounds['Custom Sound'] = file_path
            self.sound_combo.set('Custom Sound')
            messagebox.showinfo("Success", f"Custom sound selected: {os.path.basename(file_path)}")
    
    def add_alarm(self):
        """Add a new alarm"""
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            label = self.label_var.get()
            sound = self.sound_var.get()
            volume = self.volume_var.get()
            snooze_enabled = self.snooze_enabled.get()
            snooze_duration = self.snooze_duration.get()
            repeat = self.repeat_var.get()
            
            # Validate inputs
            if not label.strip():
                messagebox.showerror("Error", "Please enter a label for the alarm")
                return
            
            # Create alarm object
            alarm = {
                'id': len(self.alarms),
                'time': f"{hour:02d}:{minute:02d}",
                'label': label,
                'sound': sound,
                'volume': volume,
                'snooze_enabled': snooze_enabled,
                'snooze_duration': snooze_duration,
                'repeat': repeat,
                'enabled': True,
                'snoozed': False,
                'snooze_until': None
            }
            
            self.alarms.append(alarm)
            self.update_alarms_display()
            self.save_settings()
            
            messagebox.showinfo("Success", f"Alarm set for {hour:02d}:{minute:02d}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid time values")
    
    def update_alarms_display(self):
        """Update the alarms listbox"""
        self.alarms_listbox.delete(0, tk.END)
        for alarm in self.alarms:
            status = "ON" if alarm['enabled'] else "OFF"
            snooze_info = f" (Snoozed)" if alarm['snoozed'] else ""
            display_text = f"{alarm['time']} - {alarm['label']} - {status}{snooze_info}"
            self.alarms_listbox.insert(tk.END, display_text)
    
    def edit_alarm(self):
        """Edit selected alarm"""
        selection = self.alarms_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an alarm to edit")
            return
        
        alarm_index = selection[0]
        alarm = self.alarms[alarm_index]
        
        # Pre-fill form with alarm data
        hour, minute = alarm['time'].split(':')
        self.hour_var.set(hour)
        self.minute_var.set(minute)
        self.label_var.set(alarm['label'])
        self.sound_var.set(alarm['sound'])
        self.volume_var.set(alarm['volume'])
        self.snooze_enabled.set(alarm['snooze_enabled'])
        self.snooze_duration.set(alarm['snooze_duration'])
        self.repeat_var.set(alarm['repeat'])
        
        # Remove old alarm and user can add updated one
        self.alarms.pop(alarm_index)
        self.update_alarms_display()
    
    def delete_alarm(self):
        """Delete selected alarm"""
        selection = self.alarms_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an alarm to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this alarm?"):
            alarm_index = selection[0]
            self.alarms.pop(alarm_index)
            self.update_alarms_display()
            self.save_settings()
    
    def toggle_alarm(self):
        """Enable/disable selected alarm"""
        selection = self.alarms_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an alarm to toggle")
            return
        
        alarm_index = selection[0]
        self.alarms[alarm_index]['enabled'] = not self.alarms[alarm_index]['enabled']
        self.update_alarms_display()
        self.save_settings()
    
    def test_sound(self):
        """Test the currently selected sound"""
        sound_file = None
        if self.sound_var.get() == "Custom Sound" and self.alarm_sounds['Custom Sound']:
            sound_file = self.alarm_sounds['Custom Sound']
        
        try:
            if sound_file and os.path.exists(sound_file):
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.set_volume(self.volume_var.get())
                pygame.mixer.music.play()
                messagebox.showinfo("Info", "Playing test sound... Click OK to stop.")
                pygame.mixer.music.stop()
            else:
                # Play system beep for default
                import winsound
                winsound.Beep(800, 1000)
        except Exception as e:
            messagebox.showerror("Error", f"Could not play sound: {str(e)}")
    
    def monitor_alarms(self):
        """Background thread to monitor alarms"""
        while True:
            current_time = datetime.datetime.now()
            current_time_str = current_time.strftime("%H:%M")
            current_day = current_time.weekday()  # 0=Monday, 6=Sunday
            
            for alarm in self.alarms[:]:  # Create a copy to avoid modification during iteration
                if not alarm['enabled']:
                    continue
                
                # Check if alarm is snoozed
                if alarm['snoozed'] and alarm['snooze_until']:
                    if current_time >= alarm['snooze_until']:
                        alarm['snoozed'] = False
                        alarm['snooze_until'] = None
                    else:
                        continue
                
                # Check if alarm should trigger
                if alarm['time'] == current_time_str:
                    # Check repeat settings
                    should_trigger = False
                    
                    if alarm['repeat'] == 'Once':
                        should_trigger = True
                    elif alarm['repeat'] == 'Daily':
                        should_trigger = True
                    elif alarm['repeat'] == 'Weekdays' and current_day < 5:  # Monday to Friday
                        should_trigger = True
                    elif alarm['repeat'] == 'Weekends' and current_day >= 5:  # Saturday and Sunday
                        should_trigger = True
                    
                    if should_trigger:
                        self.trigger_alarm(alarm)
                        
                        # If it's a "Once" alarm, disable it after triggering
                        if alarm['repeat'] == 'Once':
                            alarm['enabled'] = False
                            self.root.after(0, self.update_alarms_display)
            
            time.sleep(30)  # Check every 30 seconds
    
    def trigger_alarm(self, alarm):
        """Trigger the alarm"""
        self.current_playing_alarm = alarm
        
        # Play alarm sound
        self.play_alarm_sound(alarm)
        
        # Show alarm dialog
        self.root.after(0, lambda: self.show_alarm_dialog(alarm))
    
    def play_alarm_sound(self, alarm):
        """Play the alarm sound"""
        try:
            sound_file = None
            if alarm['sound'] == "Custom Sound" and self.alarm_sounds['Custom Sound']:
                sound_file = self.alarm_sounds['Custom Sound']
            
            if sound_file and os.path.exists(sound_file):
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.set_volume(alarm['volume'])
                pygame.mixer.music.play(-1)  # Loop indefinitely
            else:
                # Fallback to system beep in a loop
                def beep_loop():
                    import winsound
                    for _ in range(10):  # Beep 10 times
                        if self.current_playing_alarm != alarm:
                            break
                        winsound.Beep(800, 500)
                        time.sleep(0.5)
                
                beep_thread = threading.Thread(target=beep_loop, daemon=True)
                beep_thread.start()
                
        except Exception as e:
            print(f"Error playing alarm sound: {e}")
    
    def show_alarm_dialog(self, alarm):
        """Show alarm notification dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("ALARM!")
        dialog.geometry("400x300")
        dialog.configure(bg='#e74c3c')
        dialog.grab_set()  # Make it modal
        dialog.attributes('-topmost', True)
        
        # Alarm message
        msg_label = tk.Label(dialog, text=f"⏰ ALARM! ⏰\n\n{alarm['label']}\n\nTime: {alarm['time']}", 
                            font=('Arial', 16, 'bold'), 
                            fg='white', bg='#e74c3c')
        msg_label.pack(expand=True)
        
        # Button frame
        btn_frame = tk.Frame(dialog, bg='#e74c3c')
        btn_frame.pack(side='bottom', pady=20)
        
        # Dismiss button
        dismiss_btn = tk.Button(btn_frame, text="Dismiss", 
                               command=lambda: self.dismiss_alarm(dialog, alarm),
                               bg='#27ae60', fg='white', 
                               font=('Arial', 12, 'bold'),
                               width=10)
        dismiss_btn.pack(side='left', padx=10)
        
        # Snooze button (if enabled)
        if alarm['snooze_enabled']:
            snooze_btn = tk.Button(btn_frame, text=f"Snooze ({alarm['snooze_duration']}m)", 
                                  command=lambda: self.snooze_alarm(dialog, alarm),
                                  bg='#f39c12', fg='white', 
                                  font=('Arial', 12, 'bold'),
                                  width=15)
            snooze_btn.pack(side='left', padx=10)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.geometry("+{}+{}".format(
            int(self.root.winfo_x() + self.root.winfo_width()/2 - 200),
            int(self.root.winfo_y() + self.root.winfo_height()/2 - 150)
        ))
    
    def dismiss_alarm(self, dialog, alarm):
        """Dismiss the alarm"""
        pygame.mixer.music.stop()
        self.current_playing_alarm = None
        dialog.destroy()
        self.save_settings()
    
    def snooze_alarm(self, dialog, alarm):
        """Snooze the alarm"""
        pygame.mixer.music.stop()
        self.current_playing_alarm = None
        
        # Set snooze time
        snooze_until = datetime.datetime.now() + datetime.timedelta(minutes=alarm['snooze_duration'])
        alarm['snoozed'] = True
        alarm['snooze_until'] = snooze_until
        
        dialog.destroy()
        self.update_alarms_display()
        self.save_settings()
        
        messagebox.showinfo("Snoozed", 
                           f"Alarm snoozed for {alarm['snooze_duration']} minutes.\n"
                           f"Will ring again at {snooze_until.strftime('%H:%M')}")
    
    def save_settings(self):
        """Save alarm settings to file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            settings_data = []
            for alarm in self.alarms:
                alarm_copy = alarm.copy()
                if alarm_copy.get('snooze_until'):
                    alarm_copy['snooze_until'] = alarm_copy['snooze_until'].isoformat()
                settings_data.append(alarm_copy)
            
            with open(self.settings_file, 'w') as f:
                json.dump({
                    'alarms': settings_data,
                    'alarm_sounds': self.alarm_sounds
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        """Load alarm settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    
                self.alarms = data.get('alarms', [])
                saved_sounds = data.get('alarm_sounds', {})
                self.alarm_sounds.update(saved_sounds)
                
                # Convert string datetime back to datetime objects
                for alarm in self.alarms:
                    if alarm.get('snooze_until'):
                        alarm['snooze_until'] = datetime.datetime.fromisoformat(alarm['snooze_until'])
                
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.alarms = []

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = AlarmClock(root)
    app.update_alarms_display()  # Initial display update
    
    # Handle window close event
    def on_closing():
        app.save_settings()
        pygame.mixer.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

print("Advanced Alarm Clock application code has been created!")
print("\nFeatures included:")
print("✓ Multiple alarms with custom labels")
print("✓ Customizable alarm tones (including file browser)")
print("✓ Volume control for each alarm")
print("✓ Snooze functionality with configurable duration")
print("✓ Repeat options (Once, Daily, Weekdays, Weekends)")
print("✓ Enable/disable alarms without deletion")
print("✓ Settings persistence (saved to JSON file)")
print("✓ Modern GUI with dark theme")
print("✓ Background monitoring with threading")
print("✓ Sound testing capability")
print("✓ Modal alarm notifications")